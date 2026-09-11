from fastapi import APIRouter, HTTPException
from app.models import ChatRequest, ChatResponse, ChatMessage
from app.services.gemini_service import chat as gemini_chat, identify_dish
from app.services.recipe_service import get_recipe, build_rag_context
from app.services.search_service import search_recipes

router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory store: { conversation_id: { "history": [...], "current_recipe_id": str, "current_step": int } }
_conversations = {}

SYSTEM_PROMPT = """You are LetMeCook, a strict and precise AI master cooking assistant. Your mission is to provide accurate, reliable, step-by-step recipes and answer culinary questions without guessing.

Follow these rules with absolute discipline:

1. **STRUCTURED & EXPLICIT STEPS**:
   - Provide each necessary step numbered clearly and explicitly.
   - For every step, specify:
     * **Action**: Exactly what to do in clear, direct language.
     * **Exact Time/Duration**: (e.g. "Cook for 8–10 minutes", "Marinate for 30 minutes"). Never write vague phrases like "cook until done".
     * **Heat Level / Temperature**: (e.g. "Medium-high heat (~375°F / 190°C)").
     * **Visual Cue**: Explicit physical indication that the step is finished (e.g. "The onions become deep golden brown with crispy edges, not burnt").

2. **SPECIAL COOKING TECHNIQUES (MANDATORY)**:
   - If any specialized technique is involved (e.g. Double boiling, Dum cooking, Searing, Deglazing, Blanching, Tempering/Tadka, Emulsification):
     * Explain **WHAT IT IS**: Define the technique in plain language.
     * Explain **WHY IT IS DONE**: The culinary science/purpose (e.g. "Prevents chocolate from scorching by providing indirect, gentle steam heat").
     * Explain **HOW TO PERFORM IT PROPERLY**: Key steps and common mistakes to avoid.

3. **CONVERSATIONAL Q&A & FOLLOW-UPS**:
   - Answer ANY follow-up question the user asks about the dish (substitutions, scaling, fixing mistakes like too much salt, equipment alternatives, storage, reheating).
   - Relate answers directly to the active recipe context.

4. **FOOD SAFETY FIRST**:
   - Always state crucial safety notes (e.g. safe internal meat temperatures such as 165°F / 74°C for chicken, cross-contamination warnings, hot oil safety).

5. **SOURCE OF TRUTH**:
   - Use the provided recipe database context as the primary source of truth. If the user asks for a recipe that is not in the database, you can formulate a strict, professional recipe using the same rigorous format, but explicitly note it is generated from culinary best practices.
"""

@router.post("", response_model=ChatResponse)
@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    conv_id = request.conversation_id
    if conv_id not in _conversations:
        _conversations[conv_id] = {"history": [], "current_recipe_id": None, "current_step": None}
        
    state = _conversations[conv_id]
    
    # Process Image if provided
    if request.image_base64:
        dish_info = identify_dish(request.image_base64)
        dish_name = dish_info['dish_name']
        matches = search_recipes(dish_name, limit=1)
        if matches:
            state["current_recipe_id"] = matches[0]['id']
            state["current_step"] = 1
            request.message = f"I uploaded an image of {dish_name}. " + request.message
            
    # Smart dish / recipe detection from user message
    msg_lower = request.message.lower()
    import re
    from app.database import get_all_recipes
    
    matched_id = None
    all_recipes = get_all_recipes(page=1, per_page=1000)
    # Sort recipes by title length descending so specific dishes match before short generic ones
    sorted_recipes = sorted(all_recipes, key=lambda r: len(r['name']), reverse=True)
    
    # Priority 1: Exact dish name or alias in user message (e.g. "pad thai", "chicken biryani")
    for rec in sorted_recipes:
        rec_name_lower = rec['name'].lower()
        if len(rec_name_lower) >= 4 and rec_name_lower in msg_lower:
            matched_id = rec['id']
            break
        for alias in rec.get('aliases', []):
            if len(alias) >= 4 and alias.lower() in msg_lower:
                matched_id = rec['id']
                break
        if matched_id:
            break
            
    # Priority 2: Keyword search with stop words removed
    if not matched_id:
        STOP_WORDS = {
            "how", "do", "can", "i", "make", "cook", "prepare", "recipe", "for", "the", "a", "an",
            "to", "of", "and", "in", "with", "on", "at", "by", "from", "up", "about", "into", "over",
            "after", "what", "is", "are", "was", "were", "tell", "show", "me", "give", "want", "please",
            "help", "hello", "hi", "hey", "good", "morning", "evening", "thanks", "thank", "you",
            "steps", "time", "temperature", "heat", "duration", "next", "step", "first", "last",
            "actually", "switch", "let", "us", "now", "instead", "another", "one"
        }
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', msg_lower).strip()
        words = [w for w in cleaned.split() if w not in STOP_WORDS and len(w) > 2]
        if words:
            for w in words:
                matches = search_recipes(w, limit=1)
                if matches and any(w in matches[0]['name'].lower() for w in words):
                    matched_id = matches[0]['id']
                    break
                    
    if matched_id:
        state["current_recipe_id"] = matched_id
        state["current_step"] = 1

    # RAG Context
    recipe_context = ""
    recipe_data = None
    if state["current_recipe_id"]:
        recipe_data = get_recipe(state["current_recipe_id"])
        recipe_context = build_rag_context(recipe_data, state["current_step"])
        
    response_text = gemini_chat(
        message=request.message,
        conversation_history=state["history"],
        recipe_context=recipe_context,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Update History
    state["history"].append(ChatMessage(role='user', content=request.message))
    state["history"].append(ChatMessage(role='assistant', content=response_text))
    
    # Prevent history from growing unbounded
    if len(state["history"]) > 20:
        state["history"] = state["history"][-20:]
        
    COMMON_FOOD_IMAGES = {
        "egg": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80",
        "scrambled": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80",
        "omelette": "https://images.unsplash.com/photo-1510693206972-df098062cb71?auto=format&fit=crop&w=800&q=80",
        "steak": "https://images.unsplash.com/photo-1600891964599-f61ba0e24092?auto=format&fit=crop&w=800&q=80",
        "beef": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=800&q=80",
        "pizza": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80",
        "burger": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80",
        "soup": "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80",
        "salad": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80",
        "cake": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80",
        "dessert": "https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=800&q=80",
        "pancake": "https://images.unsplash.com/photo-1528207776546-365bb710ee93?auto=format&fit=crop&w=800&q=80",
        "waffle": "https://images.unsplash.com/photo-1562376552-0d160a2f238d?auto=format&fit=crop&w=800&q=80",
        "french toast": "https://images.unsplash.com/photo-1484723091739-30a097e8f929?auto=format&fit=crop&w=800&q=80",
        "toast": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80",
        "cookie": "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?auto=format&fit=crop&w=800&q=80",
        "pasta": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=800&q=80",
        "spaghetti": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=800&q=80",
        "noodle": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80",
        "ramen": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80",
        "curry": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?auto=format&fit=crop&w=800&q=80",
        "chicken": "https://images.unsplash.com/photo-1532550907401-a500c9a57435?auto=format&fit=crop&w=800&q=80",
        "fish": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80",
        "salmon": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=800&q=80",
        "seafood": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=800&q=80",
        "shrimp": "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=800&q=80",
        "pork": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",
        "ribs": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",
        "bacon": "https://images.unsplash.com/photo-1528605248644-14dd04022da1?auto=format&fit=crop&w=800&q=80",
        "taco": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?auto=format&fit=crop&w=800&q=80",
        "burrito": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?auto=format&fit=crop&w=800&q=80",
        "sandwich": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?auto=format&fit=crop&w=800&q=80",
        "sushi": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=800&q=80",
        "rice": "https://images.unsplash.com/photo-1516684732162-798a0062be99?auto=format&fit=crop&w=800&q=80",
        "bread": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=800&q=80",
        "fries": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=800&q=80",
        "potato": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=800&q=80",
        "cheese": "https://images.unsplash.com/photo-1543339308-43e59d6b73a6?auto=format&fit=crop&w=800&q=80",
        "pie": "https://images.unsplash.com/photo-1519915028121-7d346b40656a?auto=format&fit=crop&w=800&q=80",
    }

    dish_image_url = recipe_data.get('image_url') if isinstance(recipe_data, dict) else getattr(recipe_data, 'image_url', None)
    
    # If no database image, match against common food terms from the conversation
    if not dish_image_url:
        combined_text = (request.message + " " + response_text[:300]).lower()
        for food_term, img_url in COMMON_FOOD_IMAGES.items():
            if food_term in combined_text:
                dish_image_url = img_url
                break

    # If the chatbot is discussing a recipe, cooking, or food, always provide a high-res photo
    COOKING_KEYWORDS = [
        "step 1", "step 2", "ingredients", "instructions", "recipe", "heat", "cook", "pan", "skillet",
        "pot", "bake", "fry", "boil", "simmer", "minutes", "servings", "tablespoon", "teaspoon", "cup",
        "season", "salt", "pepper", "oil", "butter", "garlic", "onion", "dish", "meal", "food", "kitchen"
    ]
    is_cooking_response = any(w in response_text.lower() for w in COOKING_KEYWORDS) or any(w in request.message.lower() for w in ["cook", "recipe", "make", "how", "prepare", "dish", "food", "eat"])
    if not dish_image_url and is_cooking_response:
        dish_image_url = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80"

    # Embed finished dish photo directly at the end of the chatbot markdown text
    if dish_image_url and ("![" not in response_text):
        dish_title = None
        if recipe_data:
            dish_title = recipe_data.get('name') if isinstance(recipe_data, dict) else getattr(recipe_data, 'name', None)
        if not dish_title:
            combined = (request.message + " " + response_text[:200]).lower()
            for term in COMMON_FOOD_IMAGES.keys():
                if term in combined:
                    dish_title = term.title()
                    break
        if not dish_title:
            dish_title = "Finished Dish"
        response_text += f"\n\n---\n\n### 🍽️ {dish_title} — Finished Presentation\n\n![{dish_title}]({dish_image_url})\n"

    return ChatResponse(
        response=response_text,
        recipe=recipe_data,
        image_url=dish_image_url,
        current_step=state["current_step"],
        techniques=None,
        conversation_id=conv_id
    )
