from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...schemas.client import ClientResponse, ClientCreate
from ...schemas.auth import ClientCredentials, TokenResponse
from ...services.auth_service import AuthService
from ...services.client_service import ClientService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Bad request: client_id and client_secret are required"},
        401: {"description": "Bad request: Invalid client credentials"}
    }
)
def login(credentials: ClientCredentials, db: Session = Depends(get_db)):
    """
    Получить JWT токен по client_id и client_secret.

    Возможные ошибки:
    - 400: Неверный формат запроса
    - 401: Неверные учётные данные
    """
    if not credentials.client_id or not credentials.client_secret:
        raise HTTPException(
            status_code=400,
            detail="client_id and client_secret are required"
        )

    auth_service = AuthService(db)
    client = auth_service.authenticate_client(
        credentials.client_id,
        credentials.client_secret
    )

    if not client:
        raise HTTPException(
            status_code=401,
            detail="Invalid client credentials"
        )

    return auth_service.create_token(client)


@router.post(
    "/register",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Bad request - invalid format"},
        409: {"description": "Client with this client_id already exists"}
    }
)
def register_client(
    data: ClientCreate,
    db: Session = Depends(get_db)
):
    """
    Зарегистрировать нового клиента.

    Возможные ошибки:
    - 400: Неверный формат запроса
    - 409: Клиент с таким client_id уже существует
    """

    client_service = ClientService(db)

    existing = client_service.get_by_client_id(data.client_id)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Client with client_id '{data.client_id}' already exists"
        )

    try:
        client = client_service.create(data)
        return client
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create client: {str(e)}"
        )
