from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...services.auth_service import AuthService
from ...schemas.auth import ClientCredentials, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
def login(credentials: ClientCredentials, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    client = auth_service.authenticate_client(credentials.client_id, credentials.client_secret)

    if not client:
        raise HTTPException(status_code=401, detail="Invalid client credentials")

    return auth_service.create_token(client)
