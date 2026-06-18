"""Interactive terminal UI for GameForge."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pymongo.errors import DuplicateKeyError

from config.database import get_collections, test_connection
from models.game_model import GameCreate, GameUpdate, LibraryEntryCreate, LibraryUpdate, SENTIMENT_STATES, split_csv
from models.user_model import UserCreate, UserUpdate
from services.library_service import GameForgeService
from utils.terminal_ui import (
    show_chip,
    show_empty,
    show_error,
    show_menu,
    show_message,
    show_panel,
    show_progress,
    show_record,
    show_records,
    show_stats,
    show_title,
)


MENU_OPTIONS = [
    "Add user",
    "List users",
    "Update user",
    "Delete user",
    "Add game",
    "List games",
    "Update game",
    "Delete game",
    "Track a game",
    "Update tracked game",
    "Delete tracked game",
    "View user library",
    "Inspect game HUD",
    "Lore-link suggestions",
    "Search games",
    "View user stats",
    "List all library entries",
    "Exit",
]


def run_cli() -> None:
    try:
        test_connection()
    except RuntimeError as exc:
        show_error(str(exc))
        return

    service = GameForgeService(*get_collections())
    service.ensure_indexes()

    while True:
        show_title("GameForge", "Cyber terminal game tracking system")
        show_menu(MENU_OPTIONS)
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                add_user(service)
            elif choice == "2":
                list_users(service)
            elif choice == "3":
                update_user(service)
            elif choice == "4":
                delete_user(service)
            elif choice == "5":
                add_game(service)
            elif choice == "6":
                list_games(service)
            elif choice == "7":
                update_game(service)
            elif choice == "8":
                delete_game(service)
            elif choice == "9":
                track_game(service)
            elif choice == "10":
                update_track(service)
            elif choice == "11":
                delete_track(service)
            elif choice == "12":
                view_library(service)
            elif choice == "13":
                inspect_game(service)
            elif choice == "14":
                lore_suggestions(service)
            elif choice == "15":
                search_games(service)
            elif choice == "16":
                view_stats(service)
            elif choice == "17":
                list_all_library(service)
            elif choice == "18":
                show_message("exit", "Goodbye.")
                break
            else:
                show_error("Invalid option.")
        except (ValueError, DuplicateKeyError) as exc:
            show_error(str(exc))


def add_user(service: GameForgeService) -> None:
    user = UserCreate(
        username=input("Username: "),
        email=input("Email: "),
        favorite_platform=input("Favorite platform: ") or "Unknown",
        favorite_genres=split_csv(input("Favorite genres (comma-separated): ")),
        playstyles=split_csv(input("Playstyles (comma-separated): ")),
        bio=input("Short bio: "),
    )
    created = service.create_user(user)
    show_record("User Created", created)


def list_users(service: GameForgeService) -> None:
    users = service.list_users()
    if not users:
        show_empty("No users registered.")
        return
    show_records("User Registry", users)


def update_user(service: GameForgeService) -> None:
    user_ref = input("User ID or username: ")
    user = _resolve_user(service, user_ref)
    update = UserUpdate(
        username=_optional_text(input("Username (blank to skip): ")),
        email=_optional_text(input("Email (blank to skip): ")),
        favorite_platform=_optional_text(input("Favorite platform (blank to skip): ")),
        favorite_genres=_optional_csv(input("Favorite genres (blank to skip): ")),
        playstyles=_optional_csv(input("Playstyles (blank to skip): ")),
        bio=_optional_text(input("Bio (blank to skip): ")),
    )
    updated = service.update_user(user["_id"], update)
    show_record("User Updated", updated or user)


def delete_user(service: GameForgeService) -> None:
    user_ref = input("User ID or username: ")
    user = _resolve_user(service, user_ref)
    if service.delete_user(user["_id"]):
        show_message("deleted", "User and linked library entries deleted.")
    else:
        show_empty("No matching user found.")


def add_game(service: GameForgeService) -> None:
    game = GameCreate(
        title=input("Game title: "),
        genre=split_csv(input("Genres (comma-separated): ")),
        playstyles=split_csv(input("Playstyles (comma-separated): ")),
        lore_tags=split_csv(input("Lore tags (comma-separated): ")),
        developer=input("Developer: "),
        release_year=int(input("Release year: ")),
        price_paid=float(input("Price paid: ") or "0"),
        platform=input("Platform: ") or "Unknown",
        description=input("Description: "),
    )
    created = service.create_game(game)
    show_game_card(service.view_game(created["_id"]) or created)


def list_games(service: GameForgeService) -> None:
    games = service.list_games()
    if not games:
        show_empty("No games registered.")
        return
    show_records("Game Vault", games)


def update_game(service: GameForgeService) -> None:
    game_ref = input("Game ID or title: ")
    game = _resolve_game(service, game_ref)
    update = GameUpdate(
        title=_optional_text(input("Title (blank to skip): ")),
        genre=_optional_csv(input("Genres (blank to skip): ")),
        playstyles=_optional_csv(input("Playstyles (blank to skip): ")),
        lore_tags=_optional_csv(input("Lore tags (blank to skip): ")),
        developer=_optional_text(input("Developer (blank to skip): ")),
        release_year=_optional_int(input("Release year (blank to skip): ")),
        price_paid=_optional_float(input("Price paid (blank to skip): ")),
        platform=_optional_text(input("Platform (blank to skip): ")),
        description=_optional_text(input("Description (blank to skip): ")),
    )
    updated = service.update_game(game["_id"], update)
    show_game_card(service.view_game(updated["_id"]) if updated else game)


def delete_game(service: GameForgeService) -> None:
    game_ref = input("Game ID or title: ")
    game = _resolve_game(service, game_ref)
    if service.delete_game(game["_id"]):
        show_message("deleted", "Game and linked library entries deleted.")
    else:
        show_empty("No matching game found.")


def track_game(service: GameForgeService) -> None:
    entry = LibraryEntryCreate(
        user_id=input("User ID or username: "),
        game_id=input("Game ID or title: "),
        hours_played=float(input("Hours played: ") or "0"),
        status=input("Status [Wishlist/Playing/Completed/Paused]: ") or "Wishlist",
        sentiment_state=_sentiment_prompt(),
        sentiment_score=_bounded_int(input("Sentiment score 1-5: ") or "3", 1, 5),
        rating=_optional_float(input("Rating 0-10 (optional): ")),
        comment=input("Comment: "),
        achievements_unlocked=split_csv(input("Achievements unlocked (comma-separated): ")),
        completion_percentage=int(input("Completion percentage: ") or "0"),
        last_played_at=_optional_datetime(input("Last played ISO datetime (optional): ")),
    )
    created = service.create_library_entry(entry)
    show_library_entry(service, service.view_library_entry(created["_id"]) or created)


def update_track(service: GameForgeService) -> None:
    entry_id = input("Tracked entry ID: ")
    update = LibraryUpdate(
        hours_played=_optional_float(input("Hours played (blank to skip): ")),
        status=_optional_text(input("Status (blank to skip): ")),
        sentiment_state=_optional_text(input("Sentiment state (blank to skip): ")),
        sentiment_score=_optional_int(input("Sentiment score 1-5 (blank to skip): ")),
        rating=_optional_float(input("Rating (blank to skip): ")),
        comment=_optional_text(input("Comment (blank to skip): ")),
        completion_percentage=_optional_int(input("Completion percentage (blank to skip): ")),
        achievements_unlocked=_optional_csv(input("Achievements unlocked (blank to skip): ")),
        last_played_at=_optional_datetime(input("Last played ISO datetime (blank to skip): ")),
    )
    updated = service.update_library_entry(entry_id, update)
    if updated:
        show_library_entry(service, service.view_library_entry(updated["_id"]) or updated)
    else:
        show_empty("No matching tracked entry found.")


def delete_track(service: GameForgeService) -> None:
    entry_id = input("Tracked entry ID: ")
    if service.delete_library_entry(entry_id):
        show_message("deleted", "Tracked entry deleted.")
    else:
        show_empty("No matching tracked entry found.")


def view_library(service: GameForgeService) -> None:
    user_ref = input("User ID or username: ")
    entries = service.list_user_library(user_ref)
    if not entries:
        show_empty("No tracked games found.")
        return
    for entry in entries:
        show_library_entry(service, entry)


def list_all_library(service: GameForgeService) -> None:
    entries = service.list_library_entries()
    if not entries:
        show_empty("Library is empty.")
        return
    for entry in entries:
        show_library_entry(service, entry)


def inspect_game(service: GameForgeService) -> None:
    game_ref = input("Game ID or title: ")
    game = _resolve_game(service, game_ref)
    show_game_card(service.game_insight(game["_id"]))


def lore_suggestions(service: GameForgeService) -> None:
    game_ref = input("Game ID or title: ")
    game = _resolve_game(service, game_ref)
    suggestions = service.suggest_next_games(game["_id"])
    if not suggestions:
        show_empty("No lore-linked games found.")
        return
    show_panel(
        "Lore Linker",
        [
            f"Source: {game['title']}",
            *[
                f"{index + 1}. {item['title']} | Shared Traits: {', '.join(item.get('shared_traits', []))}"
                for index, item in enumerate(suggestions)
            ],
        ],
    )


def search_games(service: GameForgeService) -> None:
    results = service.search_games(input("Search term: "))
    if not results:
        show_empty("No games found.")
        return
    for game in results:
        show_game_card(game)


def view_stats(service: GameForgeService) -> None:
    user_ref = input("User ID or username: ")
    stats = service.user_stats(user_ref)
    show_stats("User Stats", stats)
    show_progress("Library Completion", stats.get("avg_completion") or 0)
    if stats.get("avg_cost_per_hour") is not None:
        show_chip("Avg Cost/Hr", f"${stats['avg_cost_per_hour']:.2f}")
    show_chip("Dusty Games", stats.get("dusty_games", 0))
    show_chip("Worthwhile Games", stats.get("worthwhile_games", 0))


def show_game_card(game: dict) -> None:
    lines = [
        f"Title: {game.get('title', 'N/A')}",
        f"Developer: {game.get('developer', 'N/A')}",
        f"Platform: {game.get('platform', 'N/A')}",
        f"Genres: {', '.join(game.get('genre', [])) or 'N/A'}",
        f"Playstyles: {', '.join(game.get('playstyles', [])) or 'N/A'}",
        f"Lore Tags: {', '.join(game.get('lore_tags', [])) or 'N/A'}",
        f"Price Paid: ${float(game.get('price_paid', 0) or 0):.2f}",
        f"Value State: {game.get('game_value', 'N/A')}",
    ]
    if game.get("added_at"):
        lines.append(f"Added At: {game['added_at']}")
    if game.get("shared_traits"):
        lines.append(f"Shared Traits: {', '.join(game.get('shared_traits', []))}")
    if game.get("lore_link_suggestions"):
        lines.append(f"Lore Links: {len(game['lore_link_suggestions'])} candidates")
    show_panel(game.get("title", "GAME"), lines)


def show_library_entry(service: GameForgeService, entry: dict) -> None:
    game = entry.get("game") or service.get_game(entry.get("game_id")) or {}
    lines = [
        f"User: {entry.get('user_id', 'N/A')}",
        f"Game: {game.get('title', entry.get('game_id', 'N/A'))}",
        f"Hours Played: {entry.get('hours_played', 0):.1f}",
        f"Cost per Hour: ${entry['cost_per_hour']:.2f}" if entry.get('cost_per_hour') is not None else "Cost per Hour: N/A",
        f"Financial Verdict: {entry.get('financial_value', 'N/A')}",
        f"Dust State: {entry.get('dust_state', 'N/A')} ({entry.get('dust_days', 0)} dust days)",
        f"Sentiment: {entry.get('sentiment_state', 'N/A')} / {entry.get('sentiment_score', 'N/A')}",
        f"Status: {entry.get('status', 'N/A')}",
        f"Completion: {entry.get('completion_percentage', 0)}%",
        f"Achievements: {', '.join(entry.get('achievements_unlocked', [])) or 'N/A'}",
        f"Comment: {entry.get('comment', 'N/A')}",
    ]
    if entry.get("last_played_at"):
        lines.append(f"Last Played: {entry['last_played_at']}")
    show_panel(f"TRACKED ENTRY {entry.get('_id', 'N/A')}", lines)
    if entry.get("cost_per_hour") is not None:
        value_score = max(0, min(100, 100 - int(entry["cost_per_hour"] * 10)))
        show_progress("Value Score", value_score)
    show_chip("Dust", entry.get("dust_note", "N/A"))


def _resolve_user(service: GameForgeService, identifier: str) -> dict:
    user = service.find_user(identifier)
    if not user:
        raise ValueError(f"User {identifier} does not exist.")
    return user


def _resolve_game(service: GameForgeService, identifier: str) -> dict:
    game = service.find_game(identifier)
    if not game:
        raise ValueError(f"Game {identifier} does not exist.")
    return game


def _optional_text(value: str) -> Optional[str]:
    value = value.strip()
    return value or None


def _optional_float(value: str) -> Optional[float]:
    value = value.strip()
    return float(value) if value else None


def _optional_int(value: str) -> Optional[int]:
    value = value.strip()
    return int(value) if value else None


def _optional_csv(value: str) -> Optional[list[str]]:
    value = value.strip()
    return split_csv(value) if value else None


def _optional_datetime(value: str) -> Optional[datetime]:
    value = value.strip()
    if not value:
        return None
    return datetime.fromisoformat(value)


def _bounded_int(value: str, minimum: int, maximum: int) -> int:
    number = int(value)
    return max(minimum, min(maximum, number))


def _sentiment_prompt() -> str:
    choice = input(f"Sentiment state {SENTIMENT_STATES}: ").strip()
    return choice if choice in SENTIMENT_STATES else "Playing"
