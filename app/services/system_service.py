from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete as sql_delete
from sqlalchemy import insert

from ..models.event import Event
from ..models.system import System
from ..schemas.system import SystemCreate


class SystemService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            sort_by: str = "id",
            order: str = "asc",
            status_filter=None
    ):
        """Асинхронное получение систем с динамической сортировкой, фильтрацией и пагинацией"""
        query = select(System)

        if status_filter:
            query = query.filter(System.status == status_filter)

        if order == "asc":
            query = query.order_by(getattr(System, sort_by).asc())
        else:
            query = query.order_by(getattr(System, sort_by).desc())

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, system_id: int):
        """Асинхронный поиск космической системы по её ID"""
        query = select(System).filter(System.id == system_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(self, data: SystemCreate):
        """Асинхронное создание новой системы космического корабля"""
        db_system = System(
            name=data.name,
            system_type=data.system_type
        )
        self.db.add(db_system)
        await self.db.commit()
        await self.db.refresh(db_system)
        return db_system

    async def delete(self, system_id: int):
        """Асинхронное удаление системы из реестра"""
        system = await self.get_by_id(system_id)
        if system:
            delete_events_query = sql_delete(Event).where(Event.system_id == system_id)
            await self.db.execute(delete_events_query)

            query = sql_delete(System).where(System.id == system_id)
            await self.db.execute(query)

            await self.db.commit()
            return system
        return None

    async def update_status(self, system_id: int, status: str):
        """Асинхронное обновление статуса системы (stable / warning / failure)"""
        system = await self.get_by_id(system_id)
        if system:
            system.status = status
            await self.db.commit()
            await self.db.refresh(system)
        return system

    async def add_event(self, system_id: int, event_data: dict):
        """Асинхронное добавление ивента в историю логов системы"""
        system = await self.get_by_id(system_id)
        if system:
            events = list(system.events or [])
            events.append(event_data)
            system.events = events

            event_insert_query = insert(Event).values(
                system_id=system_id,
                event_type=event_data["event"],
                payload=event_data
            )
            await self.db.execute(event_insert_query)
            await self.db.commit()
            await self.db.refresh(system)
        return system
