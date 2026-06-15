# routes/library_routes.py
from fastapi import APIRouter, HTTPException, Body, status
from config.database import library_collection, game_collection
from models.game_model import LibraryItemSchema, UpdateLibraryItemSchema
from bson import ObjectId
from typing import List

router = APIRouter()

# Helper translation function mapping BSON to Python Dict formats
def library_helper(item) -> dict:
    return {
        "id": str(item["_id"]),
        "user_id": str(item["user_id"]),
        "game_id": str(item["game_id"]),
        "playtime_hours": item["playtime_hours"],
        "status": item["status"],
        "completion_percentage": item["completion_percentage"],
        "story_progress": item["story_progress"],
        "side_quests_completed": item["side_quests_completed"],
        "achievement_score": item["achievement_score"]
    }

# --- C (CREATE): Add Game to User Library ---
@router.post("/", response_description="Game successfully indexed to library tracking pool", status_code=status.HTTP_201_CREATED)
async def add_game_to_library(item: LibraryItemSchema = Body(...)):
    item_dict = item.dict()
    # Ensure inputs conform to standard BSON string references
    new_item = await library_collection.insert_one(item_dict)
    retrieved = await library_collection.find_one({"_id": new_item.inserted_id})
    return {"status": "Success", "message": "Game added to tracker.", "data": library_helper(retrieved)}

# --- R (READ): List all items in track library ---
@router.get("/{user_id}", response_description="User tracked titles catalog parsed")
async def get_user_library(user_id: str):
    items = []
    async for target in library_collection.find({"user_id": user_id}):
        items.append(library_helper(target))
    return {"status": "Success", "total_tracked": len(items), "data": items}

# --- U (UPDATE): Dynamically modify tracking stats ---
@router.put("/{library_id}", response_description="Tracking data values updated dynamically")
async def update_library_metrics(library_id: str, payload: UpdateLibraryItemSchema = Body(...)):
    clean_update = {k: v for k, v in payload.dict().items() if v is not None}
    
    if len(clean_update) >= 1:
        update_op = await library_collection.update_one(
            {"_id": ObjectId(library_id)}, {"$set": clean_update}
        )
        if update_op.modified_count == 1:
            updated_doc = await library_collection.find_one({"_id": ObjectId(library_id)})
            return {"status": "Success", "updated_data": library_helper(updated_doc)}
            
    raise HTTPException(status_code=404, detail=f"Tracking ID reference target '{library_id}' not found.")

# --- D (DELETE): Drop game completely out of individual tracking array ---
@router.delete("/{library_id}", response_description="Document profile deleted explicitly from database")
async def drop_tracked_game(library_id: str):
    execution = await library_collection.delete_one({"_id": ObjectId(library_id)})
    if execution.deleted_count == 1:
        return {"status": "Success", "message": f"Successfully dropped tracked library entity {library_id}"}
    raise HTTPException(status_code=404, detail="Requested tracker identity not found in systems pool.")

# --- ADVANCED QUERY: Dashboard Statistics Pipeline Engine ---
@router.get("/dashboard/analytics/{user_id}", response_description="Complex dashboard payload metrics synthesized")
async def get_dashboard_analytics(user_id: str):
    """
    Executes a multi-stage aggregation pipeline across collections to calculate core 
    user gaming performance stats instantly.
    """
    pipeline = [
        {"$match": {"user_id": user_id}},
        {
            "$group": {
                "_id": "$user_id",
                "total_playtime": {"$sum": "$playtime_hours"},
                "average_completion": {"$avg": "$completion_percentage"},
                "accumulated_gamer_score": {"$sum": "$achievement_score"},
                "completed_games_count": {
                    "$sum": {"$cond": [{"$eq": ["$status", "Completed"]}, 1, 0]}
                }
            }
        }
    ]
    
    cursor = library_collection.aggregate(pipeline)
    results = await cursor.to_list(length=1)
    
    if not results:
        return {
            "status": "Success",
            "message": "No gaming tracking profile data found for analytical aggregation calculations.",
            "metrics": {"total_playtime": 0, "average_completion": 0, "accumulated_gamer_score": 0, "completed_games_count": 0}
        }
        
    return {"status": "Success", "metrics": results[0]}