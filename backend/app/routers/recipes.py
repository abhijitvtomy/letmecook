from fastapi import APIRouter, Query, HTTPException
from app.services.recipe_service import list_recipes, get_recipe

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.get("/")
def get_recipes(page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100), cuisine: str = None, category: str = None, difficulty: str = None):
    # Pass filters downstream if DB logic handles it; else simple list
    return list_recipes(page, per_page, cuisine, category)

@router.get("/{recipe_id}")
def get_recipe_by_id(recipe_id: str):
    recipe = get_recipe(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe
