import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "data", "recipes.db"))
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
