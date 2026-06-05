from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from app.database.connection import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cgpa = Column(Float, nullable=False)
    aptitude_score = Column(Integer, nullable=False)
    communication_score = Column(Integer, nullable=False)
    dsa_score = Column(Integer, nullable=False)
    projects = Column(Integer, nullable=False)
    internship_experience = Column(Boolean, nullable=False)
    placement_readiness_score = Column(Float, nullable=False)
    placement_prediction = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    placed_probability = Column(Float, nullable=False)
    not_placed_probability = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
