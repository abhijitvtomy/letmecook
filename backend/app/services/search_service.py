from app.database import search_recipes as db_search_recipes, get_db

def search_recipes(query: str, filters: dict = None, limit: int = None):
    filters = filters or {}
    effective_limit = limit if limit is not None else filters.get('limit', 10)
    return db_search_recipes(
        query=query,
        cuisine=filters.get('cuisine'),
        category=filters.get('category'),
        difficulty=filters.get('difficulty'),
        limit=effective_limit
    )

def get_recipes_by_cuisine(cuisine: str):
    return search_recipes("", filters={"cuisine": cuisine, "limit": 50})

def get_recipes_by_category(category: str):
    return search_recipes("", filters={"category": category, "limit": 50})

def suggest_recipes(partial_query: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name FROM recipes 
            WHERE name LIKE ? LIMIT 5
        ''', (f"%{partial_query}%",))
        return [row['name'] for row in cursor.fetchall()]
