from pydantic import BaseModel
from datetime import datetime


class ClientCreate(BaseModel):
    client_id: str
    client_secret: str
    name: str


class ClientResponse(BaseModel):
    id: int
    client_id: str
    name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
