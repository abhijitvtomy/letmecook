import json
import os

SAFETY_FILE = os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'safety.json')

_safety_db = {}

def load_safety():
    global _safety_db
    if not os.path.exists(SAFETY_FILE):
        return
    with open(SAFETY_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            _safety_db[item['id']] = item

load_safety()

def get_safety_guidelines(category: str):
    return _safety_db.get(category)

def get_all_guidelines():
    return list(_safety_db.values())

def get_safety_for_ingredients(ingredient_names: list):
    relevant = []
    text = " ".join(ingredient_names).lower()
    
    if any(w in text for w in ['chicken', 'turkey', 'duck', 'poultry']):
        if 'poultry' in _safety_db: relevant.append(_safety_db['poultry'])
    if any(w in text for w in ['beef', 'pork', 'lamb', 'steak', 'meat']):
        if 'red_meat' in _safety_db: relevant.append(_safety_db['red_meat'])
    if any(w in text for w in ['fish', 'salmon', 'shrimp', 'crab', 'seafood']):
        if 'seafood' in _safety_db: relevant.append(_safety_db['seafood'])
    if any(w in text for w in ['egg']):
        if 'eggs' in _safety_db: relevant.append(_safety_db['eggs'])
    if any(w in text for w in ['milk', 'cheese', 'cream', 'butter']):
        if 'dairy' in _safety_db: relevant.append(_safety_db['dairy'])
        
    return relevant
