from langchain.chat_models import init_chat_model
from langchain.tools import tool

from utils import constants


# 1. Define a Python function and expose it as a LangChain tool.
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers and return the product."""
    return a * b


# 2. Initialize the model.
model = init_chat_model(
    constants.GPT_4_MINI,
    temperature=0,
    api_key=constants.OPENAI_API_KEY
)

# 3. Make the tool available to the model.
model_with_tools = model.bind_tools([multiply])


# 4. Ask a question that may require the tool.
response = model_with_tools.invoke(
    "What is 125 multiplied by 48? Use the multiply tool."
)


# 5. Inspect the model's tool request.
print(response.tool_calls)

# 6. Create a lookup table for the tools we allow.
tools_by_name = {
    "multiply": multiply,
}

# 7. Execute each tool requested by the model.
for tool_call in response.tool_calls:
    selected_tool = tools_by_name[tool_call["name"]]

    tool_result = selected_tool.invoke(tool_call["args"])

    print("Tool result:", tool_result)