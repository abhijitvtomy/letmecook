import os
import base64
from google import genai
from google.genai import types
from app.config import GEMINI_API_KEY

def get_api_key():
    for var in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_KEY", "API_KEY"]:
        key = os.getenv(var, "").strip()
        if key and key != "your_gemini_api_key_here":
            return key
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    if os.path.exists(env_path):
        from dotenv import load_dotenv
        load_dotenv(env_path, override=True)
        for var in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_KEY", "API_KEY"]:
            key = os.getenv(var, "").strip()
            if key and key != "your_gemini_api_key_here":
                return key
    return ""

def get_client():
    key = get_api_key()
    if not key:
        raise ValueError("GEMINI_API_KEY is not set")
    return genai.Client(api_key=key)

def chat(message: str, conversation_history: list, recipe_context: str, system_prompt: str) -> str:
    key = get_api_key()
    if not key or key == "your_gemini_api_key_here":
        if recipe_context:
            return (
                "⚠️ **Gemini API Key Missing**: I found the recipe in the database, but your `GEMINI_API_KEY` is not set yet in the environment variables.\n\n"
                "Here is the recipe information from the kitchen database:\n\n" + recipe_context
            )
        return (
            "⚠️ **Gemini API Key Missing**: Please set your `GEMINI_API_KEY` environment variable in your deployment settings to enable AI conversational chat. "
            "In the meantime, you can search and browse all 515 curated recipes using the **Browse Recipes** tab at the top!"
        )

    client = get_client()
    
    contents = []
    for msg in conversation_history:
        role = 'user' if msg.role == 'user' else 'model'
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg.content)]))
        
    contents.append(types.Content(role='user', parts=[types.Part.from_text(text=message)]))

    config = types.GenerateContentConfig(
        system_instruction=system_prompt + "\n\nCONTEXT:\n" + recipe_context,
        temperature=0.3
    )

    # Multi-model pool with high free-tier limits:
    # If one model hits a momentary rate limit, the next one answers instantly!
    MODELS_POOL = [
        'gemini-3.1-flash-lite',
        'gemini-flash-lite-latest',
        'gemini-3.6-flash',
        'gemini-flash-latest'
    ]

    last_error = None
    for model_name in MODELS_POOL:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            return response.text
        except Exception as e:
            last_error = e
            continue

    if recipe_context:
        return f"⚠️ **AI Chat Notice**: ({str(last_error)}).\n\nHere is the verified recipe data from the kitchen database:\n\n{recipe_context}"
    return f"⚠️ **Could not connect to Gemini**: {str(last_error)}. Please ensure your GEMINI_API_KEY is configured in your deployment settings."

def identify_dish(image_base64: str) -> dict:
    client = get_client()
    
    prompt = """
    Identify this food dish. Provide your answer as JSON with these keys:
    - dish_name: the name of the dish
    - confidence: a number from 0 to 100
    - description: what you see
    """
    
    image_bytes = base64.b64decode(image_base64)
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.1
    )
    
    IMAGE_MODELS_POOL = [
        'gemini-3.1-flash-lite',
        'gemini-flash-lite-latest',
        'gemini-3.6-flash',
        'gemini-flash-latest'
    ]
    
    import json
    for model_name in IMAGE_MODELS_POOL:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                    types.Part.from_text(text=prompt)
                ],
                config=config
            )
            data = json.loads(response.text)
            return {
                "dish_name": data.get("dish_name", "Unknown"),
                "confidence": float(data.get("confidence", 0)),
                "description": data.get("description", "")
            }
        except Exception:
            continue

    return {
        "dish_name": "Unknown",
        "confidence": 0.0,
        "description": "Could not identify dish due to rate limit."
    }
