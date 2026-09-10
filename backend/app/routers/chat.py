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
            
    # Intent detection for finding a recipe
    # Smart recipe detection from database
    if not state["current_recipe_id"]:
        import re
        from app.database import get_all_recipes
        
        # Check all available recipes in DB against user message
        all_recipes = get_all_recipes(page=1, per_page=1000)
        msg_lower = request.message.lower()
        
        # 1. Exact or partial match on name or aliases
        for rec in all_recipes:
            name_lower = rec['name'].lower()
            # If dish name appears in message or message in dish name
            if name_lower in msg_lower or any(word in msg_lower for word in name_lower.split() if len(word) > 3):
                state["current_recipe_id"] = rec['id']
                state["current_step"] = 1
                break
            # Check aliases
            for alias in rec.get('aliases', []):
                if alias.lower() in msg_lower:
                    state["current_recipe_id"] = rec['id']
                    state["current_step"] = 1
                    break
            if state["current_recipe_id"]:
                break
                
        # 2. Fallback to FTS5 search if still not found
        if not state["current_recipe_id"]:
            cleaned = re.sub(
                r'^(how\s+(do|can)\s+i\s+(make|cook|prepare)|recipe\s+for|how\s+to\s+(make|cook|prepare)|show\s+me|tell\s+me\s+how\s+to\s+make)\s+',
                '',
                msg_lower
            )
            cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', cleaned).strip()
            matches = search_recipes(cleaned, limit=1) if cleaned else []
            if not matches:
                matches = search_recipes(request.message, limit=1)
            if matches:
                state["current_recipe_id"] = matches[0]['id']
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
        
    return ChatResponse(
        response=response_text,
        recipe=recipe_data,
        current_step=state["current_step"],
        techniques=None,
        conversation_id=conv_id
    )
