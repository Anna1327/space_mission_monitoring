from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..services.auth_service import AuthService

security = HTTPBearer()


def get_current_client(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    token = credentials.credentials
    auth_service = AuthService(db)
    client = auth_service.get_client_from_token(token)

    if not client:
        raise HTTPException(status_code=401, detail="Invalid token")

    return client
