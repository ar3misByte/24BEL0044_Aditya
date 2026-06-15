# main.py
from fastapi import FastAPI
from routes.library_routes import router as LibraryRouter

app = FastAPI(
    title="GameForge Engine Dashboard",
    description="Asynchronous Backend Engine managing gameplay structures, libraries, and analytics tracking.",
    version="1.1.0"
)

# Connect endpoints safely via clean path namespaces
app.include_router(LibraryRouter, tags=["Library Track Operations & Analytics"], prefix="/library")

@app.get("/", tags=["Diagnostic Base Portal"])
async def environment_root():
    return {
        "engine_status": "ONLINE",
        "message": "Welcome to GameForge Core Systems Engine. Navigate to execution portal route at /docs."
    }