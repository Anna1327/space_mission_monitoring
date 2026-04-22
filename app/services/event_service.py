from sqlalchemy.orm import Session
from typing import Optional

from ..models.event import Event
from ..schemas.event import EventCreate


class EventService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: EventCreate) -> Event:
        """Создать новое событие"""
        db_event = Event(
            system_id=data.system_id,
            event_type=data.event_type,
            payload=data.payload or {}
        )
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event

    def get_by_id(self, event_id: int) -> Optional[Event]:
        """Получить событие по ID"""
        return self.db.query(Event).filter(Event.id == event_id).first()

    def get_by_system(self, system_id: int, limit: int = 100, skip: int = 0):
        """Получить все события для конкретной системы"""
        return (
            self.db.query(Event)
            .filter(Event.system_id == system_id)
            .order_by(Event.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all(self, limit: int = 100, skip: int = 0):
        """Получить все события"""
        return (
            self.db.query(Event)
            .order_by(Event.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete_by_system(self, system_id: int):
        """Удалить все события системы. Возвращает количество удалённых."""
        deleted = self.db.query(Event).filter(Event.system_id == system_id).delete()
        self.db.commit()
        return deleted

    def delete_old(self, days: int = 30):
        """Удалить события старше N дней"""
        from datetime import datetime, timedelta, timezone
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        deleted = self.db.query(Event).filter(Event.created_at < cutoff).delete()
        self.db.commit()
        return deleted
