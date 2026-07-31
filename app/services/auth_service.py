from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta
from ..models.client import Client
from ..core.security import verify_password, create_access_token, decode_access_token
from ..core.config import settings


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate_client(self, client_id: str, client_secret: str):
        """Асинхронная аутентификация клиента через SQLAlchemy 2.0"""
        print(f"\n[AUTH DEBUG] Ищем client_id: {client_id}")
        query = select(Client).where(
            Client.client_id == client_id,
            Client.is_active
        )

        result = await self.db.execute(query)
        client = result.scalars().first()

        if not client:
            return None

        is_password_correct = verify_password(client_secret, client.client_secret_hash)
        if not is_password_correct:
            return None

        return client

    def create_token(self, client: Client):
        """Синхронный метод генерации JWT-токена в памяти"""
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": client.client_id},
            expires_delta=expires_delta
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    async def get_client_from_token(self, token: str):
        """Асинентное извлечение и валидация клиента из JWT-токена"""
        payload = decode_access_token(token)
        if not payload:
            return None

        client_id = payload.get("sub")
        if not client_id:
            return None

        query = select(Client).where(
            Client.client_id == client_id,
            Client.is_active
        )
        result = await self.db.execute(query)
        return result.scalars().first()
