from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProbabilityBreakdown(BaseModel):
    placed: float
    not_placed: float


class PredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    placement_prediction: str
    confidence: float
    probabilities: ProbabilityBreakdown
    placement_readiness_score: float
    created_at: datetime


class PredictionListResponse(BaseModel):
    total: int
    predictions: list[PredictionResponse]


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_version: str
    database: str


class ErrorResponse(BaseModel):
    detail: str
    status_code: int
