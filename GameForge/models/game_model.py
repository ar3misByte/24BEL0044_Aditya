"""Game and library data models used by the CLI."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def split_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


SENTIMENT_STATES = ["Completed", "Playing", "Rage-Quit", "Post-Game-Depression"]


@dataclass
class GameCreate:
    title: str
    genre: List[str]
    playstyles: List[str]
    lore_tags: List[str]
    developer: str
    release_year: int
    price_paid: float
    platform: str = "Unknown"
    description: str = ""

    def to_document(self) -> dict:
        now = utc_now()
        return {
            "title": self.title.strip(),
            "genre": self.genre,
            "playstyles": self.playstyles,
            "lore_tags": self.lore_tags,
            "developer": self.developer.strip(),
            "release_year": self.release_year,
            "price_paid": self.price_paid,
            "platform": self.platform.strip() or "Unknown",
            "description": self.description.strip(),
            "added_at": now,
            "created_at": now,
            "updated_at": now,
        }


@dataclass
class GameUpdate:
    title: Optional[str] = None
    genre: Optional[List[str]] = None
    playstyles: Optional[List[str]] = None
    lore_tags: Optional[List[str]] = None
    developer: Optional[str] = None
    release_year: Optional[int] = None
    price_paid: Optional[float] = None
    platform: Optional[str] = None
    description: Optional[str] = None

    def to_update(self) -> dict:
        payload = {
            "title": self.title.strip() if isinstance(self.title, str) else self.title,
            "genre": self.genre,
            "playstyles": self.playstyles,
            "lore_tags": self.lore_tags,
            "developer": self.developer.strip() if isinstance(self.developer, str) else self.developer,
            "release_year": self.release_year,
            "price_paid": self.price_paid,
            "platform": self.platform.strip() if isinstance(self.platform, str) else self.platform,
            "description": self.description.strip() if isinstance(self.description, str) else self.description,
        }
        return {key: value for key, value in payload.items() if value is not None}


@dataclass
class LibraryEntryCreate:
    user_id: str
    game_id: str
    hours_played: float = 0.0
    status: str = "Wishlist"
    sentiment_state: str = "Playing"
    sentiment_score: int = 3
    rating: Optional[float] = None
    comment: str = ""
    achievements_unlocked: List[str] = field(default_factory=list)
    completion_percentage: int = 0
    last_played_at: Optional[datetime] = None

    def to_document(self) -> dict:
        now = utc_now()
        return {
            "user_id": self.user_id,
            "game_id": self.game_id,
            "hours_played": self.hours_played,
            "playtime_hours": self.hours_played,
            "status": self.status,
            "sentiment_state": self.sentiment_state,
            "sentiment_score": self.sentiment_score,
            "rating": self.rating,
            "comment": self.comment.strip(),
            "achievements_unlocked": self.achievements_unlocked,
            "completion_percentage": self.completion_percentage,
            "last_played_at": self.last_played_at,
            "created_at": now,
            "updated_at": now,
        }


@dataclass
class LibraryUpdate:
    hours_played: Optional[float] = None
    status: Optional[str] = None
    sentiment_state: Optional[str] = None
    sentiment_score: Optional[int] = None
    rating: Optional[float] = None
    comment: Optional[str] = None
    completion_percentage: Optional[int] = None
    achievements_unlocked: Optional[List[str]] = None
    last_played_at: Optional[datetime] = None

    def to_update(self) -> dict:
        payload = {
            "hours_played": self.hours_played,
            "playtime_hours": self.hours_played,
            "status": self.status,
            "sentiment_state": self.sentiment_state,
            "sentiment_score": self.sentiment_score,
            "rating": self.rating,
            "comment": self.comment.strip() if isinstance(self.comment, str) else self.comment,
            "completion_percentage": self.completion_percentage,
            "achievements_unlocked": self.achievements_unlocked,
            "last_played_at": self.last_played_at,
        }
        return {key: value for key, value in payload.items() if value is not None}
