import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import init_db
from app.services.technique_service import load_techniques
from app.services.safety_service import load_safety
from app.routers import chat, recipes, search, image

app = FastAPI(title="LetMeCook API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(image.router, prefix="/api")

@app.on_event("startup")
def on_startup():
    init_db()
    load_techniques()
    load_safety()

@app.get("/health")
def health():
    return {"status": "healthy"}

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    assets_dir = os.path.join(STATIC_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api") or full_path.startswith("health"):
            raise HTTPException(status_code=404, detail="Not Found")
        file_path = os.path.join(STATIC_DIR, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
else:
    @app.get("/")
    def root():
        return {"name": "LetMeCook API", "version": "1.0.0"}
