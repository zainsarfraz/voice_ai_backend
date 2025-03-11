from app.api.deps import SessionDep
from app.models.assistant import Assistant
from app.schemas.assistant import AssistantCreate
from app.models.user import User


def create_assistant_service(
    session: SessionDep, assistant_create: AssistantCreate, current_user: User
):
    assistant_data = assistant_create.model_dump()
    assistant = Assistant()
    assistant.name = assistant_data["name"]
    assistant.system_instructions = assistant_data["system_instructions"]
    assistant.first_message = assistant_data["first_message"]
    assistant.voice = assistant_data["voice"]
    assistant.user = current_user

    session.add(assistant)
    session.commit()
    session.refresh(assistant)

    return assistant


def get_all_assistants_service(session: SessionDep, current_user: User):
    assistants = (
        session.query(Assistant).filter(Assistant.user_id == current_user.id).all()
    )
    return assistants


def get_assistant_by_id_service(
    session: SessionDep, current_user: User, assistant_id: str
):
    assistant = (
        session.query(Assistant)
        .filter(Assistant.id == assistant_id, Assistant.user_id == current_user.id)
        .first()
    )
    return assistant
