from sqlalchemy.orm import Session
from ..models.client import Client
from ..schemas.client import ClientCreate
from ..core.security import get_password_hash


class ClientService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: ClientCreate):
        client = Client(
            client_id=data.client_id,
            client_secret_hash=get_password_hash(data.client_secret),
            name=data.name
        )
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def get_by_client_id(self, client_id: str):
        return self.db.query(Client).filter(Client.client_id == client_id).first()
