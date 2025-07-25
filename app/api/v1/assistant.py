from typing import List

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException,
    status,
    Response,
)

from app.api.deps import get_current_user, SessionDep
from app.models.user import User
from app.schemas.assistant import (
    AssistantCreate,
    AssistantID,
    AssistantPublic,
    AssistantUpdate,
)
from app.crud.assistant import (
    create_assistant_service,
    get_all_assistants_service,
    get_assistant_by_id_service,
    delete_assistant_by_id_service,
    update_assistant_service,
)
from app.services.rag import add_doc_to_vector_store, files_in_collection
from app.core.logger import logger


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


@routes.get("", description="Get All Assistants", response_model=List[AssistantPublic])
async def get_all_assistants(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all assistants for the current user.
    """
    assistants = get_all_assistants_service(session=session, current_user=current_user)
    return assistants


@routes.get(
    "/{assistant_id}",
    description="Get a Single Assistant",
    response_model=AssistantPublic,
)
async def get_assistant(
    assistant_id: str,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a single assistant by its ID for the current user.
    """
    assistant = get_assistant_by_id_service(
        session=session, current_user=current_user, assistant_id=assistant_id
    )

    return assistant


@routes.put(
    "/{assistant_id}", description="Edit an Assistant", response_model=AssistantPublic
)
async def edit_assistant(
    assistant_id: str,
    assistant_update: AssistantUpdate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """
    Update an assistant's details.
    """
    assistant = update_assistant_service(
        session=session,
        current_user=current_user,
        assistant_id=assistant_id,
        assistant_update=assistant_update,
    )
    return assistant


@routes.delete(
    "/{assistant_id}",
    description="Delete an Assistant",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_assistant(
    assistant_id: str,
    session: SessionDep,
    current_user=Depends(get_current_user),
):
    """
    Delete a single assistant by its ID for the current user.
    Also deletes associated data from ChromaDB.
    """
    delete_assistant_by_id_service(
        session=session, current_user=current_user, assistant_id=assistant_id
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@routes.get(
    "/{assistant_id}/knowledge_base",
    description="Get Vector store file names of assistant",
    response_model=List[str],
)
async def get_assistant_knowledgebase(assistant_id: str):
    """
    Retrieve vector store file names of assistant
    """
    files = files_in_collection(str(assistant_id))

    return files


@routes.post(
    "/{assistant_id}/upload_document",
    description="Upload pdf files in assistant knowledge base",
    response_model=str,
)
async def upload_document(
    session: SessionDep,
    assistant_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Uploads a document via FormData and add it to vector store
    """

    assistant = get_assistant_by_id_service(
        session=session, current_user=current_user, assistant_id=assistant_id
    )

    try:
        await add_doc_to_vector_store(file, str(assistant.id))
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Failed to upload document to vector store",
        )

    return "Document added to vector store."
