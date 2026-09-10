from app.database import get_recipe_by_id, get_recipe_by_name, get_all_recipes
from app.services.technique_service import get_techniques_for_recipe
import json

def get_recipe(recipe_id: str):
    return get_recipe_by_id(recipe_id)

def get_recipe_by_name_str(name: str):
    return get_recipe_by_name(name)

def list_recipes(page: int = 1, per_page: int = 10, cuisine: str = None, category: str = None):
    # Ignoring filters for simplicity in basic list, relying on search for filters
    return get_all_recipes(page, per_page)

def build_rag_context(recipe: dict, step_number: int = None):
    if not recipe:
        return "No recipe context provided."

    context_lines = [f"Recipe: {recipe.get('name')}"]
    context_lines.append(f"Difficulty: {recipe.get('difficulty')}")
    context_lines.append(f"Total Time: {recipe.get('total_time_minutes')} mins")
    
    context_lines.append("\nIngredients:")
    for ing in recipe.get('ingredients', []):
        substitutes = ", ".join(ing.get('substitutes', []))
        sub_text = f" (Subs: {substitutes})" if substitutes else ""
        context_lines.append(f"- {ing['quantity']} {ing['unit']} {ing['name']}{sub_text}")
    
    context_lines.append("\nSteps:")
    for step in recipe.get('steps', []):
        marker = ">>> CURRENT STEP <<< " if step_number == step.get('step_number') else ""
        context_lines.append(f"{marker}Step {step['step_number']}: {step['instruction']}")
        if step.get('duration_minutes'):
            context_lines.append(f"  Duration: {step['duration_minutes']} mins")
        if step.get('temperature'):
            context_lines.append(f"  Temp: {step['temperature']}")
        if step.get('visual_cue'):
            context_lines.append(f"  Visual Cue: {step['visual_cue']}")

    tech_ids = recipe.get('techniques_referenced', [])
    if tech_ids:
        techniques = get_techniques_for_recipe(tech_ids)
        if techniques:
            context_lines.append("\nSpecial Culinary Techniques (EXPLAIN THESE THOROUGHLY TO THE USER):")
            for t in techniques:
                context_lines.append(f"### Technique: {t['name']}")
                context_lines.append(f"- What it is: {t['definition']}")
                context_lines.append(f"- Why it is done: {t.get('why_its_done', '')}")
                if t.get('how_to'):
                    context_lines.append(f"- How to do it: {'; '.join(t['how_to'])}")
                if t.get('common_mistakes'):
                    context_lines.append(f"- Mistakes to avoid: {'; '.join(t['common_mistakes'])}")

    safety = recipe.get('safety_notes', [])
    if safety:
        context_lines.append("\nSafety Notes:")
        for s in safety:
            context_lines.append(f"- {s}")
            
    return "\n".join(context_lines)
