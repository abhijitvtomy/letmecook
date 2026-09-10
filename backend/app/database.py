import sqlite3
import json
import os
from contextlib import contextmanager
from app.config import DATABASE_PATH

def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Create recipes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id TEXT PRIMARY KEY,
                name TEXT,
                aliases TEXT,
                cuisine TEXT,
                category TEXT,
                sub_category TEXT,
                difficulty TEXT,
                servings INTEGER,
                prep_time_minutes INTEGER,
                cook_time_minutes INTEGER,
                total_time_minutes INTEGER,
                dietary_tags TEXT,
                ingredients TEXT,
                steps TEXT,
                techniques_referenced TEXT,
                nutrition_per_serving TEXT,
                safety_notes TEXT,
                source TEXT,
                image_url TEXT
            )
        ''')
        
        # Create FTS5 virtual table
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS recipes_fts USING fts5(
                name,
                aliases,
                cuisine,
                category,
                ingredients_text,
                content='recipes',
                content_rowid='rowid'
            )
        ''')
        conn.commit()

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def insert_recipe(recipe_dict):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO recipes (
                id, name, aliases, cuisine, category, sub_category, difficulty, servings, 
                prep_time_minutes, cook_time_minutes, total_time_minutes, dietary_tags, 
                ingredients, steps, techniques_referenced, nutrition_per_serving, 
                safety_notes, source, image_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            recipe_dict.get('id'),
            recipe_dict.get('name'),
            json.dumps(recipe_dict.get('aliases', [])),
            recipe_dict.get('cuisine'),
            recipe_dict.get('category'),
            recipe_dict.get('sub_category'),
            recipe_dict.get('difficulty'),
            recipe_dict.get('servings'),
            recipe_dict.get('prep_time_minutes'),
            recipe_dict.get('cook_time_minutes'),
            recipe_dict.get('total_time_minutes'),
            json.dumps(recipe_dict.get('dietary_tags', [])),
            json.dumps(recipe_dict.get('ingredients', [])),
            json.dumps(recipe_dict.get('steps', [])),
            json.dumps(recipe_dict.get('techniques_referenced', [])),
            json.dumps(recipe_dict.get('nutrition_per_serving', {})),
            json.dumps(recipe_dict.get('safety_notes', [])),
            recipe_dict.get('source'),
            recipe_dict.get('image_url')
        ))
        
        # Extract ingredients for FTS
        ingredients_text = " ".join([i.get("name", "") for i in recipe_dict.get('ingredients', [])])
        
        # Update FTS5 table
        cursor.execute('''
            INSERT INTO recipes_fts(rowid, name, aliases, cuisine, category, ingredients_text)
            VALUES (last_insert_rowid(), ?, ?, ?, ?, ?)
        ''', (
            recipe_dict.get('name'),
            json.dumps(recipe_dict.get('aliases', [])),
            recipe_dict.get('cuisine'),
            recipe_dict.get('category'),
            ingredients_text
        ))
        conn.commit()

def _parse_recipe_row(row):
    if not row:
        return None
    recipe = dict(row)
    for field in ['aliases', 'dietary_tags', 'ingredients', 'steps', 'techniques_referenced', 'nutrition_per_serving', 'safety_notes']:
        if recipe[field]:
            recipe[field] = json.loads(recipe[field])
        else:
            recipe[field] = [] if field != 'nutrition_per_serving' else None
    return recipe

def get_recipe_by_id(recipe_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
        return _parse_recipe_row(cursor.fetchone())

def get_recipe_by_name(name):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recipes WHERE name LIKE ?", (f"%{name}%",))
        return _parse_recipe_row(cursor.fetchone())

def search_recipes(query, cuisine=None, category=None, difficulty=None, limit=10):
    with get_db() as conn:
        cursor = conn.cursor()
        
        sql = """
            SELECT r.*, rank as match_score
            FROM recipes_fts f
            JOIN recipes r ON r.rowid = f.rowid
        """
        params = []
        conditions = []
        
        if query:
            import re
            cleaned_query = re.sub(r'[^a-zA-Z0-9\s]', ' ', query).strip()
            if cleaned_query:
                # Use prefix matching on each word for flexible search
                terms = [f'"{term}"*' for term in cleaned_query.split() if term]
                conditions.append("recipes_fts MATCH ?")
                params.append(" ".join(terms))
            
        if cuisine:
            conditions.append("r.cuisine = ?")
            params.append(cuisine)
            
        if category:
            conditions.append("r.category = ?")
            params.append(category)
            
        if difficulty:
            conditions.append("r.difficulty = ?")
            params.append(difficulty)
            
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
            
        sql += " ORDER BY match_score LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()
        return [_parse_recipe_row(row) for row in rows]

def get_all_recipes(page=1, per_page=10):
    offset = (page - 1) * per_page
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recipes LIMIT ? OFFSET ?", (per_page, offset))
        return [_parse_recipe_row(row) for row in cursor.fetchall()]
