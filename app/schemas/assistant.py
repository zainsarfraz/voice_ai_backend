import uuid

from pydantic import BaseModel, ConfigDict


class AssistantBase(BaseModel):
    name: str
    system_instruction: str
    vector_store_collection_name: str
    first_message: str


class AssistantCreate(BaseModel):
    name: str
    system_instructions: str
    first_message: str


class AssistantID(BaseModel):
    id: uuid.UUID


class AssistantPublic(AssistantBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
