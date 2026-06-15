# models/game_model.py
from pydantic import BaseModel, Field
from typing import List, Optional

class GameSchema(BaseModel):
    title: str = Field(..., description="The name of the video game")
    genre: List[str] = Field(..., description="List of genres applicable (e.g., Action, RPG)")
    developer: str = Field(..., description="Studio that created the game")
    release_year: int = Field(..., ge=1950, le=2030)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Elden Ring",
                "genre": ["Action", "RPG", "Souls-like"],
                "developer": "FromSoftware",
                "release_year": 2022
            }
        }

class LibraryItemSchema(BaseModel):
    user_id: str = Field(..., description="The hex ID of the user matching this entry")
    game_id: str = Field(..., description="The hex ID of the game being tracked")
    playtime_hours: float = Field(0.0, ge=0.0, description="Total logged playing hours")
    status: str = Field("Backlog", description="Options: Backlog, Playing, Completed, Wishlist")
    completion_percentage: int = Field(0, ge=0, le=100)
    story_progress: str = Field("0% Not Started", description="Custom textual update of where they are")
    side_quests_completed: int = Field(0, ge=0)
    achievement_score: int = Field(0, ge=0, description="Accrued score based on unlocked tiers")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "641b2c3e4f1a2b3c4d5e6f7a",
                "game_id": "641b2c3e4f1a2b3c4d5e6f7b",
                "playtime_hours": 42.5,
                "status": "Playing",
                "completion_percentage": 65,
                "story_progress": "Defeated Morgott, moving to Mountaintops",
                "side_quests_completed": 12,
                "achievement_score": 250
            }
        }

class UpdateLibraryItemSchema(BaseModel):
    playtime_hours: Optional[float] = None
    status: Optional[str] = None
    completion_percentage: Optional[int] = None
    story_progress: Optional[str] = None
    side_quests_completed: Optional[int] = None
    achievement_score: Optional[int] = None