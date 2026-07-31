from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.client import Client
from ..schemas.client import ClientCreate
from ..core.security import get_password_hash


class ClientService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: ClientCreate):
        """Асинхронное создание нового клиента космической миссии"""
        client = Client(
            client_id=data.client_id,
            client_secret_hash=get_password_hash(data.client_secret),
            name=data.name
        )
        async with self.db.begin_nested():
            self.db.add(client)

        await self.db.commit()
        await self.db.refresh(client)
        return client

    async def get_by_client_id(self, client_id: str):
        """Асинхронный поиск клиента по его уникальному идентификатору"""
        query = select(Client).filter(Client.client_id == client_id)
        result = await self.db.execute(query)
        return result.scalars().first()
