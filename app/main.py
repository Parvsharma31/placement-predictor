import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.connection import Base, engine
import app.database.models  # noqa: F401
from app.routes import health, prediction
from app.services import predictor

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        predictor.model = predictor.load_model()
    except Exception as exc:
        logger.error("Application startup failed: %s", exc)
        raise RuntimeError(f"Application startup failed: {exc}") from exc

    logger.info("Application startup complete")

    yield

    logger.info("Application shutdown")


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="Production-style ML API for predicting student placement outcomes.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(prediction.router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Student Placement Prediction API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
