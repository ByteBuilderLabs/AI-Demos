from pathlib import Path


def read_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_file(path: str, content: str) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"wrote {len(content)} chars to {path}"


REQUIRED_FIELDS = ["title", "summary", "owner", "deadline", "risks"]


def verify(path: str) -> str:
    report = read_file(path).lower()
    missing = [f for f in REQUIRED_FIELDS if f not in report]
    return "PASS" if not missing else f"FAIL missing: {', '.join(missing)}"
