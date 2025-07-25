from fastapi import HTTPException, status

from app.api.deps import SessionDep
from app.models.assistant import Assistant
from app.schemas.assistant import AssistantCreate, AssistantUpdate
from app.models.user import User


def create_assistant_service(
    session: SessionDep, assistant_create: AssistantCreate, current_user: User
):
    assistant_data = assistant_create.model_dump()
    assistant = Assistant()
    for key, value in assistant_data.items():
        setattr(assistant, key, value)

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
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assistant not found",
        )
    return assistant


def delete_assistant_by_id_service(
    session: SessionDep, current_user: User, assistant_id: str
):
    assistant = get_assistant_by_id_service(session, current_user, assistant_id)
    session.delete(assistant)
    session.commit()


def update_assistant_service(
    session: SessionDep,
    current_user: User,
    assistant_id: str,
    assistant_update: AssistantUpdate,
):
    assistant = get_assistant_by_id_service(session, current_user, assistant_id)
    assistant_data = assistant_update.model_dump(exclude_unset=True)
    for key, value in assistant_data.items():
        setattr(assistant, key, value)

    session.commit()
    session.refresh(assistant)

    return assistant
