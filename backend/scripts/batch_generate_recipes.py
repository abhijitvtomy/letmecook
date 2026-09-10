"""
Batch Recipe Generator for LetMeCook
Generates strict, structured, technique-aware recipes using Gemini 3.6 Flash
and seeds them directly into SQLite.
"""

import os
import sys
import json
import time
import sqlite3
from dotenv import load_dotenv

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

load_dotenv(os.path.join(ROOT_DIR, '.env'))

from google import genai
from google.genai import types
from app.database import get_db, insert_recipe

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in .env")

client = genai.Client(api_key=API_KEY)

# 300 of the Most Famous and Searched Global Recipes
TOP_300_DISHES = [
    # Indian (45)
    ("Chicken Biryani", "Indian", "Main Course"),
    ("Butter Chicken", "Indian", "Main Course"),
    ("Paneer Butter Masala", "Indian", "Main Course"),
    ("Dal Makhani", "Indian", "Main Course"),
    ("Palak Paneer", "Indian", "Main Course"),
    ("Chole Bhature", "Indian", "Main Course"),
    ("Rogan Josh", "Indian", "Main Course"),
    ("Chicken Tikka Masala", "Indian", "Main Course"),
    ("Masala Dosa", "Indian", "Breakfast"),
    ("Idli Sambar", "Indian", "Breakfast"),
    ("Mutton Biryani", "Indian", "Main Course"),
    ("Fish Curry (Goan)", "Indian", "Main Course"),
    ("Samosa", "Indian", "Snack"),
    ("Aloo Gobi", "Indian", "Main Course"),
    ("Tandoori Chicken", "Indian", "Main Course"),
    ("Pani Puri", "Indian", "Snack"),
    ("Pav Bhaji", "Indian", "Snack"),
    ("Gulab Jamun", "Indian", "Dessert"),
    ("Rasgulla", "Indian", "Dessert"),
    ("Jalebi", "Indian", "Dessert"),
    ("Korma (Chicken)", "Indian", "Main Course"),
    ("Vada Pav", "Indian", "Snack"),
    ("Rajma Chawal", "Indian", "Main Course"),
    ("Chicken 65", "Indian", "Appetizer"),
    ("Prawn Malai Curry", "Indian", "Main Course"),
    ("Dhokla", "Indian", "Snack"),
    ("Upma", "Indian", "Breakfast"),
    ("Poha", "Indian", "Breakfast"),
    ("Dal Tadka", "Indian", "Main Course"),
    ("Baingan Bharta", "Indian", "Main Course"),
    ("Kadhai Paneer", "Indian", "Main Course"),
    ("Hyderabadi Biryani", "Indian", "Main Course"),
    ("Malai Kofta", "Indian", "Main Course"),
    ("Keema Matar", "Indian", "Main Course"),
    ("Gajar Ka Halwa", "Indian", "Dessert"),
    ("Kheer", "Indian", "Dessert"),
    ("Chicken Chettinad", "Indian", "Main Course"),
    ("Medu Vada", "Indian", "Breakfast"),
    ("Aloo Paratha", "Indian", "Breakfast"),
    ("Bhel Puri", "Indian", "Snack"),
    ("Shahi Paneer", "Indian", "Main Course"),
    ("Egg Curry", "Indian", "Main Course"),
    ("Chicken Kebab", "Indian", "Appetizer"),
    ("Mysore Pak", "Indian", "Dessert"),
    ("Bhindi Masala", "Indian", "Main Course"),

    # Italian (35)
    ("Pasta Carbonara", "Italian", "Main Course"),
    ("Margherita Pizza", "Italian", "Main Course"),
    ("Lasagna Bolognese", "Italian", "Main Course"),
    ("Spaghetti Bolognese", "Italian", "Main Course"),
    ("Fettuccine Alfredo", "Italian", "Main Course"),
    ("Risotto alla Milanese", "Italian", "Main Course"),
    ("Tiramisu", "Italian", "Dessert"),
    ("Panna Cotta", "Italian", "Dessert"),
    ("Bruschetta al Pomodoro", "Italian", "Appetizer"),
    ("Cacio e Pepe", "Italian", "Main Course"),
    ("Penne all'Arrabbiata", "Italian", "Main Course"),
    ("Osso Buco", "Italian", "Main Course"),
    ("Minestrone Soup", "Italian", "Soup"),
    ("Gnocchi Sorrentina", "Italian", "Main Course"),
    ("Chicken Parmesan", "Italian", "Main Course"),
    ("Eggplant Parmigiana", "Italian", "Main Course"),
    ("Focaccia Bread", "Italian", "Baking"),
    ("Arancini", "Italian", "Snack"),
    ("Calzone", "Italian", "Main Course"),
    ("Carpaccio", "Italian", "Appetizer"),
    ("Seafood Risotto", "Italian", "Main Course"),
    ("Pesto Genovese Pasta", "Italian", "Main Course"),
    ("Cannoli Siciliani", "Italian", "Dessert"),
    ("Affogato al Caffe", "Italian", "Dessert"),
    ("Polenta with Mushrooms", "Italian", "Main Course"),
    ("Spaghetti alle Vongole", "Italian", "Main Course"),
    ("Bistecca alla Fiorentina", "Italian", "Main Course"),
    ("Panzanella Salad", "Italian", "Salad"),
    ("Caprese Salad", "Italian", "Salad"),
    ("Ravioli Ricotta and Spinach", "Italian", "Main Course"),
    ("Saltimbocca alla Romana", "Italian", "Main Course"),
    ("Ribollita", "Italian", "Soup"),
    ("Zuppa Toscana", "Italian", "Soup"),
    ("Tortellini in Brodo", "Italian", "Soup"),
    ("Ciabatta", "Italian", "Baking"),

    # Chinese (30)
    ("Kung Pao Chicken", "Chinese", "Main Course"),
    ("Mapo Tofu", "Chinese", "Main Course"),
    ("Peking Duck", "Chinese", "Main Course"),
    ("Sweet and Sour Pork", "Chinese", "Main Course"),
    ("Dim Sum Pork Dumplings", "Chinese", "Appetizer"),
    ("Chow Mein", "Chinese", "Main Course"),
    ("Yangzhou Fried Rice", "Chinese", "Main Course"),
    ("Hot and Sour Soup", "Chinese", "Soup"),
    ("Wonton Soup", "Chinese", "Soup"),
    ("Spring Rolls", "Chinese", "Snack"),
    ("General Tso's Chicken", "Chinese", "Main Course"),
    ("Beef with Broccoli", "Chinese", "Main Course"),
    ("Dan Dan Noodles", "Chinese", "Main Course"),
    ("Char Siu Pork", "Chinese", "Main Course"),
    ("Baozi (Steamed Buns)", "Chinese", "Snack"),
    ("Egg Fried Rice", "Chinese", "Main Course"),
    ("Szechuan Beef", "Chinese", "Main Course"),
    ("Scallion Pancakes", "Chinese", "Breakfast"),
    ("Egg Drop Soup", "Chinese", "Soup"),
    ("Hainanese Chicken Rice", "Chinese", "Main Course"),
    ("Mongolian Beef", "Chinese", "Main Course"),
    ("Honey Walnut Shrimp", "Chinese", "Main Course"),
    ("Sesame Chicken", "Chinese", "Main Course"),
    ("Orange Chicken", "Chinese", "Main Course"),
    ("Mooncakes", "Chinese", "Dessert"),
    ("Tanghulu", "Chinese", "Dessert"),
    ("Lo Mein", "Chinese", "Main Course"),
    ("Twice-Cooked Pork", "Chinese", "Main Course"),
    ("Salt and Pepper Squid", "Chinese", "Appetizer"),
    ("Congee", "Chinese", "Breakfast"),

    # Japanese (25)
    ("Chicken Ramen", "Japanese", "Main Course"),
    ("Sushi California Roll", "Japanese", "Main Course"),
    ("Chicken Katsu Curry", "Japanese", "Main Course"),
    ("Tempura Shrimp", "Japanese", "Appetizer"),
    ("Miso Soup", "Japanese", "Soup"),
    ("Okonomiyaki", "Japanese", "Main Course"),
    ("Takoyaki", "Japanese", "Snack"),
    ("Yakitori", "Japanese", "Appetizer"),
    ("Tonkatsu", "Japanese", "Main Course"),
    ("Gyoza", "Japanese", "Appetizer"),
    ("Beef Teriyaki", "Japanese", "Main Course"),
    ("Udon Noodle Soup", "Japanese", "Main Course"),
    ("Gyudon (Beef Bowl)", "Japanese", "Main Course"),
    ("Oyakodon", "Japanese", "Main Course"),
    ("Matcha Green Tea Ice Cream", "Japanese", "Dessert"),
    ("Mochi", "Japanese", "Dessert"),
    ("Soba Noodles with Dashi", "Japanese", "Main Course"),
    ("Tamagoyaki", "Japanese", "Breakfast"),
    ("Dorayaki", "Japanese", "Dessert"),
    ("Chashu Pork", "Japanese", "Main Course"),
    ("Karaage (Fried Chicken)", "Japanese", "Appetizer"),
    ("Agedashi Tofu", "Japanese", "Appetizer"),
    ("Chawanmushi", "Japanese", "Appetizer"),
    ("Sukiyaki", "Japanese", "Main Course"),
    ("Onigiri", "Japanese", "Snack"),

    # Mexican (25)
    ("Carne Asada Tacos", "Mexican", "Main Course"),
    ("Guacamole", "Mexican", "Appetizer"),
    ("Chicken Enchiladas", "Mexican", "Main Course"),
    ("Beef Burrito", "Mexican", "Main Course"),
    ("Quesadilla", "Mexican", "Main Course"),
    ("Chiles Rellenos", "Mexican", "Main Course"),
    ("Carnitas", "Mexican", "Main Course"),
    ("Churros with Chocolate", "Mexican", "Dessert"),
    ("Pozole Verde", "Mexican", "Soup"),
    ("Tamales (Chicken)", "Mexican", "Main Course"),
    ("Fajitas (Steak and Peppers)", "Mexican", "Main Course"),
    ("Tortilla Soup", "Mexican", "Soup"),
    ("Elote (Mexican Street Corn)", "Mexican", "Snack"),
    ("Birria Tacos with Consomé", "Mexican", "Main Course"),
    ("Tres Leches Cake", "Mexican", "Dessert"),
    ("Huevos Rancheros", "Mexican", "Breakfast"),
    ("Pico de Gallo", "Mexican", "Appetizer"),
    ("Mole Poblano", "Mexican", "Main Course"),
    ("Fish Tacos", "Mexican", "Main Course"),
    ("Al Pastor Tacos", "Mexican", "Main Course"),
    ("Salsa Verde", "Mexican", "Condiment"),
    ("Chilaquiles", "Mexican", "Breakfast"),
    ("Nachos Supreme", "Mexican", "Snack"),
    ("Tostadas", "Mexican", "Main Course"),
    ("Flan", "Mexican", "Dessert"),

    # American & Western (35)
    ("Classic Cheeseburger", "American", "Main Course"),
    ("Macaroni and Cheese", "American", "Main Course"),
    ("Buffalo Wings", "American", "Appetizer"),
    ("BBQ Ribs", "American", "Main Course"),
    ("New England Clam Chowder", "American", "Soup"),
    ("Apple Pie", "American", "Dessert"),
    ("Chocolate Chip Cookies", "American", "Dessert"),
    ("Pancakes with Maple Syrup", "American", "Breakfast"),
    ("Fried Chicken", "American", "Main Course"),
    ("Caesar Salad", "American", "Salad"),
    ("BLT Sandwich", "American", "Lunch"),
    ("Pulled Pork Sandwich", "American", "Main Course"),
    ("Brownies", "American", "Dessert"),
    ("Clam Bake", "American", "Main Course"),
    ("Cornbread", "American", "Side"),
    ("Lobster Roll", "American", "Main Course"),
    ("Philly Cheesesteak", "American", "Main Course"),
    ("Mashed Potatoes with Gravy", "American", "Side"),
    ("Eggs Benedict", "American", "Breakfast"),
    ("French Toast", "American", "Breakfast"),
    ("Waffles", "American", "Breakfast"),
    ("Biscuits and Gravy", "American", "Breakfast"),
    ("Pot Roast", "American", "Main Course"),
    ("Coleslaw", "American", "Side"),
    ("Meatloaf", "American", "Main Course"),
    ("Key Lime Pie", "American", "Dessert"),
    ("Cheesecake (New York Style)", "American", "Dessert"),
    ("Gumbo", "American", "Soup"),
    ("Jambalaya", "American", "Main Course"),
    ("Po' Boy Sandwich", "American", "Main Course"),
    ("Grilled Cheese Sandwich", "American", "Lunch"),
    ("Cobb Salad", "American", "Salad"),
    ("Onion Rings", "American", "Snack"),
    ("Hot Dogs with Relish", "American", "Lunch"),
    ("Banana Bread", "American", "Baking"),

    # French (20)
    ("French Onion Soup", "French", "Soup"),
    ("Beef Bourguignon", "French", "Main Course"),
    ("Coq au Vin", "French", "Main Course"),
    ("Ratatouille", "French", "Main Course"),
    ("Crème Brûlée", "French", "Dessert"),
    ("Croissant", "French", "Breakfast"),
    ("Quiche Lorraine", "French", "Breakfast"),
    ("Duck Confit", "French", "Main Course"),
    ("Soufflé (Cheese)", "French", "Main Course"),
    ("Chocolate Lava Cake", "French", "Dessert"),
    ("Bouillabaisse", "French", "Soup"),
    ("Salade Niçoise", "French", "Salad"),
    ("Tarte Tatin", "French", "Dessert"),
    ("Cassoulet", "French", "Main Course"),
    ("Steak Frites with Béarnaise", "French", "Main Course"),
    ("Madeleines", "French", "Dessert"),
    ("Macarons", "French", "Dessert"),
    ("Crêpes Suzette", "French", "Dessert"),
    ("Pot-au-Feu", "French", "Soup"),
    ("Gratin Dauphinois", "French", "Side"),

    # Thai (20)
    ("Pad Thai", "Thai", "Main Course"),
    ("Tom Yum Goong", "Thai", "Soup"),
    ("Green Curry with Chicken", "Thai", "Main Course"),
    ("Massaman Curry", "Thai", "Main Course"),
    ("Som Tum (Papaya Salad)", "Thai", "Salad"),
    ("Mango Sticky Rice", "Thai", "Dessert"),
    ("Tom Kha Gai", "Thai", "Soup"),
    ("Pad Kra Pao (Basil Chicken)", "Thai", "Main Course"),
    ("Panang Curry", "Thai", "Main Course"),
    ("Pad See Ew", "Thai", "Main Course"),
    ("Satay Chicken with Peanut Sauce", "Thai", "Appetizer"),
    ("Thai Fish Cakes", "Thai", "Appetizer"),
    ("Yellow Curry", "Thai", "Main Course"),
    ("Khao Soi", "Thai", "Main Course"),
    ("Thai Fried Rice", "Thai", "Main Course"),
    ("Pineapple Fried Rice", "Thai", "Main Course"),
    ("Larb Gai (Minced Chicken Salad)", "Thai", "Salad"),
    ("Thai Iced Tea Pudding", "Thai", "Dessert"),
    ("Drunken Noodles (Pad Kee Mao)", "Thai", "Main Course"),
    ("Tod Mun Pla", "Thai", "Appetizer"),

    # Middle Eastern & Mediterranean (25)
    ("Hummus with Tahini", "Middle Eastern", "Appetizer"),
    ("Falafel", "Middle Eastern", "Main Course"),
    ("Chicken Shawarma", "Middle Eastern", "Main Course"),
    ("Shakshuka", "Middle Eastern", "Breakfast"),
    ("Baba Ganoush", "Middle Eastern", "Appetizer"),
    ("Tabbouleh", "Middle Eastern", "Salad"),
    ("Baklava", "Middle Eastern", "Dessert"),
    ("Kofta Kebab", "Middle Eastern", "Main Course"),
    ("Mansaf", "Middle Eastern", "Main Course"),
    ("Greek Salad", "Mediterranean", "Salad"),
    ("Moussaka", "Mediterranean", "Main Course"),
    ("Spanakopita", "Mediterranean", "Snack"),
    ("Tzatziki Dip", "Mediterranean", "Appetizer"),
    ("Souvlaki (Chicken Skewers)", "Mediterranean", "Main Course"),
    ("Dolmas (Stuffed Grape Leaves)", "Mediterranean", "Appetizer"),
    ("Fattoush Salad", "Middle Eastern", "Salad"),
    ("Knafeh", "Middle Eastern", "Dessert"),
    ("Foul Mudammas", "Middle Eastern", "Breakfast"),
    ("Lentil Soup (Shorba)", "Middle Eastern", "Soup"),
    ("Lamb Tagine with Apricots", "Moroccan", "Main Course"),
    ("Couscous with Roasted Veggies", "Moroccan", "Main Course"),
    ("Za'atar Flatbread (Manakish)", "Middle Eastern", "Breakfast"),
    ("Shish Taouk", "Middle Eastern", "Main Course"),
    ("Halva", "Middle Eastern", "Dessert"),
    ("Mujadara (Lentils and Rice)", "Middle Eastern", "Main Course"),

    # Korean (20)
    ("Bibimbap", "Korean", "Main Course"),
    ("Kimchi Jjigae", "Korean", "Soup"),
    ("Bulgogi Beef", "Korean", "Main Course"),
    ("Tteokbokki (Spicy Rice Cakes)", "Korean", "Snack"),
    ("Korean Fried Chicken", "Korean", "Main Course"),
    ("Japchae (Glass Noodles)", "Korean", "Main Course"),
    ("Samgyeopsal (Pork Belly)", "Korean", "Main Course"),
    ("Kimchi Pancake (Jeon)", "Korean", "Appetizer"),
    ("Sundubu Jjigae (Soft Tofu Stew)", "Korean", "Soup"),
    ("Galbi (Short Ribs)", "Korean", "Main Course"),
    ("Kimbap", "Korean", "Snack"),
    ("Bingsu (Shaved Ice)", "Korean", "Dessert"),
    ("Hotteok (Sweet Pancakes)", "Korean", "Dessert"),
    ("Budae Jjigae (Army Stew)", "Korean", "Soup"),
    ("Bossam (Boiled Pork)", "Korean", "Main Course"),
    ("Dakgalbi (Spicy Chicken)", "Korean", "Main Course"),
    ("Mandu (Korean Dumplings)", "Korean", "Appetizer"),
    ("Soybean Paste Stew (Doenjang Jjigae)", "Korean", "Soup"),
    ("Tornado Potato", "Korean", "Snack"),
    ("Jajangmyeon", "Korean", "Main Course"),

    # Spanish (15)
    ("Paella Valenciana", "Spanish", "Main Course"),
    ("Patatas Bravas", "Spanish", "Appetizer"),
    ("Gazpacho", "Spanish", "Soup"),
    ("Tortilla Española (Spanish Omelette)", "Spanish", "Breakfast"),
    ("Chorizo al Vino", "Spanish", "Appetizer"),
    ("Gambas al Ajillo (Garlic Shrimp)", "Spanish", "Appetizer"),
    ("Empanadas Gallegas", "Spanish", "Snack"),
    ("Crema Catalana", "Spanish", "Dessert"),
    ("Croquetas de Jamón", "Spanish", "Appetizer"),
    ("Pisto Manchego", "Spanish", "Side"),
    ("Fabada Asturiana", "Spanish", "Soup"),
    ("Pulpo a la Gallega (Galician Octopus)", "Spanish", "Appetizer"),
    ("Salmorejo", "Spanish", "Soup"),
    ("Albondigas (Spanish Meatballs)", "Spanish", "Appetizer"),
    ("Basque Burnt Cheesecake", "Spanish", "Dessert"),

    # Global Desserts, Soups & Street Food (30)
    ("Tiramisu", "Italian", "Dessert"),
    ("Cinnamon Rolls", "Baking", "Breakfast"),
    ("Pavlova", "Australian", "Dessert"),
    ("Pastéis de Nata", "Portuguese", "Dessert"),
    ("Peri Peri Chicken", "African", "Main Course"),
    ("Pho Bo (Vietnamese Beef Noodle)", "Vietnamese", "Soup"),
    ("Banh Mi Sandwich", "Vietnamese", "Lunch"),
    ("Vietnamese Spring Rolls", "Vietnamese", "Appetizer"),
    ("Beef Rendang", "Indonesian", "Main Course"),
    ("Nasi Goreng", "Indonesian", "Main Course"),
    ("Satay with Peanut Sauce", "Indonesian", "Appetizer"),
    ("Poutine", "Canadian", "Snack"),
    ("Fish and Chips", "British", "Main Course"),
    ("Shepherd's Pie", "British", "Main Course"),
    ("Beef Wellington", "British", "Main Course"),
    ("Bangers and Mash", "British", "Main Course"),
    ("Sticky Toffee Pudding", "British", "Dessert"),
    ("Irish Beef Stew", "Irish", "Soup"),
    ("Sauerbraten", "German", "Main Course"),
    ("Bratwurst with Sauerkraut", "German", "Main Course"),
    ("Pretzels", "German", "Baking"),
    ("Wiener Schnitzel", "Austrian", "Main Course"),
    ("Apple Strudel", "Austrian", "Dessert"),
    ("Goulash", "Hungarian", "Soup"),
    ("Borscht", "Eastern European", "Soup"),
    ("Pierogi", "Polish", "Main Course"),
    ("Arepas", "Venezuelan", "Breakfast"),
    ("Ceviche", "Peruvian", "Appetizer"),
    ("Lomo Saltado", "Peruvian", "Main Course"),
    ("Feijoada", "Brazilian", "Main Course")
]

SYSTEM_PROMPT = """
You are a culinary data engine. Generate a STRICT, standardized JSON recipe object matching the exact schema below.
Rules:
- EXACT times and temperatures for every step.
- Visual cues for completion (e.g. "Edges become golden brown and crisp").
- List explicit techniques used (e.g. searing, braising, double_boiling, simmering, caramelization, tempering).
- Accurate ingredient quantities and units.
- Realistic safety notes for meat/allergens/hot oil.

Output MUST be clean JSON matching this exact structure:
{
  "id": "slug_id",
  "name": "Dish Name",
  "aliases": ["Alias 1"],
  "cuisine": "Cuisine",
  "category": "Main Course",
  "sub_category": "Curry / Rice / Pasta etc.",
  "difficulty": "Easy|Medium|Hard",
  "servings": 4,
  "prep_time_minutes": 20,
  "cook_time_minutes": 40,
  "total_time_minutes": 60,
  "dietary_tags": ["Gluten-Free", "Vegetarian", etc.],
  "ingredients": [
    {"name": "Ingredient Name", "quantity": 1.5, "unit": "cups/tbsp/lbs/g", "category": "Produce/Meat/Dairy", "substitutes": ["Alternative"], "prep_note": "diced"}
  ],
  "steps": [
    {
      "step_number": 1,
      "phase": "Prep / Cooking / Finishing",
      "instruction": "Detailed, explicit action.",
      "duration_minutes": 10,
      "temperature": "Medium-high heat (375°F / 190°C)",
      "heat_level": "Medium-High",
      "visual_cue": "Exact visual indicator of doneness.",
      "equipment": ["Pan", "Tongs"],
      "techniques_used": ["searing"],
      "tips": "Pro chef tip"
    }
  ],
  "techniques_referenced": ["searing", "simmering"],
  "nutrition_per_serving": {"calories": 450, "protein_g": 25, "carbs_g": 40, "fat_g": 18},
  "safety_notes": ["Safety note if applicable"]
}
"""

def generate_recipe(dish_name: str, cuisine: str, category: str):
    prompt = f"Generate the complete, authentic recipe for: '{dish_name}' (Cuisine: {cuisine}, Category: {category}). Return ONLY valid JSON."
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        system_instruction=SYSTEM_PROMPT,
        temperature=0.2
    )

    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=[types.Part.from_text(text=prompt)],
        config=config
    )
    return json.loads(response.text)

def main():
    print(f"==================================================")
    print(f" Starting LetMeCook 300 Global Recipe Generator")
    print(f" Target: 300 Recipes | Rate: 15 req/min (Free Tier)")
    print(f"==================================================")

    # Check existing recipes in DB
    existing_ids = set()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM recipes")
        for row in cursor.fetchall():
            existing_ids.add(row['id'])

    print(f"Found {len(existing_ids)} existing recipes in database.")

    count = 0
    start_time = time.time()

    for idx, (dish, cuisine, category) in enumerate(TOP_300_DISHES, 1):
        slug = dish.lower().replace(" ", "_").replace("'", "").replace("(", "").replace(")", "").replace("-", "_")
        
        if slug in existing_ids:
            print(f"[{idx}/300] Skipping '{dish}' (already in DB)")
            continue

        print(f"[{idx}/300] Generating '{dish}' ({cuisine})...", end="", flush=True)
        try:
            recipe_data = generate_recipe(dish, cuisine, category)
            recipe_data['id'] = slug
            insert_recipe(recipe_data)
            existing_ids.add(slug)
            count += 1
            print(f" Done! (Total in DB: {len(existing_ids)})")
        except Exception as e:
            print(f" Error: {e}")

        # Comply with 15 requests per minute limit (wait 4.2 seconds between calls)
        time.sleep(4.2)

    elapsed = (time.time() - start_time) / 60
    print(f"\n==================================================")
    print(f" Completed! Generated {count} new recipes in {elapsed:.1f} minutes.")
    print(f" Total recipes in SQLite database: {len(existing_ids)}")
    print(f"==================================================")

if __name__ == "__main__":
    main()
