from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from dotenv import load_dotenv
import os

load_dotenv()

chat_histories = {}

chat_model = ChatOpenAI(model_name="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))


def get_chat_history(session_id: str):
    if session_id not in chat_histories:
        chat_histories[session_id] = ChatMessageHistory(
            messages=[
                SystemMessage(
                    content="Talk in humanly manner and expressions.\
                    Give direct answers to user as if you are on a phone call and an actual person is talking.\
                    Keep your answers short and precise."
                )
            ]
        )
    return chat_histories[session_id]


def get_response(session_id: str, user_input: str):
    history = get_chat_history(session_id)

    history.add_user_message(user_input)
    messages = history.messages
    response = chat_model.invoke(messages)
    history.add_ai_message(response.content)

    return response.content
