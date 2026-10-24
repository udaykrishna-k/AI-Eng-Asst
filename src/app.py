from pydantic_models.concept_explaination import ConceptExplaination
from utils import constants
import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

st.set_page_config(
    page_title="AI Engineering Assistant",
    page_icon="🤖",
)
st.title("AI Engineering Assistant")
st.caption("Built with LangChain and Streamlit")

@st.cache_resource
def get_model():
    return init_chat_model(model=constants.GPT_4_MINI,
                        temperature=0,
                        api_key=constants.OPENAI_API_KEY)

model = get_model()
structured_model = model.with_structured_output(ConceptExplaination)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", constants.SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}")
])


chain = prompt_template | structured_model

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Ask me anything..."):
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state["messages"].append({"role": "user", "content": user_input})

    conversation = [SystemMessage(content=constants.SYSTEM_PROMPT)]

    for message in st.session_state["messages"]:
        if message["role"] == "assistant":
            conversation.append(AIMessage(content=message["content"]))
        elif message["role"] == "user":
            conversation.append(HumanMessage(content=message["content"]))

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):

                result = chain.invoke({"history": conversation,
                                         "input": user_input})

            st.subheader(result.concept)
            st.write(result.explanation)

            st.caption(f"Difficulty: {result.difficulty}")

            st.write("Related topics:")
            for topic in result.related_topics:
                st.write(f"- {topic}")

        st.session_state["messages"].append({"role": "assistant", "content": result})

    except Exception as e:
        st.error(f"Something went wrong: {e}")
