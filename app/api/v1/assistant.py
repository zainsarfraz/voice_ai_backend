from fastapi import APIRouter, status, Depends, HTTPException

from app.api.deps import get_current_user, SessionDep
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UpdateMe, UserPublic, UpdatePassword
from app.schemas.assistant import AssistantCreate

routes = APIRouter(prefix="/assistant", tags=["Assistant"])


@routes.post("", description="Create Assistant", response_model=AssistantCreate)
async def create_assistant(assistant: AssistantCreate, current_user: User = Depends(get_current_user)):
    """
    Create new user assistant based on the settings
    """
    
    return assistant

