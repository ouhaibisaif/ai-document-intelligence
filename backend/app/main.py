from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import documents_router
from app.core.config import get_settings
from app.core.rate_limit import RateLimitMiddleware
from app.db.session import Base, engine
from app.models import ChatMessage, Document

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)
app.add_middleware(
    RateLimitMiddleware, requests_per_minute=settings.request_limit_per_minute
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(documents_router)
