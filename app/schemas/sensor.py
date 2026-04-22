from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SensorBase(BaseModel):
    name: str
    unit: str = "celsius"
    min_normal: float
    max_normal: float


class SensorCreate(SensorBase):
    pass


class SensorUpdate(BaseModel):
    value: float


class SensorResponse(SensorBase):
    id: int
    system_id: int
    value: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
