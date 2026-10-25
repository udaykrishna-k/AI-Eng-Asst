import uuid
import sqlite3
from pathlib import Path
import logging

import streamlit as st
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.store.sqlite import SqliteStore
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import InMemorySaver

from tools.preferences import save_preference, get_preference
from utils import constants
from utils.logging_config import setup_logger
from utils.stream import stream_answer


# Configure console logging before creating the agent.
setup_logger()
log = logging.getLogger(constants.APP_NAME)


st.set_page_config(
    page_title="AI Engineering Assistant",
    page_icon="🤖",
)

st.title("AI Engineering Assistant")
st.caption("Built with LangChain and Streamlit")


@st.cache_resource
def get_agent():
    log.info("Initializing AI Engineering Assistant agent")

    conn = None

    try:
        log.debug("Initializing chat model")

        model = init_chat_model(
            model=constants.GPT_4_MINI,
            temperature=0,
            api_key=constants.OPENAI_API_KEY,
        )

        log.debug("Chat model initialized successfully")

        db_path = Path(__file__).parent / "assistant_memory.sqlite"
        log.debug("Initializing SQLite preference store")

        conn = sqlite3.connect(
            str(db_path),
            check_same_thread=False,
            isolation_level=None,
        )

        log.debug("Initializing in-memory checkpointer")
        checkpointer = SqliteSaver(conn)
        checkpointer.setup()

        store = SqliteStore(conn)
        store.setup()

        log.info("SQLite preference store initialized successfully")

        agent = create_agent(
            model=model,
            tools=[save_preference, get_preference],
            system_prompt=constants.SYSTEM_PROMPT,
            checkpointer=checkpointer,
            store=store,
        )

        log.info("AI Engineering Assistant agent initialized successfully")
        return agent

    except Exception:
        log.exception("Failed to initialize AI Engineering Assistant agent")
        raise


try:
    agent = get_agent()
except Exception:
    st.error("The assistant could not be initialized. Please check the application logs.")
    st.stop()


# Initialize Streamlit session state.
if "messages" not in st.session_state:
    st.session_state["messages"] = []
    log.debug("Initialized chat message history")

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = str(uuid.uuid4())
    log.debug("Created a new conversation thread")


# Start a fresh conversation when requested.
if st.button("➕ New chat"):
    st.session_state["messages"] = []
    st.session_state["thread_id"] = str(uuid.uuid4())

    log.info("Started a new conversation thread")

    st.rerun()


# Display existing conversation history.
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Process a new user message.
if user_input := st.chat_input("Ask me anything..."):
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state["messages"].append(
        {"role": "user", "content": user_input}
    )

    thread_id = st.session_state["thread_id"]

    log.info("Received a new user request")
    log.debug(
        "Request metadata: thread_id=%s, input_length=%d",
        thread_id,
        len(user_input),
    )

    try:
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        log.debug("Starting agent response stream")

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = st.write_stream(
                    stream_answer(agent, user_input, config)
                )

        st.session_state["messages"].append(
            {"role": "assistant", "content": answer}
        )

        log.info("Agent request completed successfully")

    except Exception:
        log.exception(
            "Failed to process agent request for thread_id=%s",
            thread_id,
        )

        st.error(
            "Sorry, something went wrong while processing your request. "
            "Please try again."
        )
