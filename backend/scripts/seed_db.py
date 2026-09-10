import json
import os
import sys

# Ensure the app module can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import init_db, insert_recipe

SEED_FILE = os.path.join(os.path.dirname(__file__), '..', 'app', 'data', 'seed_recipes.json')

def main():
    print("Initializing database...")
    init_db()
    
    print(f"Loading seed data from {SEED_FILE}...")
    if not os.path.exists(SEED_FILE):
        print(f"Error: {SEED_FILE} not found!")
        sys.exit(1)
        
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        recipes = json.load(f)
        
    print(f"Found {len(recipes)} recipes to seed.")
    
    for r in recipes:
        print(f"Inserting recipe: {r['name']}...")
        insert_recipe(r)
        
    print("Database seeding complete!")

if __name__ == '__main__':
    main()
