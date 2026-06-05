from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database.connection import get_db
from app.schemas.response_schema import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    try:
        db.execute(text("SELECT 1"))
        database = "connected"
    except Exception:
        database = "disconnected"

    return HealthResponse(
        status="healthy",
        model_version=settings.MODEL_VERSION,
        database=database,
    )
