import os

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from dotenv import load_dotenv

from app.models.assistant import Assistant
from app.services.rag import search_vector_store


load_dotenv()

chat_histories = {}

chat_model = ChatOpenAI(model_name="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

BASE_PHONE_SYSTEM_PROMPT = "<instructions> Talk in humanly manner and expressions.\
                    Give direct answers to user as if you are on a phone call and an actual person is talking.\
                    Keep your answers short and precise. Use provided <context> to answer user questions if context is provided.</instructions>"


def get_chat_history(session_id: str, user_system_prompt: str = ""):
    if session_id not in chat_histories:
        chat_histories[session_id] = ChatMessageHistory(
            messages=[
                SystemMessage(
                    content=f"{BASE_PHONE_SYSTEM_PROMPT}\n   <important_instructions>{user_system_prompt}</important_instructions>"
                )
            ]
        )
    return chat_histories[session_id]


def get_response(assistant: Assistant, session_id: str, user_input: str):
    history = get_chat_history(session_id, assistant.system_instructions)
    try:
        context = search_vector_store(str(assistant.id), user_input)
    except Exception:
        context = ""

    retriever_message = f"<context>{context}</context>\n{user_input}"
    history.add_user_message(retriever_message)
    messages = history.messages
    response = chat_model.invoke(messages)
    history.add_ai_message(response.content)
    return response.content
