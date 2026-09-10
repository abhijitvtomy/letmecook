from fastapi import APIRouter
from pydantic import BaseModel
from app.models import ImageIdentifyResponse
from app.services.gemini_service import identify_dish
from app.services.search_service import search_recipes

router = APIRouter(prefix="/image", tags=["image"])

class ImageRequest(BaseModel):
    image_base64: str

@router.post("/identify", response_model=ImageIdentifyResponse)
def identify(request: ImageRequest):
    dish_info = identify_dish(request.image_base64)
    dish_name = dish_info.get("dish_name", "")
    
    recipe_id = None
    if dish_name and dish_name != "Unknown":
        matches = search_recipes(dish_name, filters={"limit": 1})
        if matches:
            recipe_id = matches[0]['id']
            
    return ImageIdentifyResponse(
        dish_name=dish_name,
        confidence=dish_info.get("confidence", 0.0),
        recipe_id=recipe_id,
        message=dish_info.get("description", "")
    )
