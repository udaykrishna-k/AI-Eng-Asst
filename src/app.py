import uuid

from langchain.agents import create_agent
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import InMemorySaver

from tools.preferences import save_preference, get_preference
from utils import constants
import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

st.set_page_config(
    page_title="AI Engineering Assistant",
    page_icon="🤖",
)
st.title("AI Engineering Assistant")
st.caption("Built with LangChain and Streamlit")

@st.cache_resource
def get_agent():
    model = init_chat_model(model=constants.GPT_4_MINI,
                        temperature=0,
                        api_key=constants.OPENAI_API_KEY)

    checkpointer = InMemorySaver()
    store = InMemoryStore()
    return create_agent(model=model,
                        tools=[save_preference, get_preference],
                        system_prompt=constants.SYSTEM_PROMPT,
                        checkpointer=checkpointer,
                        store=store)

agent = get_agent()

prompt_template = ChatPromptTemplate.from_messages([
    ("system", constants.SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}")
])


if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = str(uuid.uuid4())

# Start a fresh conversation when requested.
if st.button("➕ New chat"):
    st.session_state["messages"] = []
    st.session_state["thread_id"] = str(uuid.uuid4())
    st.rerun()

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Ask me anything..."):
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state["messages"].append({"role": "user", "content": user_input})

    # conversation = []
    # for message in st.session_state["messages"]:
    #     if message["role"] == "assistant":
    #         conversation.append(AIMessage(content=message["content"]))
    #     elif message["role"] == "user":
    #         conversation.append(HumanMessage(content=message["content"]))

    try:
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = agent.invoke({"messages": [HumanMessage(content=user_input)]},
                                        config=config)
            answer = response["messages"][-1].content
            st.markdown(answer)

        st.session_state["messages"].append({"role": "assistant", "content": answer})

    except Exception as e:
        st.error(f"Something went wrong: {e}")
