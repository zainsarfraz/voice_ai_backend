import uuid
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class VoiceType(str, Enum):
    male = "male"
    female = "female"


class AssistantBase(BaseModel):
    name: Optional[str] = ""
    system_instructions: Optional[str] = ""
    first_message: Optional[str] = ""
    voice: Optional[VoiceType] = None


class AssistantCreate(BaseModel):
    name: str
    system_instructions: str
    first_message: str
    voice: VoiceType


class AssistantUpdate(BaseModel):
    name: Optional[str] = None
    system_instructions: Optional[str] = None
    first_message: Optional[str] = None
    voice: Optional[VoiceType] = None

    
class AssistantID(BaseModel):
    id: uuid.UUID


class AssistantPublic(AssistantBase):
    id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)
