from typing import TypedDict
from pydantic import BaseModel


class SubQuery(BaseModel):
    query: str
    docs: list[str] = []
    is_relevant: bool = False
    retry_count: int = 0


class GraphState(TypedDict):
    original_query: str
    sub_queries: list[SubQuery]
    final_answer: str