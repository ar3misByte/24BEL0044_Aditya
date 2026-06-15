# models/user_model.py
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class GoalSchema(BaseModel):
    goal_title: str = Field(..., example="Complete 5 RPGs this month")
    target_metric: str = Field(..., example="5 Games")
    is_completed: bool = False

class CustomCollectionSchema(BaseModel):
    collection_name: str = Field(..., example="Games to Play During Summer")
    game_ids: List[str] = []

class UserSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    global_gamer_score: int = 0
    custom_collections: List[CustomCollectionSchema] = []
    goals: List[GoalSchema] = []

    class Config:
        json_schema_extra = {
            "example": {
                "username": "GamerForgeX",
                "email": "player1@gameforge.com",
                "global_gamer_score": 0,
                "custom_collections": [
                    {"collection_name": "100% Completion Goals", "game_ids": []}
                ],
                "goals": [
                    {"goal_title": "Reach 50 gaming hours", "target_metric": "50 Hours", "is_completed": False}
                ]
            }
        }