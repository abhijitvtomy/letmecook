from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/")
def root():
    return {"name": "LetMeCook API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}
