from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from pydantic import BaseModel
from sqlalchemy import asc, desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Prediction
from app.schemas.request_schema import StudentRequest
from app.schemas.response_schema import (
    PredictionListResponse,
    PredictionResponse,
    ProbabilityBreakdown,
)
from app.services import predictor

router = APIRouter(prefix="/predictions", tags=["Predictions"])

SORTABLE_FIELDS = {
    "cgpa": Prediction.cgpa,
    "confidence": Prediction.confidence,
    "created_at": Prediction.created_at,
}
VALID_STATUSES = {"Placed", "Not Placed"}
VALID_ORDERS = {"asc", "desc"}


class UpdatePredictionRequest(BaseModel):
    cgpa: Optional[float] = None
    aptitude_score: Optional[int] = None
    communication_score: Optional[int] = None
    dsa_score: Optional[int] = None
    projects: Optional[int] = None
    internship_experience: Optional[bool] = None


def _to_prediction_response(record: Prediction) -> PredictionResponse:
    return PredictionResponse(
        id=record.id,
        placement_prediction=record.placement_prediction,
        confidence=record.confidence,
        probabilities=ProbabilityBreakdown(
            placed=record.placed_probability,
            not_placed=record.not_placed_probability,
        ),
        placement_readiness_score=record.placement_readiness_score,
        created_at=record.created_at,
    )


def _get_prediction_or_404(db: Session, prediction_id: int) -> Prediction:
    record = db.scalar(select(Prediction).where(Prediction.id == prediction_id))
    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Prediction {prediction_id} not found",
        )
    return record


@router.post("/predict", response_model=PredictionResponse, status_code=201)
def create_prediction(
    request: StudentRequest,
    db: Session = Depends(get_db),
) -> PredictionResponse:
    try:
        result = predictor.predict(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    record = Prediction(
        cgpa=request.academic.cgpa,
        aptitude_score=request.academic.aptitude_score,
        communication_score=request.skills.communication_score,
        dsa_score=request.skills.dsa_score,
        projects=request.skills.projects,
        internship_experience=request.internship_experience,
        placement_readiness_score=request.placement_readiness_score,
        placement_prediction=result["placement_prediction"],
        confidence=result["confidence"],
        placed_probability=result["placed_probability"],
        not_placed_probability=result["not_placed_probability"],
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save prediction: {exc}",
        ) from exc

    return _to_prediction_response(record)


@router.get("/", response_model=PredictionListResponse)
def list_predictions(
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by 'Placed' or 'Not Placed'"),
    sort_by: Optional[str] = Query(None, description="Sort by: cgpa, confidence, created_at"),
    order: str = Query("desc", description="Sort order: asc or desc"),
    min_confidence: Optional[float] = Query(
        None, ge=0, le=100, description="Minimum confidence %"
    ),
) -> PredictionListResponse:
    if status is not None and status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Must be 'Placed' or 'Not Placed'.",
        )

    if order not in VALID_ORDERS:
        raise HTTPException(
            status_code=400,
            detail="Invalid order. Must be 'asc' or 'desc'.",
        )

    if sort_by is not None and sort_by not in SORTABLE_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by value. Must be one of: {', '.join(SORTABLE_FIELDS)}",
        )

    try:
        stmt = select(Prediction)

        if status is not None:
            stmt = stmt.where(Prediction.placement_prediction == status)

        if min_confidence is not None:
            stmt = stmt.where(Prediction.confidence >= min_confidence)

        if sort_by is not None:
            sort_column = SORTABLE_FIELDS[sort_by]
            stmt = stmt.order_by(
                asc(sort_column) if order == "asc" else desc(sort_column)
            )

        records = db.scalars(stmt).all()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list predictions: {exc}",
        ) from exc

    return PredictionListResponse(
        total=len(records),
        predictions=[_to_prediction_response(record) for record in records],
    )


@router.get("/{prediction_id}", response_model=PredictionResponse)
def get_prediction(
    prediction_id: int = Path(..., ge=1, description="The prediction record ID"),
    db: Session = Depends(get_db),
) -> PredictionResponse:
    try:
        record = _get_prediction_or_404(db, prediction_id)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve prediction: {exc}",
        ) from exc

    return _to_prediction_response(record)


@router.put("/{prediction_id}", response_model=PredictionResponse)
def update_prediction(
    update: UpdatePredictionRequest,
    prediction_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
) -> PredictionResponse:
    try:
        record = _get_prediction_or_404(db, prediction_id)

        updates = update.model_dump(exclude_none=True)
        for field, value in updates.items():
            setattr(record, field, value)

        db.commit()
        db.refresh(record)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update prediction: {exc}",
        ) from exc

    return _to_prediction_response(record)


@router.delete("/{prediction_id}", status_code=204)
def delete_prediction(
    prediction_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
) -> Response:
    try:
        record = _get_prediction_or_404(db, prediction_id)
        db.delete(record)
        db.commit()
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete prediction: {exc}",
        ) from exc

    return Response(status_code=204)
