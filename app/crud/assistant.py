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
    assistant.user = current_user

    session.add(assistant)
    session.commit()
    session.refresh(assistant)

    return assistant
