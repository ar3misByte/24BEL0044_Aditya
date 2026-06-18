"""Database operations for the GameForge CLI."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.collection import Collection

from models.game_model import GameCreate, GameUpdate, LibraryEntryCreate, LibraryUpdate
from models.user_model import UserCreate, UserUpdate


def _normalize_doc(document: Dict[str, Any]) -> Dict[str, Any]:
    if not document:
        return document
    normalized = dict(document)
    normalized["_id"] = str(normalized["_id"])
    for key in ("user_id", "game_id"):
        if key in normalized and isinstance(normalized[key], ObjectId):
            normalized[key] = str(normalized[key])
    return normalized


def _utcify(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class GameForgeService:
    def __init__(self, users: Collection, games: Collection, library: Collection) -> None:
        self.users = users
        self.games = games
        self.library = library

    def ensure_indexes(self) -> None:
        self.users.create_index("email", unique=True)
        self.games.create_index([("title", 1), ("developer", 1)])
        self.games.create_index([("lore_tags", 1)])
        self.games.create_index([("genre", 1)])
        self.games.create_index([("playstyles", 1)])
        self.library.create_index([("user_id", 1), ("game_id", 1)], unique=True)
        self.library.create_index([("status", 1)])

    def create_user(self, user: UserCreate) -> Dict[str, Any]:
        result = self.users.insert_one(user.to_document())
        return self.get_user(result.inserted_id)

    def list_users(self) -> List[Dict[str, Any]]:
        return [_normalize_doc(user) for user in self.users.find().sort("username", 1)]

    def update_user(self, user_id: str, update: UserUpdate) -> Optional[Dict[str, Any]]:
        payload = update.to_update()
        if payload:
            payload["updated_at"] = datetime.now(timezone.utc)
            self.users.update_one({"_id": self._to_object_id(user_id)}, {"$set": payload})
        return self.get_user(user_id)

    def delete_user(self, user_id: str) -> bool:
        user = self._resolve_user(user_id)
        self.library.delete_many({"user_id": user["_id"]})
        result = self.users.delete_one({"_id": self._to_object_id(user["_id"] )})
        return result.deleted_count == 1

    def create_game(self, game: GameCreate) -> Dict[str, Any]:
        result = self.games.insert_one(game.to_document())
        return self.get_game(result.inserted_id)

    def view_game(self, game_id: str) -> Optional[Dict[str, Any]]:
        game = self.get_game(game_id)
        return self._decorate_game(game) if game else None

    def list_games(self) -> List[Dict[str, Any]]:
        return [self._decorate_game(game) for game in self.games.find().sort("title", 1)]

    def update_game(self, game_id: str, update: GameUpdate) -> Optional[Dict[str, Any]]:
        payload = update.to_update()
        if payload:
            payload["updated_at"] = datetime.now(timezone.utc)
            self.games.update_one({"_id": self._to_object_id(game_id)}, {"$set": payload})
        return self.get_game(game_id)

    def delete_game(self, game_id: str) -> bool:
        game = self.get_game(game_id)
        if not game:
            return False
        self.library.delete_many({"game_id": game["_id"]})
        result = self.games.delete_one({"_id": self._to_object_id(game["_id"] )})
        return result.deleted_count == 1

    def create_library_entry(self, entry: LibraryEntryCreate) -> Dict[str, Any]:
        user = self._resolve_user(entry.user_id)
        game = self._resolve_game(entry.game_id)
        resolved_entry = entry.to_document()
        resolved_entry["user_id"] = user["_id"]
        resolved_entry["game_id"] = game["_id"]
        result = self.library.insert_one(resolved_entry)
        return self.get_library_entry(result.inserted_id)

    def view_library_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        entry = self.get_library_entry(entry_id)
        return self._decorate_library_entry(entry) if entry else None

    def list_library_entries(self) -> List[Dict[str, Any]]:
        return [self._decorate_library_entry(entry) for entry in self.library.find().sort("updated_at", -1)]

    def update_library_entry(self, entry_id: str, update: LibraryUpdate) -> Optional[Dict[str, Any]]:
        payload = update.to_update()
        if payload:
            if "hours_played" in payload:
                payload["last_played_at"] = payload.get("last_played_at") or datetime.now(timezone.utc)
            payload["updated_at"] = datetime.now(timezone.utc)
            self.library.update_one({"_id": self._to_object_id(entry_id)}, {"$set": payload})
        return self.get_library_entry(entry_id)

    def delete_library_entry(self, entry_id: str) -> bool:
        result = self.library.delete_one({"_id": self._to_object_id(entry_id)})
        return result.deleted_count == 1

    def list_user_library(self, user_id: str) -> List[Dict[str, Any]]:
        user = self._resolve_user(user_id)
        entries: List[Dict[str, Any]] = []
        for entry in self.library.find({"user_id": user["_id"]}):
            entries.append(self._decorate_library_entry(entry))
        return entries

    def user_stats(self, user_id: str) -> Dict[str, Any]:
        user = self._resolve_user(user_id)
        pipeline = [
            {"$match": {"user_id": user["_id"]}},
            {
                "$group": {
                    "_id": "$user_id",
                    "tracked_games": {"$sum": 1},
                    "total_playtime": {"$sum": {"$ifNull": ["$hours_played", "$playtime_hours"]}},
                    "avg_rating": {"$avg": "$rating"},
                    "avg_completion": {"$avg": "$completion_percentage"},
                    "completed_games": {
                        "$sum": {"$cond": [{"$eq": ["$status", "Completed"]}, 1, 0]}
                    },
                    "total_achievements": {
                        "$sum": {"$size": {"$ifNull": ["$achievements_unlocked", []]}}
                    },
                }
            },
        ]
        result = list(self.library.aggregate(pipeline))
        if not result:
            return {
                "tracked_games": 0,
                "total_playtime": 0,
                "avg_rating": None,
                "avg_completion": None,
                "completed_games": 0,
                "total_achievements": 0,
                "total_spent": 0,
                "avg_cost_per_hour": None,
                "worthwhile_games": 0,
                "dusty_games": 0,
            }
        stats = result[0]
        stats.pop("_id", None)
        stats["total_spent"] = self._user_total_spent(user["_id"])
        stats["avg_cost_per_hour"] = self._user_avg_cost_per_hour(user["_id"])
        stats["worthwhile_games"] = self._count_worthwhile_games(user["_id"])
        stats["dusty_games"] = self._count_dusty_games(user["_id"])
        return stats

    def search_games(self, query: str) -> List[Dict[str, Any]]:
        terms = query.strip()
        if not terms:
            return []
        filter_query = {
            "$or": [
                {"title": {"$regex": terms, "$options": "i"}},
                {"developer": {"$regex": terms, "$options": "i"}},
                {"genre": {"$regex": terms, "$options": "i"}},
                {"playstyles": {"$regex": terms, "$options": "i"}},
                {"lore_tags": {"$regex": terms, "$options": "i"}},
            ]
        }
        return [self._decorate_game(game) for game in self.games.find(filter_query).limit(20)]

    def suggest_next_games(self, game_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        source = self.get_game(game_id)
        if not source:
            raise ValueError(f"Game {game_id} does not exist.")

        source_tags = set(source.get("lore_tags", [])) | set(source.get("genre", [])) | set(source.get("playstyles", []))
        recommendations: List[Dict[str, Any]] = []

        for game in self.games.find({"_id": {"$ne": self._to_object_id(source["_id"])}}):
            game_tags = set(game.get("lore_tags", [])) | set(game.get("genre", [])) | set(game.get("playstyles", []))
            overlap = sorted(source_tags & game_tags)
            if not overlap:
                continue
            decorated = self._decorate_game(game)
            decorated["shared_traits"] = overlap
            decorated["match_score"] = len(overlap)
            recommendations.append(decorated)

        recommendations.sort(key=lambda item: (item["match_score"], item.get("price_paid", 0)), reverse=True)
        return recommendations[:limit]

    def game_insight(self, game_id: str) -> Dict[str, Any]:
        game = self.get_game(game_id)
        if not game:
            raise ValueError(f"Game {game_id} does not exist.")
        decorated = self._decorate_game(game)
        decorated["lore_link_suggestions"] = self.suggest_next_games(game_id)
        return decorated

    def get_user(self, user_id: Any) -> Optional[Dict[str, Any]]:
        return self._get_by_id(self.users, user_id)

    def find_user(self, user_identifier: str) -> Optional[Dict[str, Any]]:
        try:
            user = self.get_user(user_identifier)
            if user:
                return user
        except ValueError:
            pass
        user = self.users.find_one({"username": user_identifier})
        return _normalize_doc(user) if user else None

    def get_game(self, game_id: Any) -> Optional[Dict[str, Any]]:
        return self._get_by_id(self.games, game_id)

    def find_game(self, game_identifier: str) -> Optional[Dict[str, Any]]:
        try:
            game = self.get_game(game_identifier)
            if game:
                return game
        except ValueError:
            pass
        game = self.games.find_one({"title": game_identifier})
        return _normalize_doc(game) if game else None

    def get_library_entry(self, entry_id: Any) -> Optional[Dict[str, Any]]:
        return self._get_by_id(self.library, entry_id)

    def _get_by_id(self, collection: Collection, doc_id: Any) -> Optional[Dict[str, Any]]:
        try:
            object_id = self._to_object_id(doc_id)
        except ValueError:
            return None
        document = collection.find_one({"_id": object_id})
        return _normalize_doc(document) if document else None

    def _require_user(self, user_id: str) -> None:
        self._resolve_user(user_id)

    def _require_game(self, game_id: str) -> None:
        self._resolve_game(game_id)

    def _decorate_game(self, game: Dict[str, Any]) -> Dict[str, Any]:
        normalized = _normalize_doc(game)
        price = normalized.get("price_paid", 0) or 0
        normalized["lore_tag_count"] = len(normalized.get("lore_tags", []))
        normalized["playstyle_count"] = len(normalized.get("playstyles", []))
        normalized["price_paid"] = price
        normalized["game_value"] = self._game_value_label(price, normalized)
        normalized["lore_anchor"] = ", ".join(normalized.get("lore_tags", [])[:3]) or "None"
        return normalized

    def _decorate_library_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        normalized = _normalize_doc(entry)
        game = self.get_game(normalized["game_id"])
        if game:
            game = self._decorate_game(game)
        normalized["game"] = game or {"_id": normalized["game_id"], "missing": True}

        hours_played = normalized.get("hours_played", normalized.get("playtime_hours", 0)) or 0
        price_paid = (game or {}).get("price_paid", 0) or 0
        cost_per_hour = price_paid / hours_played if hours_played > 0 else None
        dust_info = self._dust_info(game, normalized)

        normalized["hours_played"] = hours_played
        normalized["cost_per_hour"] = cost_per_hour
        normalized["financial_value"] = self._value_verdict(cost_per_hour, hours_played, price_paid)
        normalized["dust_days"] = dust_info["dust_days"]
        normalized["dust_state"] = dust_info["dust_state"]
        normalized["dust_score"] = dust_info["dust_score"]
        normalized["dust_note"] = dust_info["dust_note"]
        normalized["updated_age_days"] = dust_info["updated_age_days"]
        return normalized

    def _dust_info(self, game: Optional[Dict[str, Any]], entry: Dict[str, Any]) -> Dict[str, Any]:
        anchor = entry.get("last_played_at") or (game or {}).get("added_at") or entry.get("created_at")
        if not isinstance(anchor, datetime):
            anchor = datetime.now(timezone.utc)
        else:
            anchor = _utcify(anchor) or datetime.now(timezone.utc)
        now = datetime.now(timezone.utc)
        updated_age_days = max(0, (now - anchor).days)
        dust_days = max(0, updated_age_days - 180)
        if dust_days == 0:
            state = "FRESH"
            note = "Recently active"
        elif dust_days < 30:
            state = "DUSTING"
            note = "A little rust is forming"
        else:
            state = "RUSTED"
            note = "Untouched for 6+ months"
        return {
            "updated_age_days": updated_age_days,
            "dust_days": dust_days,
            "dust_score": min(100, int(dust_days / 3)),
            "dust_state": state,
            "dust_note": note,
        }

    def _value_verdict(self, cost_per_hour: Optional[float], hours_played: float, price_paid: float) -> str:
        if hours_played <= 0:
            return "NO PLAYTIME YET"
        if price_paid <= 0:
            return "FREE VALUE"
        if cost_per_hour is not None and cost_per_hour <= 1.0:
            return "HIGH VALUE"
        if hours_played >= price_paid:
            return "WORTH IT"
        if cost_per_hour is not None and cost_per_hour <= 2.5:
            return "GOOD VALUE"
        return "EXPENSIVE"

    def _game_value_label(self, price_paid: float, game: Dict[str, Any]) -> str:
        if price_paid <= 0:
            return "FREE"
        if len(game.get("lore_tags", [])) >= 3:
            return "RICH"
        return "STANDARD"

    def _user_total_spent(self, user_id: str) -> float:
        total = 0.0
        for entry in self.library.find({"user_id": user_id}):
            game = self.get_game(entry["game_id"])
            if game:
                total += float(game.get("price_paid", 0) or 0)
        return total

    def _user_avg_cost_per_hour(self, user_id: str) -> Optional[float]:
        values = []
        for entry in self.library.find({"user_id": user_id}):
            game = self.get_game(entry["game_id"])
            if not game:
                continue
            hours_played = entry.get("hours_played", entry.get("playtime_hours", 0)) or 0
            price_paid = float(game.get("price_paid", 0) or 0)
            if hours_played > 0 and price_paid > 0:
                values.append(price_paid / hours_played)
        if not values:
            return None
        return sum(values) / len(values)

    def _count_worthwhile_games(self, user_id: str) -> int:
        count = 0
        for entry in self.library.find({"user_id": user_id}):
            game = self.get_game(entry["game_id"])
            if not game:
                continue
            hours_played = entry.get("hours_played", entry.get("playtime_hours", 0)) or 0
            price_paid = float(game.get("price_paid", 0) or 0)
            cost_per_hour = price_paid / hours_played if hours_played > 0 and price_paid > 0 else None
            if self._value_verdict(cost_per_hour, hours_played, price_paid) in {"HIGH VALUE", "GOOD VALUE", "WORTH IT", "FREE VALUE"}:
                count += 1
        return count

    def _count_dusty_games(self, user_id: str) -> int:
        count = 0
        for entry in self.library.find({"user_id": user_id}):
            game = self.get_game(entry["game_id"])
            if not game:
                continue
            if self._dust_info(game, _normalize_doc(entry))["dust_days"] > 0:
                count += 1
        return count

    def _game_summary(self, game_id: str) -> Dict[str, Any]:
        game = self.get_game(game_id)
        if not game:
            return {"_id": game_id, "missing": True}
        decorated = self._decorate_game(game)
        return {
            "_id": decorated["_id"],
            "title": decorated["title"],
            "developer": decorated.get("developer", ""),
            "platform": decorated.get("platform", "Unknown"),
            "price_paid": decorated.get("price_paid", 0),
            "game_value": decorated.get("game_value", "STANDARD"),
            "lore_tags": decorated.get("lore_tags", []),
            "playstyles": decorated.get("playstyles", []),
        }

    def _resolve_user(self, user_identifier: str) -> Dict[str, Any]:
        user = self.get_user(user_identifier)
        if user:
            return user

        user = self.users.find_one({"username": user_identifier})
        if user:
            return _normalize_doc(user)

        raise ValueError(f"User {user_identifier} does not exist.")

    def _resolve_game(self, game_identifier: str) -> Dict[str, Any]:
        game = self.get_game(game_identifier)
        if game:
            return game

        game = self.games.find_one({"title": game_identifier})
        if game:
            return _normalize_doc(game)

        raise ValueError(f"Game {game_identifier} does not exist.")

    @staticmethod
    def _to_object_id(value: Any) -> ObjectId:
        try:
            return ObjectId(value)
        except (InvalidId, TypeError) as exc:
            raise ValueError(f"Invalid document id: {value}") from exc
