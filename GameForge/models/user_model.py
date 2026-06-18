"""User data model used by the CLI."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class UserCreate:
    username: str
    email: str
    favorite_platform: str = "Unknown"
    favorite_genres: Optional[List[str]] = None
    playstyles: Optional[List[str]] = None
    bio: str = ""

    def to_document(self) -> dict:
        now = utc_now()
        return {
            "username": self.username.strip(),
            "email": self.email.strip().lower(),
            "favorite_platform": self.favorite_platform.strip() or "Unknown",
            "favorite_genres": self.favorite_genres or [],
            "playstyles": self.playstyles or [],
            "bio": self.bio.strip(),
            "created_at": now,
            "updated_at": now,
        }


@dataclass
class UserUpdate:
    username: Optional[str] = None
    email: Optional[str] = None
    favorite_platform: Optional[str] = None
    favorite_genres: Optional[List[str]] = None
    playstyles: Optional[List[str]] = None
    bio: Optional[str] = None

    def to_update(self) -> dict:
        payload = {
            "username": self.username.strip() if isinstance(self.username, str) else self.username,
            "email": self.email.strip().lower() if isinstance(self.email, str) else self.email,
            "favorite_platform": self.favorite_platform.strip() if isinstance(self.favorite_platform, str) else self.favorite_platform,
            "favorite_genres": self.favorite_genres,
            "playstyles": self.playstyles,
            "bio": self.bio.strip() if isinstance(self.bio, str) else self.bio,
        }
        return {key: value for key, value in payload.items() if value is not None}
