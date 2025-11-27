from pydantic import BaseModel, ValidationError
from typing import List
import json


class BehaviorSpec(BaseModel):
    name: str
    goal: str
    allowed_operations: List[str]
    prohibited_operations: List[str]
    reasoning_depth: int


class CognitiveBoundaries:
    def __init__(self, max_steps: int):
        self.max_steps = max_steps

    def apply(self, text: str) -> str:
        return (
            f"Limit your reasoning to {self.max_steps} steps. "
            f"Do not exceed this depth.\n{text}"
        )


class ConstraintPrompt:
    @staticmethod
    def apply(text: str, spec: BehaviorSpec) -> str:
        ops = ", ".join(spec.allowed_operations)
        banned = ", ".join(spec.prohibited_operations)

        constraint_block = (
            f"You are {spec.name}. Your primary goal: {spec.goal}.\n"
            f"Allowed operations: {ops}\n"
            f"Prohibited operations: {banned}\n"
            f"NEVER perform prohibited operations.\n"
        )
        return constraint_block + "\n" + text


class OutputGuard(BaseModel):
    reasoning: str
    answer: str

    @classmethod
    def validate_json(cls, raw: str) -> "OutputGuard":
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValidationError.from_exception_data(
                title="Invalid JSON",
                line_errors=[{
                    "loc": ("__root__",),
                    "msg": str(e),
                    "type": "value_error.jsondecode",
                }]
            )
        return cls.model_validate(data)
