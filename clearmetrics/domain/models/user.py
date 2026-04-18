import re
from dataclasses import dataclass
from enum import Enum

_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UserRole(Enum):
    """Enumeration of valid user roles."""

    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


@dataclass(frozen=True)
class User:
    """Immutable domain model representing a platform user."""

    id: str
    email: str
    role: UserRole
    hashed_password: str

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("User id must not be empty.")
        if not self.email or not _EMAIL_REGEX.match(self.email):
            raise ValueError(f"'{self.email}' is not a valid email address.")
        if not self.hashed_password:
            raise ValueError("User hashed_password must not be empty.")
