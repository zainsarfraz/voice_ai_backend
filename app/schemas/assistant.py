import uuid
from enum import Enum
from pydantic import BaseModel, ConfigDict


class VoiceType(str, Enum):
    male = "male"
    female = "female"


class AssistantBase(BaseModel):
    name: str
    system_instruction: str
    vector_store_collection_name: str
    first_message: str
    voice: VoiceType


class AssistantCreate(BaseModel):
    name: str
    system_instructions: str
    first_message: str
    voice: VoiceType


class AssistantID(BaseModel):
    id: uuid.UUID


class AssistantPublic(AssistantBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
