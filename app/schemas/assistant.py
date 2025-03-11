import uuid
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict


class VoiceType(str, Enum):
    male = "male"
    female = "female"


class AssistantBase(BaseModel):
    name: str | None = "Assistant"
    system_instructions: str | None = ""
    first_message: str | None = ""
    voice: Optional[VoiceType] = None


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
