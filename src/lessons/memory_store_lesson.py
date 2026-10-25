from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.store.memory import InMemoryStore

from utils import constants

model = init_chat_model(model=constants.GPT_4_MINI,
                        temperature=0,
                        api_key=constants.OPENAI_API_KEY)

store = InMemoryStore()
user_id = "user_001"
namespace = ("users", user_id, "preferences")

store.put(namespace,
          "learning_style",
          {"value": "Prefer Python examples when learning DSA"})

memory = store.get(namespace, "learning_style")

if memory:
    preference = memory.value["value"]
else:
    preference = "No saved preferences"

system_message = SystemMessage(
    content=(
        "You are an AI Engineering Assistant. "
        f"The user's saved preference is: {preference} "
        "Use this preference when relevant."
    )
)

# 9. Ask the model a question in the new conversation.
human_message = HumanMessage(
    content="Explain binary search."
)

response = model.invoke([system_message, human_message])

print(response.content)
