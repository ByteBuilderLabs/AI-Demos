import operator
from typing import TypedDict, Annotated, Optional
from pydantic import BaseModel, Field


class Verdict(BaseModel):
    answer: str = Field(description="Your direct answer to the question")
    evidence: str = Field(description="The specific facts or reasoning behind it")
    agrees_with_peer: bool = Field(
        description="True only if your peer is right and you now agree"
    )


class DebateState(TypedDict):
    question: str
    transcript: Annotated[list[str], operator.add]
    verdict_a: Optional[Verdict]
    verdict_b: Optional[Verdict]
    round: int
    final_answer: str
