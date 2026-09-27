"""Enumerations for the application."""
from enum import Enum


class UserRole(str, Enum):
    """User roles in the system."""

    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

    def __str__(self) -> str:
        return self.value
