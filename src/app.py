from pathlib import Path
import logging

import streamlit as st
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.store.sqlite import SqliteStore
from langgraph.checkpoint.sqlite import SqliteSaver

from tools.preferences import save_preference, get_preference
from utils import constants
from utils.conversation_history import load_thread_messages
from utils.logging_config import setup_logger
from utils.stream import stream_answer
from utils.chat_registry import initialize_chat_registry, get_connection, get_all_chats, create_chat, update_chat

# Configure console logging before creating the agent.
setup_logger()
log = logging.getLogger(constants.APP_NAME)
initialize_chat_registry()

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

        checkpoint_conn = get_connection()

        store_conn = get_connection()

        checkpointer = SqliteSaver(checkpoint_conn)
        checkpointer.setup()

        store = SqliteStore(store_conn)
        store.setup()

        log.info("SQLite checkpointer and preference store initialized")

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

chats = get_all_chats()

if "thread_id" not in st.session_state:
    if chats:
        log.debug("Using the latest conversation thread")
        st.session_state["thread_id"] = chats[0]["chat_id"]
    else:
        log.debug("Created a new conversation thread")
        st.session_state["thread_id"] = create_chat()

# Sidebar: create and switch conversations.
with st.sidebar:
    st.title("Chat history")

    if st.button("➕ New chat", use_container_width=True):
        st.session_state["thread_id"] = create_chat()
        log.info("Switched to a new conversation")
        st.rerun()

    st.divider()

    chats = get_all_chats()

    for chat in chats:
        title, chat_id = chat["title"], chat["chat_id"]
        if st.button(
            f"💬 {title}",
            key=f"chat_{chat_id}",
            use_container_width=True,
        ):
            if chat_id != st.session_state["thread_id"]:
                st.session_state["thread_id"] = chat_id
                log.info("Switched conversation")
                log.debug("Active thread_id=%s", chat_id)
                st.rerun()

thread_id = st.session_state["thread_id"]
messages = load_thread_messages(agent, thread_id)

# Display existing conversation history.
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process a new user message.
if user_input := st.chat_input("Ask me anything..."):
    with st.chat_message("user"):
        st.markdown(user_input)

    update_chat(thread_id, str(user_input))

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
