from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
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
async def login(credentials: ClientCredentials, db: AsyncSession = Depends(get_db)):
    """
    Получить JWT токен по client_id и client_secret (асинхронно).
    """
    if not credentials.client_id or not credentials.client_secret:
        raise HTTPException(
            status_code=400,
            detail="client_id and client_secret are required"
        )

    auth_service = AuthService(db)
    client = await auth_service.authenticate_client(
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
async def register_client(
    data: ClientCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Зарегистрировать нового клиента (асинхронно).
    """
    client_service = ClientService(db)

    existing = await client_service.get_by_client_id(data.client_id)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Client with client_id '{data.client_id}' already exists"
        )

    try:
        client = await client_service.create(data)
        return client
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create client: {str(e)}"
        )
