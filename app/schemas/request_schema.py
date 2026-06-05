from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class AcademicInfo(BaseModel):
    cgpa: float = Field(
        ge=0.0,
        le=10.0,
        json_schema_extra={"example": 8.5},
    )
    aptitude_score: int = Field(
        ge=0,
        le=100,
        json_schema_extra={"example": 78},
    )


class SkillInfo(BaseModel):
    communication_score: int = Field(
        ge=0,
        le=100,
        json_schema_extra={"example": 82},
    )
    dsa_score: int = Field(
        ge=0,
        le=100,
        json_schema_extra={"example": 70},
    )
    projects: int = Field(
        ge=0,
        json_schema_extra={"example": 3},
    )


class StudentRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "academic": {
                    "cgpa": 8.5,
                    "aptitude_score": 78,
                },
                "skills": {
                    "communication_score": 82,
                    "dsa_score": 70,
                    "projects": 3,
                },
                "internship_experience": True,
            }
        }
    )

    academic: AcademicInfo
    skills: SkillInfo
    internship_experience: bool = Field(json_schema_extra={"example": True})

    @computed_field
    @property
    def placement_readiness_score(self) -> float:
        score = (
            (self.academic.cgpa * 5)
            + (self.academic.aptitude_score * 0.2)
            + (self.skills.communication_score * 0.15)
            + (self.skills.dsa_score * 0.15)
            + (self.skills.projects * 2)
            + (10 if self.internship_experience else 0)
        )
        return round(min(score, 100.0), 2)

    @field_validator("academic", mode="after")
    @classmethod
    def validate_academic_combination(cls, academic: AcademicInfo) -> AcademicInfo:
        if academic.cgpa < 5.0 and academic.aptitude_score > 90:
            raise ValueError(
                "Unusual combination: very low CGPA with very high aptitude score. "
                "Please verify inputs."
            )
        return academic
