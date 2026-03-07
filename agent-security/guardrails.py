import re, yaml
from pydantic import BaseModel, field_validator

class UserQuery(BaseModel):
    query: str
    user_role: str = "viewer"
    
    @field_validator("query")
    @classmethod
    def validate_query(cls, v):
        if len(v) > 500: raise ValueError("Query exceeds limit")
        return v.strip()
    

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?instructions",
    r"system\s*prompt",
    r"you\s+are\s+now",
    r"act\s+as\s+(if\s+)?you",
]

def detect_injection(text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in INJECTION_PATTERNS)


def load_policy(path="policy.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

def authorize_tool_call(tool_name: str, user_role: str) -> bool:
    policy = load_policy()
    allowed = policy["tool_permissions"].get(user_role, [])
    return tool_name in allowed


SENSITIVE_PATTERNS = [
    (r"\b[\w.+-]+@[\w-]+\.[\w.]+\b", "[EMAIL REDACTED]"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN REDACTED]"),
    (r"sk-[a-zA-Z0-9]{20,}", "[API KEY REDACTED]"),
]

def filter_output(text: str) -> str:
    for pattern, replacement in SENSITIVE_PATTERNS:
        text = re.sub(pattern, replacement, text)
        
    return text