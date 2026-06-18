"""MongoDB connection helpers for GameForge."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Tuple

import mongomock
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


DEFAULT_URI = "mongodb://localhost:27017"
DEFAULT_DB_NAME = "gameforge"


@dataclass(frozen=True)
class MongoSettings:
    uri: str = DEFAULT_URI
    db_name: str = DEFAULT_DB_NAME


@lru_cache(maxsize=1)
def get_settings() -> MongoSettings:
    return MongoSettings(
        uri=os.getenv("MONGODB_URI", DEFAULT_URI),
        db_name=os.getenv("MONGODB_DB", DEFAULT_DB_NAME),
    )


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    settings = get_settings()
    allow_mock = os.getenv("MONGODB_ALLOW_MOCK", "1") != "0"

    try:
        client = MongoClient(settings.uri, serverSelectionTimeoutMS=3000, tz_aware=True)
        client.admin.command("ping")
        return client
    except (ConnectionFailure, ServerSelectionTimeoutError):
        if not allow_mock:
            raise
        print(f"MongoDB unavailable at {settings.uri}; using in-memory mongomock for this session.")
        return mongomock.MongoClient()


@lru_cache(maxsize=1)
def get_database() -> Database:
    settings = get_settings()
    return get_client()[settings.db_name]


def get_collections() -> Tuple[Collection, Collection, Collection]:
    database = get_database()
    return database["users"], database["games"], database["library"]


def test_connection() -> None:
    get_client()
