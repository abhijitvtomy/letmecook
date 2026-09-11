import urllib.request
import urllib.parse
import json
import re
import logging

logger = logging.getLogger(__name__)

# In-memory cache for fast responses
_IMAGE_CACHE = {}

# High-resolution, authentic culinary photography for popular foods
COMMON_FOOD_IMAGES = {
    # Eggs & Breakfast
    "scrambled egg": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80",
    "fried egg": "https://images.unsplash.com/photo-1510693206972-df098062cb71?auto=format&fit=crop&w=800&q=80",
    "boiled egg": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/cc/Soft-boiled-egg.jpg/960px-Soft-boiled-egg.jpg?utm_source=en.wikipedia.org&utm_campaign=api&utm_content=thumbnail",
    "poached egg": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/6b/Fog_Eater_Cafe_-_April_2021_-_Sarah_Stierch_06.jpg/960px-Fog_Eater_Cafe_-_April_2021_-_Sarah_Stierch_06.jpg?utm_source=en.wikipedia.org&utm_campaign=api&utm_content=thumbnail",
    "omelette": "https://images.unsplash.com/photo-1510693206972-df098062cb71?auto=format&fit=crop&w=800&q=80",
    "egg": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80",
    "pancake": "https://images.unsplash.com/photo-1528207776546-365bb710ee93?auto=format&fit=crop&w=800&q=80",
    "french toast": "https://images.unsplash.com/photo-1484723091739-30a097e8f929?auto=format&fit=crop&w=800&q=80",
    "waffle": "https://images.unsplash.com/photo-1562376552-0d160a2f238d?auto=format&fit=crop&w=800&q=80",
    "toast": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80",

    # Meats & Mains
    "steak": "https://images.unsplash.com/photo-1600891964599-f61ba0e24092?auto=format&fit=crop&w=800&q=80",
    "ribeye": "https://images.unsplash.com/photo-1600891964599-f61ba0e24092?auto=format&fit=crop&w=800&q=80",
    "beef": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=800&q=80",
    "burger": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80",
    "cheeseburger": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80",
    "chicken wing": "https://images.unsplash.com/photo-1567620832903-9fc6debc209f?auto=format&fit=crop&w=800&q=80",
    "fried chicken": "https://images.unsplash.com/photo-1562967914-608f82629710?auto=format&fit=crop&w=800&q=80",
    "chicken": "https://images.unsplash.com/photo-1532550907401-a500c9a57435?auto=format&fit=crop&w=800&q=80",
    "pork": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",
    "ribs": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",
    "bacon": "https://images.unsplash.com/photo-1528605248644-14dd04022da1?auto=format&fit=crop&w=800&q=80",

    # Italian, Pizza & Pasta
    "pizza": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80",
    "pasta": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=800&q=80",
    "spaghetti": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=800&q=80",
    "carbonara": "https://images.unsplash.com/photo-1612874742237-6526221588e3?auto=format&fit=crop&w=800&q=80",
    "lasagna": "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/ba/Lasagne_-_stonesoup.jpg/960px-Lasagne_-_stonesoup.jpg?utm_source=en.wikipedia.org&utm_campaign=api&utm_content=thumbnail",

    # Asian & Noodles
    "ramen": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80",
    "noodle": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=800&q=80",
    "maggi": "https://images.unsplash.com/photo-1612927601601-6638404737ce?auto=format&fit=crop&w=800&q=80",
    "pad thai": "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=800&q=80",
    "fried rice": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c3/Koh_Mak%2C_Thailand%2C_Fried_rice%2C_Khao_phat.jpg/960px-Koh_Mak%2C_Thailand%2C_Fried_rice%2C_Khao_phat.jpg?utm_source=en.wikipedia.org&utm_campaign=api&utm_content=thumbnail",
    "sushi": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=800&q=80",
    "dumpling": "https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?auto=format&fit=crop&w=800&q=80",

    # Indian & South Asian
    "biryani": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=800&q=80",
    "butter chicken": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?auto=format&fit=crop&w=800&q=80",
    "tikka": "https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?auto=format&fit=crop&w=800&q=80",
    "paneer": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=800&q=80",
    "dal": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=800&q=80",
    "dosa": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?auto=format&fit=crop&w=800&q=80",
    "samosa": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=800&q=80",
    "naan": "https://images.unsplash.com/photo-1626074353765-517a681e40be?auto=format&fit=crop&w=800&q=80",
    "roti": "https://images.unsplash.com/photo-1626074353765-517a681e40be?auto=format&fit=crop&w=800&q=80",
    "paratha": "https://images.unsplash.com/photo-1626074353765-517a681e40be?auto=format&fit=crop&w=800&q=80",
    "curry": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?auto=format&fit=crop&w=800&q=80",

    # Seafood
    "salmon": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=800&q=80",
    "fish": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80",
    "shrimp": "https://images.unsplash.com/photo-1559847844-5315695dadae?auto=format&fit=crop&w=800&q=80",
    "seafood": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=800&q=80",

    # Mexican & Sandwiches
    "taco": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?auto=format&fit=crop&w=800&q=80",
    "burrito": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?auto=format&fit=crop&w=800&q=80",
    "sandwich": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?auto=format&fit=crop&w=800&q=80",
    "grilled cheese": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?auto=format&fit=crop&w=800&q=80",
    "fries": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=800&q=80",

    # Soups & Salads
    "soup": "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=800&q=80",
    "salad": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80",

    # Desserts & Drinks
    "cake": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80",
    "cookie": "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?auto=format&fit=crop&w=800&q=80",
    "dessert": "https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=800&q=80",
    "chai": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=800&q=80",
    "tea": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=800&q=80",
    "coffee": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=800&q=80",

    # Universal Fallback
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

    # 1. Priority: Check curated food images dictionary for exact delicious photo
    for food_key, img_url in sorted(COMMON_FOOD_IMAGES.items(), key=lambda x: len(x[0]), reverse=True):
        if food_key != "default" and food_key in search_key:
            result = (food_key.title(), img_url)
            _IMAGE_CACHE[search_key] = result
            return result

    # 2. Search Wikipedia/Wikimedia for authentic culinary dish photo
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

    # 3. Default high-res culinary presentation fallback
    default_title = search_term.title() if search_term else "Finished Dish"
    result = (default_title, COMMON_FOOD_IMAGES["default"])
    _IMAGE_CACHE[search_key] = result
    return result
