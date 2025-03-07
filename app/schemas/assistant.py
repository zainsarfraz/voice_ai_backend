import uuid

from pydantic import BaseModel, ConfigDict


class AssistantBase(BaseModel):
    name: str
    system_instruction: str
    vector_store_collection_name: str
    
    
class AssistantCreate(BaseModel):
    name: str
    system_instruction: str
    

class AssistantPublic(AssistantBase):
    id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)