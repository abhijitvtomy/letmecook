from fastapi import APIRouter, Query
from app.services.search_service import search_recipes

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/")
def search(q: str = Query(""), cuisine: str = None, category: str = None, difficulty: str = None, limit: int = 10):
    filters = {"cuisine": cuisine, "category": category, "difficulty": difficulty, "limit": limit}
    filters = {k: v for k, v in filters.items() if v is not None}
    return search_recipes(q, filters)
