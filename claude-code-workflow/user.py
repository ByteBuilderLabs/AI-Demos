import re

from pydantic import BaseModel, EmailStr

_EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9\-]+(\.[a-zA-Z0-9\-]+)*\.[a-zA-Z]{2,}$"
)


class User(BaseModel):
    """Represents an application user."""

    name: str
    email: EmailStr


def is_valid_email(email: str) -> bool:
    """Return True if email matches a simplified valid address format, False otherwise.

    Strips surrounding whitespace before matching. Checks for a local part,
    an @ symbol, a domain with one or more non-overlapping labels, and a TLD
    of at least two characters. Does not perform DNS resolution and does not
    cover the full RFC 5321 address spec (e.g. quoted locals and IP domains
    are not supported).
    """
    return bool(_EMAIL_RE.match(email.strip()))
