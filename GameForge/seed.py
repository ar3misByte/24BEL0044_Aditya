"""Seed sample data for GameForge."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from bson import ObjectId

from config.database import get_collections, test_connection
from models.game_model import GameCreate, LibraryEntryCreate
from models.user_model import UserCreate
from services.library_service import GameForgeService
from utils.terminal_ui import show_message, show_panel, show_title


def _set_game_age(games, game_id: str, days_ago: int) -> None:
    timestamp = datetime.now(timezone.utc) - timedelta(days=days_ago)
    games.update_one(
        {"_id": ObjectId(game_id)},
        {"$set": {"added_at": timestamp, "created_at": timestamp, "updated_at": timestamp}},
    )


def _set_entry_age(library, entry_id: str, days_ago: int) -> None:
    timestamp = datetime.now(timezone.utc) - timedelta(days=days_ago)
    library.update_one(
        {"_id": ObjectId(entry_id)},
        {"$set": {"last_played_at": timestamp, "updated_at": timestamp}},
    )


def seed() -> None:
    test_connection()

    users, games, library = get_collections()
    service = GameForgeService(users, games, library)
    service.ensure_indexes()

    users.delete_many({})
    games.delete_many({})
    library.delete_many({})

    sample_users = [
        UserCreate(
            username="ApexHunter",
            email="apex.hunter@example.com",
            favorite_platform="PC",
            favorite_genres=["RPG", "Action", "Souls-like"],
            playstyles=["Completionist", "Lore Diver", "Boss Hunter"],
            bio="Prefers long RPGs and competitive shooters.",
        ),
        UserCreate(
            username="RetroQuest",
            email="retro.quest@example.com",
            favorite_platform="Nintendo Switch",
            favorite_genres=["Adventure", "Indie", "Action"],
            playstyles=["Speedrunner", "Collector", "Story Focused"],
            bio="Collects indie games and 100% completion runs.",
        ),
        UserCreate(
            username="NocturneByte",
            email="nocturne.byte@example.com",
            favorite_platform="PC",
            favorite_genres=["Horror", "Action", "RPG"],
            playstyles=["Immersion", "Narrative", "Challenge Runner"],
            bio="Prefers moody worlds and mechanically dense combat.",
        ),
        UserCreate(
            username="PixelDrift",
            email="pixel.drift@example.com",
            favorite_platform="PlayStation 5",
            favorite_genres=["Racing", "Sports", "Arcade"],
            playstyles=["Time Trial", "Casual", "Multiplayer"],
            bio="Tracks arcade racers and couch multiplayer staples.",
        ),
        UserCreate(
            username="QuestSyntax",
            email="quest.syntax@example.com",
            favorite_platform="PC",
            favorite_genres=["Strategy", "RPG", "Simulation"],
            playstyles=["Planner", "Optimizer", "Lore Diver"],
            bio="Likes systems-heavy games with deep decision trees.",
        ),
        UserCreate(
            username="SilentLoot",
            email="silent.loot@example.com",
            favorite_platform="Xbox Series X",
            favorite_genres=["Action", "Open World", "Shooter"],
            playstyles=["Completionist", "Collector", "Co-op"],
            bio="Builds giant backlogs and tracks every side quest.",
        ),
        UserCreate(
            username="ArcadeMoth",
            email="arcade.moth@example.com",
            favorite_platform="Nintendo Switch",
            favorite_genres=["Platformer", "Indie", "Puzzle"],
            playstyles=["Speedrunner", "Puzzle Solver", "Score Attack"],
            bio="Chases perfect runs and hidden secrets.",
        ),
        UserCreate(
            username="VantaPatch",
            email="vanta.patch@example.com",
            favorite_platform="PC",
            favorite_genres=["Action", "Metroidvania", "Adventure"],
            playstyles=["Explorer", "Lore Hunter", "Boss Hunter"],
            bio="Enjoys hand-crafted worlds and tight progression loops.",
        ),
        UserCreate(
            username="Moonframe",
            email="moonframe@example.com",
            favorite_platform="PlayStation 5",
            favorite_genres=["Adventure", "Narrative", "Horror"],
            playstyles=["Story Focused", "Immersion", "Decision Maker"],
            bio="Follows emotional stories and atmospheric experiences.",
        ),
        UserCreate(
            username="RiftWarden",
            email="rift.warden@example.com",
            favorite_platform="PC",
            favorite_genres=["MMO", "RPG", "Action"],
            playstyles=["Party Leader", "Grinder", "Economy Watcher"],
            bio="Likes long-term progression and guild-based play.",
        ),
        UserCreate(
            username="NovaReplay",
            email="nova.replay@example.com",
            favorite_platform="Nintendo Switch",
            favorite_genres=["Roguelike", "Action", "Indie"],
            playstyles=["Build Experimentation", "Fast Runs", "Replay Hunter"],
            bio="Replays games until every route is mastered.",
        ),
        UserCreate(
            username="CipherBloom",
            email="cipher.bloom@example.com",
            favorite_platform="PC",
            favorite_genres=["Puzzle", "Strategy", "Adventure"],
            playstyles=["Solver", "Tactician", "Lore Diver"],
            bio="Likes elegant systems and environmental storytelling.",
        ),
    ]

    sample_games = [
        GameCreate(
            title="Elden Ring",
            genre=["Action", "RPG", "Souls-like"],
            playstyles=["Boss Rush", "Exploration", "Build Crafting"],
            lore_tags=["Shattered Empire", "Ancient Gods", "Open World Ritual"],
            developer="FromSoftware",
            release_year=2022,
            price_paid=59.99,
            platform="PC",
            description="An open-world action RPG about exploration and discovery.",
        ),
        GameCreate(
            title="Hades",
            genre=["Roguelike", "Action", "Indie"],
            playstyles=["Fast Runs", "Build Experimentation", "Skill Mastery"],
            lore_tags=["Greek Myth", "Underworld", "Narrative Loop"],
            developer="Supergiant Games",
            release_year=2020,
            price_paid=24.99,
            platform="PC",
            description="Fast-paced escape from the underworld with strong replay value.",
        ),
        GameCreate(
            title="The Legend of Zelda: Tears of the Kingdom",
            genre=["Adventure", "Action", "Open World"],
            playstyles=["Sandbox Creativity", "Puzzle Solving", "Exploration"],
            lore_tags=["Sky Islands", "Ganon Return", "Ancient Tech"],
            developer="Nintendo",
            release_year=2023,
            price_paid=69.99,
            platform="Nintendo Switch",
            description="Large-scale adventure focused on creativity and exploration.",
        ),
        GameCreate(
            title="Neon Circuit",
            genre=["Racing", "Arcade", "Action"],
            playstyles=["Time Trial", "Precision Driving", "Multiplayer"],
            lore_tags=["Neo City", "Street Syndicates", "Turbo Drift"],
            developer="Blacklight Forge",
            release_year=2024,
            price_paid=34.99,
            platform="PC",
            description="A high-speed street racer in a neon-drenched future city.",
        ),
        GameCreate(
            title="Ashfall Protocol",
            genre=["Shooter", "Action", "Sci-Fi"],
            playstyles=["Co-op", "Tactical", "Loot Chase"],
            lore_tags=["Orbital Collapse", "Exo Marines", "Signal Blackout"],
            developer="Iron Comet",
            release_year=2023,
            price_paid=49.99,
            platform="Xbox Series X",
            description="A co-op tactical shooter about surviving a collapsing orbital colony.",
        ),
        GameCreate(
            title="Rune Meridian",
            genre=["RPG", "Strategy", "Fantasy"],
            playstyles=["Planner", "Summoner", "Lore Diver"],
            lore_tags=["Crystal Courts", "Ancient Seals", "Mage Dynasties"],
            developer="Star Atlas Studio",
            release_year=2021,
            price_paid=44.99,
            platform="PC",
            description="A grand strategy RPG where spells and politics shape the kingdom.",
        ),
        GameCreate(
            title="Glass Harbor",
            genre=["Adventure", "Narrative", "Mystery"],
            playstyles=["Story Focused", "Investigator", "Immersion"],
            lore_tags=["Flooded District", "Vanished Choir", "Signal Archive"],
            developer="Harborlight Interactive",
            release_year=2022,
            price_paid=29.99,
            platform="PlayStation 5",
            description="A mystery adventure set in a submerged city with shifting memories.",
        ),
        GameCreate(
            title="Forgebound",
            genre=["Action", "Metroidvania", "Indie"],
            playstyles=["Boss Hunter", "Explorer", "Build Crafting"],
            lore_tags=["Magma Keep", "Broken Covenants", "Living Metal"],
            developer="Ember Vale",
            release_year=2020,
            price_paid=19.99,
            platform="Nintendo Switch",
            description="A hand-crafted traversal game about forging weapons from living metal.",
        ),
        GameCreate(
            title="Quantum Grove",
            genre=["Puzzle", "Simulation", "Indie"],
            playstyles=["Solver", "Experimenter", "Relaxed"],
            lore_tags=["Temporal Trees", "Garden Engine", "Memory Bloom"],
            developer="Moss Circuit",
            release_year=2024,
            price_paid=14.99,
            platform="PC",
            description="A calm puzzle sim where time-bending plants reshape the world.",
        ),
        GameCreate(
            title="Dread Signal",
            genre=["Horror", "Adventure", "Sci-Fi"],
            playstyles=["Immersion", "Survival", "Narrative"],
            lore_tags=["Deep Space", "Last Transmission", "Echo Chamber"],
            developer="Red Static",
            release_year=2023,
            price_paid=39.99,
            platform="PC",
            description="An atmospheric survival horror game about a dead station still broadcasting.",
        ),
        GameCreate(
            title="Skyline Tactics",
            genre=["Strategy", "Simulation", "Tactical"],
            playstyles=["Planner", "Economy Watcher", "Turn-Based"],
            lore_tags=["Floating Districts", "Guild Market", "Storm Grid"],
            developer="North Arrow",
            release_year=2022,
            price_paid=27.99,
            platform="PC",
            description="A city-control strategy title about managing aerial districts and resources.",
        ),
    ]

    created_users = [service.create_user(user) for user in sample_users]
    created_games = [service.create_game(game) for game in sample_games]

    sample_entries = [
        LibraryEntryCreate(
            user_id=created_users[0]["_id"],
            game_id=created_games[0]["_id"],
            hours_played=84.5,
            status="Playing",
            sentiment_state="Playing",
            sentiment_score=5,
            rating=9.5,
            comment="Working through late-game bosses.",
            achievements_unlocked=["First Steps", "Stormveil Clear", "Radahn Defeated"],
            completion_percentage=72,
        ),
        LibraryEntryCreate(
            user_id=created_users[0]["_id"],
            game_id=created_games[1]["_id"],
            hours_played=61.0,
            status="Completed",
            sentiment_state="Completed",
            sentiment_score=5,
            rating=10.0,
            comment="Finished multiple runs and still returning for more.",
            achievements_unlocked=["The Unseen One", "Master of Arms"],
            completion_percentage=100,
        ),
        LibraryEntryCreate(
            user_id=created_users[1]["_id"],
            game_id=created_games[2]["_id"],
            hours_played=38.0,
            status="Playing",
            sentiment_state="Post-Game-Depression",
            sentiment_score=4,
            rating=9.0,
            comment="Exploring every shrine and side quest.",
            achievements_unlocked=["Skyview Tower", "Great Sky Island"],
            completion_percentage=48,
        ),
        LibraryEntryCreate(
            user_id=created_users[2]["_id"],
            game_id=created_games[3]["_id"],
            hours_played=22.0,
            status="Playing",
            sentiment_state="Rage-Quit",
            sentiment_score=2,
            rating=7.5,
            comment="Kept missing apex corners but the track design is brilliant.",
            achievements_unlocked=["First Lap", "Night Drift"],
            completion_percentage=31,
        ),
        LibraryEntryCreate(
            user_id=created_users[4]["_id"],
            game_id=created_games[4]["_id"],
            hours_played=57.0,
            status="Completed",
            sentiment_state="Completed",
            sentiment_score=5,
            rating=9.1,
            comment="The co-op runs turned chaotic in the best way.",
            achievements_unlocked=["Final Relay", "Squad Anchor"],
            completion_percentage=100,
        ),
        LibraryEntryCreate(
            user_id=created_users[5]["_id"],
            game_id=created_games[5]["_id"],
            hours_played=46.0,
            status="Playing",
            sentiment_state="Playing",
            sentiment_score=4,
            rating=8.8,
            comment="Enjoying the political layer and late-game spell synergies.",
            achievements_unlocked=["First Seal", "Mage Accord"],
            completion_percentage=66,
        ),
        LibraryEntryCreate(
            user_id=created_users[7]["_id"],
            game_id=created_games[6]["_id"],
            hours_played=18.0,
            status="Playing",
            sentiment_state="Post-Game-Depression",
            sentiment_score=4,
            rating=8.9,
            comment="Still thinking about the submerged city weeks later.",
            achievements_unlocked=["Archive Key", "Floodgate Access"],
            completion_percentage=54,
        ),
        LibraryEntryCreate(
            user_id=created_users[8]["_id"],
            game_id=created_games[7]["_id"],
            hours_played=73.0,
            status="Completed",
            sentiment_state="Completed",
            sentiment_score=5,
            rating=9.3,
            comment="Traversal felt incredible once the weapons clicked.",
            achievements_unlocked=["Living Metal", "Covenant Breaker"],
            completion_percentage=100,
        ),
        LibraryEntryCreate(
            user_id=created_users[10]["_id"],
            game_id=created_games[8]["_id"],
            hours_played=29.0,
            status="Playing",
            sentiment_state="Playing",
            sentiment_score=4,
            rating=8.2,
            comment="A relaxing puzzle loop with enough depth to keep me hooked.",
            achievements_unlocked=["First Bloom", "Time Spiral"],
            completion_percentage=42,
        ),
        LibraryEntryCreate(
            user_id=created_users[6]["_id"],
            game_id=created_games[9]["_id"],
            hours_played=14.0,
            status="Playing",
            sentiment_state="Rage-Quit",
            sentiment_score=2,
            rating=7.8,
            comment="The station is terrifying and I keep turning around.",
            achievements_unlocked=["Signal Lock", "Void Hall"],
            completion_percentage=28,
        ),
        LibraryEntryCreate(
            user_id=created_users[9]["_id"],
            game_id=created_games[10]["_id"],
            hours_played=44.0,
            status="Playing",
            sentiment_state="Playing",
            sentiment_score=4,
            rating=8.5,
            comment="The economic layer is as addictive as the combat.",
            achievements_unlocked=["Guild Contract", "Storm Grid"],
            completion_percentage=63,
        ),
    ]

    created_entries = [service.create_library_entry(entry) for entry in sample_entries]

    game_ages = [240, 45, 18, 110, 92, 140, 36, 210, 27, 75, 54, 14]
    entry_ages = [220, 25, 8, 60, 12, 40, 30, 180, 22, 15, 9]

    for game_doc, days_ago in zip(created_games, game_ages):
        _set_game_age(games, game_doc["_id"], days_ago)

    for entry_doc, days_ago in zip(created_entries, entry_ages):
        _set_entry_age(library, entry_doc["_id"], days_ago)

    show_title("GameForge Seed", "Sample data loaded successfully")
    show_panel(
        "Seed Summary",
        [
            f"Users Loaded: {len(created_users)}",
            f"Games Loaded: {len(created_games)}",
            f"Library Entries Loaded: {len(created_entries)}",
            "Dust Demo: Elden Ring entry is intentionally stale.",
            "Lore Demo: multiple shared tags are now seeded across games.",
        ],
    )
    show_message("ready", "Run main.py to open the cyber terminal.")


if __name__ == "__main__":
    seed()