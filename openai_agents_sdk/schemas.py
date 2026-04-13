from pydantic import BaseModel


class WriterResult(BaseModel):
    summary: str
    tone: str


class TopicCheck(BaseModel):
    is_valid_topic: bool
    reasoning: str