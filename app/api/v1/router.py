from fastapi import APIRouter
from . import health, auth, systems, websocket

router = APIRouter(prefix="/api/v1")

router.include_router(health.router)
router.include_router(auth.router)
router.include_router(systems.router)
router.include_router(websocket.router)
