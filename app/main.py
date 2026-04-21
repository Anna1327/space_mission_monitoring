from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.v1.router import router as api_v1_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router)


@app.get("/")
def root():
    return {
        "mission": settings.APP_NAME,
        "status": "operational",
        "version": settings.APP_VERSION
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
