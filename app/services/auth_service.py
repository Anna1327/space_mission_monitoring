from sqlalchemy.orm import Session
from datetime import timedelta
from ..models.client import Client
from ..core.security import verify_password, create_access_token, decode_access_token
from ..core.config import settings


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_client(self, client_id: str, client_secret: str):
        client = self.db.query(Client).filter(
            Client.client_id == client_id,
            Client.is_active == True
        ).first()

        if not client:
            return None

        if not verify_password(client_secret, client.client_secret_hash):
            return None

        return client

    def create_token(self, client: Client):
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

    def get_client_from_token(self, token: str):
        payload = decode_access_token(token)
        if not payload:
            return None

        client_id = payload.get("sub")
        if not client_id:
            return None

        return self.db.query(Client).filter(
            Client.client_id == client_id,
            Client.is_active == True
        ).first()
