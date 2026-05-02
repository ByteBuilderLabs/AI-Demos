from pydantic import BaseModel, Field
from typing import Literal


class Finding(BaseModel):
    severity: Literal["critical", "warning", "info"]
    file_path: str
    line: int
    category: Literal["security", "complexity", "tests", "bug", "style"]
    message: str
    suggestion: str


class Review(BaseModel):
    summary: str
    findings: list[Finding] = Field(default_factory=list)
