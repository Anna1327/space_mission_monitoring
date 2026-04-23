from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...services.sensor_service import SensorService
from ...services.system_service import SystemService
from ...schemas.sensor import SensorCreate, SensorUpdate, SensorResponse
from ...api.deps import get_current_client

router = APIRouter(prefix="/systems/{system_id}/sensors", tags=["sensors"])


@router.get("/", response_model=List[SensorResponse])
def get_sensors(
        system_id: int,
        db: Session = Depends(get_db),
        _=Depends(get_current_client)
):
    """Получить все датчики системы"""
    system = SystemService(db).get_by_id(system_id)
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    return SensorService(db).get_by_system(system_id)


@router.post("/", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
def create_sensor(
        system_id: int,
        data: SensorCreate,
        db: Session = Depends(get_db),
        _=Depends(get_current_client)
):
    """Создать датчик для системы"""
    system = SystemService(db).get_by_id(system_id)
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    return SensorService(db).create(system_id, data)


@router.patch("/{sensor_id}/value")
async def update_sensor_value(
        system_id: int,
        sensor_id: int,
        data: SensorUpdate,
        db: Session = Depends(get_db),
        _=Depends(get_current_client)
):
    """
    Обновить показания датчика.
    При выходе за границы min/max генерируется warning.
    При возвращении в норму — recover.
    """
    system = SystemService(db).get_by_id(system_id)
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    sensor, old_status, new_status = SensorService(db).update_value(sensor_id, data.value)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    # Если статус изменился, триггерим событие
    if old_status != new_status:
        from .systems import trigger_event
        event_type = "warning" if new_status == "abnormal" else "recover"
        await trigger_event(system_id, event_type, db)

    return {"sensor_id": sensor_id, "value": data.value, "status": new_status}
