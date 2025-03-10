from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, SessionDep
from app.models.user import User
from app.schemas.assistant import AssistantCreate, AssistantID
from app.crud.assistant import create_assistant_service

routes = APIRouter(prefix="/assistant", tags=["Assistant"])


@routes.post("", description="Create Assistant", response_model=AssistantID)
async def create_assistant(
    assistant: AssistantCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """
    Create new user assistant based on the settings
    """
    assistant = create_assistant_service(
        assistant_create=assistant, session=session, current_user=current_user
    )
    return assistant
