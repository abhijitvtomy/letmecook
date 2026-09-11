import urllib.request
import urllib.parse
import json
import re
import logging

logger = logging.getLogger(__name__)

# In-memory cache for fast responses
_IMAGE_CACHE = {}

# High-resolution Unsplash backups for common food categories
COMMON_FOOD_IMAGES = {
    "scrambled egg": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80",
    "fried egg": "https://images.unsplash.com/photo-1510693206972-df098062cb71?auto=format&fit=crop&w=800&q=80",
    "omelette": "https://images.unsplash.com/photo-1510693206972-df098062cb71?auto=format&fit=crop&w=800&q=80",
    "egg": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80",
    "steak": "https://images.unsplash.com/photo-1600891964599-f61ba0e24092?auto=format&fit=crop&w=800&q=80",
    "beef": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=800&q=80",
    "pizza": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80",
    "burger": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80",
    "soup": "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80",
    "salad": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80",
    "cake": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80",
    "pancake": "https://images.unsplash.com/photo-1528207776546-365bb710ee93?auto=format&fit=crop&w=800&q=80",
    "french toast": "https://images.unsplash.com/photo-1484723091739-30a097e8f929?auto=format&fit=crop&w=800&q=80",
    "waffle": "https://images.unsplash.com/photo-1562376552-0d160a2f238d?auto=format&fit=crop&w=800&q=80",
    "cookie": "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?auto=format&fit=crop&w=800&q=80",
    "pasta": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=800&q=80",
    "ramen": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80",
    "noodle": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80",
    "curry": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?auto=format&fit=crop&w=800&q=80",
    "chicken": "https://images.unsplash.com/photo-1532550907401-a500c9a57435?auto=format&fit=crop&w=800&q=80",
    "salmon": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=800&q=80",
    "fish": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80",
    "seafood": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=800&q=80",
    "shrimp": "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=800&q=80",
    "taco": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?auto=format&fit=crop&w=800&q=80",
    "sandwich": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?auto=format&fit=crop&w=800&q=80",
    "sushi": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=800&q=80",
    "rice": "https://images.unsplash.com/photo-1516684732162-798a0062be99?auto=format&fit=crop&w=800&q=80",
    "bread": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=800&q=80",
    "toast": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80",
    "fries": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=800&q=80",
    "potato": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=800&q=80",
    "default": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80"
}

def clean_dish_query(query: str) -> str:
    """Extracts the core culinary dish name from user prompt."""
    STOP_PATTERNS = [
        r'(?i)\b(how|to|make|cook|prepare|recipe|for|the|a|an|can|i|do|best|easy|delicious|homemade)\b',
        r'(?i)\b(please|give|me|steps|instructions|authentic|guide|want|would|like|teach|show)\b',
        r'(?i)\b(simple|quick|traditional|perfect|secret|today|tonight|dinner|lunch|breakfast)\b'
    ]
    cleaned = query
    for pat in STOP_PATTERNS:
        cleaned = re.sub(pat, ' ', cleaned)
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', cleaned).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned if len(cleaned) >= 3 else query.strip()

def fetch_dish_image(dish_or_query: str, known_dish_name: str = None) -> tuple[str, str]:
    """
    Finds a verified, high-accuracy photograph of the dish.
    Returns: (dish_title, image_url)
    """
    search_term = known_dish_name or clean_dish_query(dish_or_query)
    search_key = search_term.lower().strip()

    if search_key in _IMAGE_CACHE:
        return _IMAGE_CACHE[search_key]

    # 1. Search Wikipedia/Wikimedia for authentic culinary dish photo
    try:
        url = (
            f"https://en.wikipedia.org/w/api.php?action=query&format=json"
            f"&prop=pageimages&piprop=thumbnail&pithumbsize=800&generator=search"
            f"&gsrsearch={urllib.parse.quote(search_term)}&gsrlimit=4"
        )
        req = urllib.request.Request(url, headers={'User-Agent': 'LetMeCook-CookingAssistant/1.0 (culinary@letmecook.app)'})
        with urllib.request.urlopen(req, timeout=2.5) as r:
            data = json.loads(r.read().decode())
            pages = data.get('query', {}).get('pages', {})
            sorted_pages = sorted(pages.values(), key=lambda p: p.get('index', 99))
            for page in sorted_pages:
                thumb = page.get('thumbnail', {}).get('source')
                title = page.get('title')
                if thumb and not thumb.lower().endswith('.svg.png') and '.svg' not in thumb.lower():
                    result = (title or search_term.title(), thumb)
                    _IMAGE_CACHE[search_key] = result
                    return result
    except Exception as e:
        logger.warning(f"Wikipedia image search failed for '{search_term}': {e}")

    # 2. Check curated food images dictionary
    term_lower = search_term.lower()
    for food_key, img_url in COMMON_FOOD_IMAGES.items():
        if food_key in term_lower:
            result = (food_key.title(), img_url)
            _IMAGE_CACHE[search_key] = result
            return result

    # 3. Default high-res culinary presentation fallback
    default_title = search_term.title() if search_term else "Finished Dish"
    result = (default_title, COMMON_FOOD_IMAGES["default"])
    _IMAGE_CACHE[search_key] = result
    return result
