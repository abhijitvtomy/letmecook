import json
import os

TECHNIQUES_FILE = os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'techniques.json')

_techniques_db = {}

def load_techniques():
    global _techniques_db
    if not os.path.exists(TECHNIQUES_FILE):
        return
    with open(TECHNIQUES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for tech in data:
            _techniques_db[tech['id']] = tech

load_techniques()

def get_technique(tech_id: str):
    return _techniques_db.get(tech_id)

def get_all_techniques():
    return list(_techniques_db.values())

def search_techniques(query: str):
    query = query.lower()
    results = []
    for tech in _techniques_db.values():
        if query in tech['name'].lower() or query in tech['definition'].lower():
            results.append(tech)
    return results

def get_techniques_for_recipe(technique_ids: list):
    return [get_technique(tid) for tid in technique_ids if tid in _techniques_db]
