# config/database.py
import sys
from motor.motor_asyncio import AsyncIOMotorClient

# Update this connection string if using MongoDB Atlas cloud cluster
MONGO_DETAILS = "mongodb://localhost:27017"

try:
    client = AsyncIOMotorClient(MONGO_DETAILS)
    database = client.gameforge
    
    # Establish references to specific collections
    user_collection = database.get_collection("users")
    game_collection = database.get_collection("games")
    library_collection = database.get_collection("library")
    
    print("Successfully initialized GameForge MongoDB collections.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    sys.exit(1)