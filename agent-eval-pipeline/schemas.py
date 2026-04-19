from pydantic import BaseModel, Field


class AccuracyScore(BaseModel):
    score: float = Field(ge=0.0, le=1.0, description="Correctness score from 0 to 1")
    reasoning: str = Field(description="Short explanation for the score")
