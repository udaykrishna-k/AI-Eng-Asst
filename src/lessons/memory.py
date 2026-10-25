from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from utils import constants

model = init_chat_model(model=constants.GPT_4_MINI,
                        temperature=0,
                        api_key=constants.OPENAI_API_KEY)

checkpointer = InMemorySaver()
agent = create_agent(model=model,
                     system_prompt=constants.SYSTEM_PROMPT,
                     checkpointer=checkpointer)

config = {"configurable": {"thread_id": "memory_lesson"}}

messages = [HumanMessage(content="My favorite programming language is Python")]

response = agent.invoke({"messages": messages}, config=config)
print(response["messages"][-1].content)

messages = [HumanMessage(content="What is my favorite programming language")]
response = agent.invoke({"messages": messages}, config=config)
print(response["messages"][-1].content)