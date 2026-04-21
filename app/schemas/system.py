from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any


class SystemBase(BaseModel):
    name: str
    system_type: str


class SystemCreate(SystemBase):
    pass


class SystemUpdate(BaseModel):
    status: Optional[str] = None


class SystemResponse(SystemBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    events: List[Any] = []

    class Config:
        from_attributes = True
