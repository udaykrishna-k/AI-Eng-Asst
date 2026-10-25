from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool

from utils import constants

@tool
def add(a: int, b: int) -> int:
    """Adds two numbers together and returns the result."""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """Multiplies two numbers together and returns the result."""
    return a * b

model = init_chat_model(model=constants.GPT_4_MINI,
                        temperature=0,
                        api_key=constants.OPENAI_API_KEY)

agent = create_agent(model=model,
                     tools=[add, multiply],
                     system_prompt=(
                        "You are an AI Engineering Assistant. "
                        "Explain technical concepts clearly. "
                        "Use the available calculator tools for arithmetic "
                        "when appropriate, and explain the result."
                        )
                     )


response = agent.invoke({"messages": [{
                        "role": "user",
                        "content": "What is (10 * 10) + 10"
                    }]})
final_message = response["messages"][-1]
print(final_message.content)