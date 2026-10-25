import os
from langchain.chat_models import init_chat_model

MODEL = "gpt-4o-mini"
model = init_chat_model(model=MODEL,
                        api_key=os.environ.get("OPENAI_API_KEY"),
                        temperature=0)

response = model.invoke("Hi How are you!!")
print(response.content)