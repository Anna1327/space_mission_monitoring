from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...services.system_service import SystemService
from ...schemas.system import SystemCreate, SystemResponse
from ...api.deps import get_current_client

router = APIRouter(prefix="/systems", tags=["systems"])


@router.get("/", response_model=List[SystemResponse])
def get_systems(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        _=Depends(get_current_client)
):
    service = SystemService(db)
    return service.get_all(skip=skip, limit=limit)


@router.get("/{system_id}", response_model=SystemResponse)
def get_system(
        system_id: int,
        db: Session = Depends(get_db),
        _=Depends(get_current_client)
):
    service = SystemService(db)
    system = service.get_by_id(system_id)
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    return system


@router.post("/", response_model=SystemResponse)
def create_system(
        data: SystemCreate,
        db: Session = Depends(get_db),
        _=Depends(get_current_client)
):
    service = SystemService(db)
    return service.create(data)


@router.post("/{system_id}/trigger/{event_type}")
def trigger_event(
        system_id: int,
        event_type: str,
        db: Session = Depends(get_db),
        _=Depends(get_current_client)
):
    service = SystemService(db)
    system = service.get_by_id(system_id)
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    if event_type == "failure":
        system = service.update_status(system_id, "failed")
    elif event_type == "warning":
        system = service.update_status(system_id, "warning")
    elif event_type == "recover":
        system = service.update_status(system_id, "active")
    else:
        raise HTTPException(status_code=400, detail="Invalid event type")

    event_data = {
        "system_id": system_id,
        "event": f"system_{event_type}",
        "system_name": system.name,
        "system_type": system.system_type
    }
    service.add_event(system_id, event_data)

    # TODO: broadcast via WebSocket
    return {"status": "triggered", "event": event_data}
