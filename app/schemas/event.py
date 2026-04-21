from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class EventCreate(BaseModel):
    system_id: int
    event_type: str
    payload: Optional[Any] = None


class EventResponse(BaseModel):
    id: int
    system_id: int
    event_type: str
    payload: Any
    created_at: datetime

    class Config:
        from_attributes = True
