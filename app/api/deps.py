from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from ..services.auth_service import AuthService

security = HTTPBearer(auto_error=False)


async def get_current_client(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db)
):
    """
    Получить текущего клиента из JWT токена (полностью асинхронно).

    Возможные ошибки:
    - 401: Токен не предоставлен | Токен невалидный или истёк
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials
    auth_service = AuthService(db)

    client = await auth_service.get_client_from_token(token)

    if not client:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return client
