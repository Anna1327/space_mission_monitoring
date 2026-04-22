from sqlalchemy.orm import Session
from ..models.system import System
from ..schemas.system import SystemCreate


class SystemService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            sort_by: str = "id",
            order: str = "asc",
            status_filter=None
    ):
        query = self.db.query(System)

        # Фильтр по статусу
        if status_filter:
            query = query.filter(System.status == status_filter)

        # Сортировка
        if order == "asc":
            query = query.order_by(getattr(System, sort_by).asc())
        else:
            query = query.order_by(getattr(System, sort_by).desc())

        # Пагинация
        return query.offset(skip).limit(limit).all()

    def get_by_id(self, system_id: int):
        return self.db.query(System).filter(System.id == system_id).first()

    def create(self, data: SystemCreate):
        db_system = System(
            name=data.name,
            system_type=data.system_type
        )
        self.db.add(db_system)
        self.db.commit()
        self.db.refresh(db_system)
        return db_system

    def update_status(self, system_id: int, status: str):
        system = self.get_by_id(system_id)
        if system:
            system.status = status
            self.db.commit()
            self.db.refresh(system)
        return system

    def add_event(self, system_id: int, event_data: dict):
        system = self.get_by_id(system_id)
        if system:
            events = system.events or []
            events.append(event_data)
            system.events = events
            self.db.commit()
            self.db.refresh(system)
        return system
