from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.engine import CursorResult
from sqlalchemy import delete as sql_delete
from typing import Optional, cast
from datetime import datetime, timedelta, timezone

from ..models.event import Event
from ..schemas.event import EventCreate


class EventService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: EventCreate) -> Event:
        """Создать новое событие (асинхронно)"""
        db_event = Event(
            system_id=data.system_id,
            event_type=data.event_type,
            payload=data.payload or {}
        )
        self.db.add(db_event)
        await self.db.commit()
        await self.db.refresh(db_event)
        return db_event

    async def get_by_id(self, event_id: int) -> Optional[Event]:
        """Получить событие по ID (асинхронно)"""
        query = select(Event).filter(Event.id == event_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_system(self, system_id: int, limit: int = 100, skip: int = 0):
        """Получить все события для конкретной системы (асинхронно)"""
        query = (
            select(Event)
            .filter(Event.system_id == system_id)
            .order_by(Event.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_all(self, limit: int = 100, skip: int = 0):
        """Получить все события (асинхронно)"""
        query = (
            select(Event)
            .order_by(Event.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def delete_by_system(self, system_id: int) -> int:
        """Удалить все события системы. Возвращает количество удалённых."""
        query = sql_delete(Event).where(Event.system_id == system_id)

        result = cast(CursorResult, await self.db.execute(query))
        await self.db.commit()

        return result.rowcount if result.rowcount is not None else 0

    async def delete_old(self, days: int = 30) -> int:
        """Удалить события старше N дней"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        query = sql_delete(Event).where(Event.created_at < cutoff)

        result = cast(CursorResult, await self.db.execute(query))
        await self.db.commit()

        return result.rowcount if result.rowcount is not None else 0

