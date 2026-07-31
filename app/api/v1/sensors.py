from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...core.database import get_db
from ...services.sensor_service import SensorService
from ...schemas.sensor import SensorCreate, SensorUpdate, SensorResponse
from ...api.deps import get_current_client
from ...services.system_service import SystemService
from ...utils.websocket_manager import ws_manager


router = APIRouter(prefix="/systems/{system_id}/sensors", tags=["sensors"])


@router.get("/", response_model=List[SensorResponse])
async def get_sensors(
        system_id: int,
        db: AsyncSession = Depends(get_db),
        _=Depends(get_current_client)
):
    """Получить все датчики системы (асинхронно)"""
    system = await SystemService(db).get_by_id(system_id)
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    return await SensorService(db).get_by_system(system_id)


@router.post("/", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
async def create_sensor(
        system_id: int,
        data: SensorCreate,
        db: AsyncSession = Depends(get_db),
        _=Depends(get_current_client)
):
    """Создать датчик для системы (асинхронно)"""
    system = await SystemService(db).get_by_id(system_id)
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    return await SensorService(db).create(system_id, data)


@router.patch("/{sensor_id}/value")
async def update_sensor_value(
        system_id: int,
        sensor_id: int,
        data: SensorUpdate,
        db: AsyncSession = Depends(get_db),
        _=Depends(get_current_client)
):
    """
    Обновить показания датчика (асинхронно).
    При выходе за границы min/max генерируется warning.
    При возвращении в норму — recover.
    """
    system = await SystemService(db).get_by_id(system_id)
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    result = await SensorService(db).update_value(sensor_id, data.value)
    if not result:
        raise HTTPException(status_code=404, detail="Sensor not found")

    sensor, old_status, new_status = result

    if old_status != new_status:
        event_type = "warning" if new_status == "abnormal" else "recover"

        system_service = SystemService(db)
        db_status = "warning" if event_type == "warning" else "active"
        await system_service.update_status(system_id, db_status)

        event_data = {
            "system_id": system_id,
            "event": f"system_{event_type}",
            "system_name": system.name,
            "system_type": system.system_type,
            "old_status": "active" if event_type == "warning" else "warning",
            "new_status": "warning" if event_type == "warning" else "active"
        }

        await system_service.add_event(system_id, event_data)
        await ws_manager.broadcast_to_system(system_id, event_data)

    return {"sensor_id": sensor_id, "value": data.value, "status": new_status}
