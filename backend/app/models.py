from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field

class Ingredient(BaseModel):
    name: str
    quantity: float
    unit: str
    category: str
    substitutes: List[str] = Field(default_factory=list)
    prep_note: Optional[str] = None

class RecipeStep(BaseModel):
    step_number: int
    phase: str
    instruction: str
    duration_minutes: Optional[int] = None
    wait_time_minutes: Optional[int] = None
    temperature: Optional[str] = None
    heat_level: Optional[str] = None
    visual_cue: Optional[str] = None
    equipment: List[str] = Field(default_factory=list)
    techniques_used: List[str] = Field(default_factory=list)
    tips: Optional[str] = None
    common_mistakes: List[str] = Field(default_factory=list)

class NutritionInfo(BaseModel):
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None

class Recipe(BaseModel):
    id: str
    name: str
    aliases: List[str] = Field(default_factory=list)
    cuisine: str
    category: str
    sub_category: str
    difficulty: str
    servings: int
    prep_time_minutes: int
    cook_time_minutes: int
    total_time_minutes: int
    dietary_tags: List[str] = Field(default_factory=list)
    ingredients: List[Ingredient] = Field(default_factory=list)
    steps: List[RecipeStep] = Field(default_factory=list)
    techniques_referenced: List[str] = Field(default_factory=list)
    nutrition_per_serving: Optional[NutritionInfo] = None
    safety_notes: List[str] = Field(default_factory=list)
    source: Optional[str] = None
    image_url: Optional[str] = None

class Technique(BaseModel):
    id: str
    name: str
    definition: str
    how_to: List[str] = Field(default_factory=list)
    why_its_done: str
    common_mistakes: List[str] = Field(default_factory=list)
    used_in: List[str] = Field(default_factory=list)
    related_techniques: List[str] = Field(default_factory=list)

class SafetyGuideline(BaseModel):
    id: str
    category: str
    title: str
    guidelines: List[str] = Field(default_factory=list)
    critical_temperatures: Optional[Dict[str, str]] = None

class ChatMessage(BaseModel):
    role: Literal['user', 'assistant']
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: str
    image_base64: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    recipe: Optional[Recipe] = None
    current_step: Optional[int] = None
    techniques: Optional[List[Technique]] = None
    conversation_id: str

class SearchResult(BaseModel):
    recipe_id: str
    name: str
    cuisine: str
    category: str
    difficulty: str
    total_time_minutes: int
    match_score: float

class ImageIdentifyResponse(BaseModel):
    dish_name: str
    confidence: float
    recipe_id: Optional[str] = None
    message: str
