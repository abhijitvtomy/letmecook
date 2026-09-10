"""
LetMeCook: Option 2 Batch Generator (Next 500 Recipes via Gemini 3.6 Flash)
Uses Gemini 3.6 Flash to directly create 500 new, authentic recipes with exact timings,
temperatures, visual cues, and technique definitions, saving each into SQLite.
"""

import os
import sys
import json
import time
import re
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

load_dotenv(os.path.join(ROOT_DIR, '.env'))

from google import genai
from google.genai import types
from app.database import get_db, insert_recipe, init_db

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in .env")

client = genai.Client(api_key=API_KEY)

# Broad diverse list of 500 distinct world dishes to generate via Gemini
BATCH_DISHES_500 = [
    # Middle East & Mediterranean
    ("Shakshuka with Feta", "Middle Eastern", "Breakfast"),
    ("Chicken Shawarma Platter", "Middle Eastern", "Main Course"),
    ("Authentic Falafel with Tahini", "Middle Eastern", "Main Course"),
    ("Moutabal (Roasted Eggplant Dip)", "Middle Eastern", "Appetizer"),
    ("Lamb Kofta Kebabs", "Middle Eastern", "Main Course"),
    ("Mansaf (Jordanian Lamb and Rice)", "Middle Eastern", "Main Course"),
    ("Tabbouleh Salad", "Middle Eastern", "Salad"),
    ("Fattoush with Crispy Pita", "Middle Eastern", "Salad"),
    ("Baklava with Pistachios", "Middle Eastern", "Dessert"),
    ("Knafeh with Cheese and Sugar Syrup", "Middle Eastern", "Dessert"),
    ("Stuffed Grape Leaves (Dolma)", "Middle Eastern", "Appetizer"),
    ("Chicken Souvlaki with Tzatziki", "Greek", "Main Course"),
    ("Authentic Greek Moussaka", "Greek", "Main Course"),
    ("Spanakopita (Spinach Pie)", "Greek", "Snack"),
    ("Greek Lemon Potatoes", "Greek", "Side"),
    ("Moroccan Chicken Tagine with Preserved Lemon", "Moroccan", "Main Course"),
    ("Lamb Tagine with Prunes and Almonds", "Moroccan", "Main Course"),
    ("Traditional Couscous with Seven Vegetables", "Moroccan", "Main Course"),
    ("Harira (Moroccan Lentil and Chickpea Soup)", "Moroccan", "Soup"),
    ("Za'atar Flatbread (Manakish)", "Middle Eastern", "Breakfast"),

    # East Asia: Japanese
    ("Tonkotsu Ramen with Chashu", "Japanese", "Main Course"),
    ("Miso Ramen with Corn and Butter", "Japanese", "Main Course"),
    ("Shoyu Ramen", "Japanese", "Main Course"),
    ("Chicken Katsu Curry", "Japanese", "Main Course"),
    ("Crispy Shrimp Tempura", "Japanese", "Appetizer"),
    ("Okonomiyaki (Osaka Style)", "Japanese", "Main Course"),
    ("Takoyaki (Octopus Balls)", "Japanese", "Snack"),
    ("Chicken Yakitori Skewers", "Japanese", "Appetizer"),
    ("Pork Tonkatsu", "Japanese", "Main Course"),
    ("Japanese Pork Gyoza", "Japanese", "Appetizer"),
    ("Gyudon (Japanese Beef Bowl)", "Japanese", "Main Course"),
    ("Oyakodon (Chicken and Egg Bowl)", "Japanese", "Main Course"),
    ("Katsudon (Pork Cutlet Bowl)", "Japanese", "Main Course"),
    ("Matcha Green Tea Mille Crepe Cake", "Japanese", "Dessert"),
    ("Sweet Red Bean Dorayaki", "Japanese", "Dessert"),
    ("Japanese Strawberry Shortcake", "Japanese", "Dessert"),
    ("Zaru Soba with Dipping Sauce", "Japanese", "Main Course"),
    ("Tamagoyaki (Japanese Rolled Omelette)", "Japanese", "Breakfast"),
    ("Agedashi Tofu with Dashi Broth", "Japanese", "Appetizer"),
    ("Chawanmushi (Savory Egg Custard)", "Japanese", "Appetizer"),
    ("Beef Sukiyaki Hot Pot", "Japanese", "Main Course"),
    ("Shabu Shabu with Sesame Sauce", "Japanese", "Main Course"),
    ("Japanese Milk Bread (Shokupan)", "Japanese", "Baking"),
    ("Salmon Teriyaki", "Japanese", "Main Course"),
    ("Chicken Karaage", "Japanese", "Appetizer"),

    # East Asia: Korean
    ("Dolsot Bibimbap with Gochujang", "Korean", "Main Course"),
    ("Kimchi Jjigae (Spicy Kimchi Stew)", "Korean", "Soup"),
    ("Sundubu Jjigae (Spicy Soft Tofu Stew)", "Korean", "Soup"),
    ("Bulgogi (Marinated Beef BBQ)", "Korean", "Main Course"),
    ("Galbi (Marinated Beef Short Ribs)", "Korean", "Main Course"),
    ("Crispy Korean Fried Chicken with Sweet Spicy Glaze", "Korean", "Main Course"),
    ("Tteokbokki (Spicy Rice Cakes)", "Korean", "Snack"),
    ("Japchae (Stir-Fried Glass Noodles)", "Korean", "Main Course"),
    ("Samgyeopsal with Ssamjang Dip", "Korean", "Main Course"),
    ("Haemul Pajeon (Scallion Seafood Pancake)", "Korean", "Appetizer"),
    ("Kimchi Fried Rice with Fried Egg", "Korean", "Main Course"),
    ("Budae Jjigae (Army Base Stew)", "Korean", "Soup"),
    ("Dakgalbi (Spicy Stir-Fried Chicken)", "Korean", "Main Course"),
    ("Jajangmyeon (Black Bean Noodles)", "Korean", "Main Course"),
    ("Jjamppong (Spicy Seafood Noodle Soup)", "Korean", "Soup"),
    ("Bossam (Pork Belly Wraps)", "Korean", "Main Course"),
    ("Hotteok (Sweet Brown Sugar Pancakes)", "Korean", "Dessert"),
    ("Bingsu (Korean Shaved Ice with Mango)", "Korean", "Dessert"),
    ("Doenjang Jjigae (Soybean Paste Stew)", "Korean", "Soup"),
    ("Gimbap (Korean Seaweed Rice Rolls)", "Korean", "Snack"),

    # East Asia: Chinese
    ("Kung Pao Chicken (Sichuan Style)", "Chinese", "Main Course"),
    ("Mapo Tofu with Minced Pork", "Chinese", "Main Course"),
    ("Authentic Peking Duck with Pancakes", "Chinese", "Main Course"),
    ("Crispy Sweet and Sour Pork", "Chinese", "Main Course"),
    ("Siu Mai (Pork and Shrimp Dumplings)", "Chinese", "Appetizer"),
    ("Har Gow (Crystal Shrimp Dumplings)", "Chinese", "Appetizer"),
    ("Xiao Long Bao (Soup Dumplings)", "Chinese", "Appetizer"),
    ("Sichuan Dan Dan Noodles", "Chinese", "Main Course"),
    ("Yangzhou Special Fried Rice", "Chinese", "Main Course"),
    ("Hot and Sour Soup (Authentic)", "Chinese", "Soup"),
    ("Traditional Wonton Soup in Chicken Broth", "Chinese", "Soup"),
    ("Crispy Cantonese Spring Rolls", "Chinese", "Snack"),
    ("General Tso's Chicken", "Chinese", "Main Course"),
    ("Beef and Broccoli Stir-Fry", "Chinese", "Main Course"),
    ("Char Siu (Cantonese BBQ Pork)", "Chinese", "Main Course"),
    ("Steamed Pork Buns (Baozi)", "Chinese", "Snack"),
    ("Sichuan Boiled Fish in Chili Oil", "Chinese", "Main Course"),
    ("Scallion Oil Noodles", "Chinese", "Main Course"),
    ("Cantonese Steamed Whole Fish with Ginger and Scallions", "Chinese", "Main Course"),
    ("Hainanese Chicken Rice with Chili Sauce", "Chinese", "Main Course"),
    ("Mongolian Beef with Scallions", "Chinese", "Main Course"),
    ("Honey Walnut Shrimp", "Chinese", "Main Course"),
    ("Orange Peel Beef", "Chinese", "Main Course"),
    ("Egg Drop Soup with Sweet Corn", "Chinese", "Soup"),
    ("Mooncake with Lotus Seed Paste", "Chinese", "Dessert"),
    ("Tangyuan (Glutinous Rice Balls in Ginger Syrup)", "Chinese", "Dessert"),
    ("Twice Cooked Pork Belly", "Chinese", "Main Course"),
    ("Salt and Pepper Calamari", "Chinese", "Appetizer"),
    ("Chinese Century Egg Congee", "Chinese", "Breakfast"),
    ("Chinese Steamed Egg Custard", "Chinese", "Side"),

    # Southeast Asian: Thai & Vietnamese
    ("Pad Thai with Tiger Prawns", "Thai", "Main Course"),
    ("Tom Yum Goong (Spicy Prawn Soup)", "Thai", "Soup"),
    ("Tom Kha Gai (Coconut Chicken Soup)", "Thai", "Soup"),
    ("Authentic Thai Green Chicken Curry", "Thai", "Main Course"),
    ("Massaman Beef Curry with Potatoes", "Thai", "Main Course"),
    ("Panang Chicken Curry", "Thai", "Main Course"),
    ("Som Tum (Green Papaya Salad)", "Thai", "Salad"),
    ("Mango Sticky Rice with Coconut Cream", "Thai", "Dessert"),
    ("Pad Kra Pao (Holy Basil Minced Chicken)", "Thai", "Main Course"),
    ("Pad See Ew (Wide Rice Noodles with Pork)", "Thai", "Main Course"),
    ("Pad Kee Mao (Drunken Noodles)", "Thai", "Main Course"),
    ("Khao Soi (Northern Thai Curry Noodle Soup)", "Thai", "Main Course"),
    ("Chicken Satay with Spicy Peanut Sauce", "Thai", "Appetizer"),
    ("Thai Fish Cakes (Tod Mun Pla)", "Thai", "Appetizer"),
    ("Larb Gai (Spicy Minced Chicken Salad)", "Thai", "Salad"),
    ("Traditional Vietnamese Beef Pho (Pho Bo)", "Vietnamese", "Soup"),
    ("Chicken Pho (Pho Ga)", "Vietnamese", "Soup"),
    ("Banh Mi with Lemongrass Pork", "Vietnamese", "Lunch"),
    ("Fresh Vietnamese Summer Spring Rolls with Peanut Dip", "Vietnamese", "Appetizer"),
    ("Bun Cha (Hanoi Grilled Pork with Noodles)", "Vietnamese", "Main Course"),
    ("Banh Xeo (Crispy Vietnamese Pancake)", "Vietnamese", "Main Course"),
    ("Vietnamese Caramelized Pork and Eggs (Thit Kho)", "Vietnamese", "Main Course"),
    ("Vietnamese Shaking Beef (Bo Luc Lac)", "Vietnamese", "Main Course"),
    ("Vietnamese Egg Coffee", "Vietnamese", "Beverage"),
    ("Indonesian Nasi Goreng with Fried Egg", "Indonesian", "Main Course"),
    ("Beef Rendang (Slow-Cooked Coconut Beef)", "Indonesian", "Main Course"),
    ("Mie Goreng (Stir-Fried Yellow Noodles)", "Indonesian", "Main Course"),
    ("Gado Gado with Peanut Dressing", "Indonesian", "Salad"),
    ("Singapore Chili Crab", "Singaporean", "Main Course"),
    ("Laksa (Spicy Coconut Noodle Soup)", "Malaysian", "Soup"),

    # Indian & South Asian
    ("Hyderabadi Dum Biryani (Chicken)", "Indian", "Main Course"),
    ("Lucknowi Mutton Biryani", "Indian", "Main Course"),
    ("Butter Chicken (Restaurant Style)", "Indian", "Main Course"),
    ("Paneer Butter Masala", "Indian", "Main Course"),
    ("Dal Makhani (Slow-Cooked 24-Hour Style)", "Indian", "Main Course"),
    ("Palak Paneer with Homemade Paneer", "Indian", "Main Course"),
    ("Amritsari Chole Bhature", "Indian", "Main Course"),
    ("Kashmiri Rogan Josh", "Indian", "Main Course"),
    ("Chicken Tikka Masala", "Indian", "Main Course"),
    ("South Indian Masala Dosa with Chutneys", "Indian", "Breakfast"),
    ("Soft Idli with Madras Sambar", "Indian", "Breakfast"),
    ("Crispy Medu Vada", "Indian", "Breakfast"),
    ("Goan Fish Curry with Coconut and Kokum", "Indian", "Main Course"),
    ("Prawn Malai Curry (Bengali Style)", "Indian", "Main Course"),
    ("Punjabi Samosa with Mint Chutney", "Indian", "Snack"),
    ("Aloo Gobi Matar", "Indian", "Main Course"),
    ("Tandoori Chicken Skewers", "Indian", "Main Course"),
    ("Mumbai Pani Puri (Puchka)", "Indian", "Snack"),
    ("Pav Bhaji with Butter Pav", "Indian", "Snack"),
    ("Melt-in-Mouth Gulab Jamun", "Indian", "Dessert"),
    ("Soft Bengali Rasgulla", "Indian", "Dessert"),
    ("Crispy Hot Jalebi with Rabdi", "Indian", "Dessert"),
    ("Chicken Korma (Shahi Style)", "Indian", "Main Course"),
    ("Mumbai Vada Pav with Garlic Chutney", "Indian", "Snack"),
    ("Rajma Masala (Punjabi Kidney Beans)", "Indian", "Main Course"),
    ("Spicy Chicken 65", "Indian", "Appetizer"),
    ("Gujarati Khaman Dhokla", "Indian", "Snack"),
    ("Dal Tadka (Dhaba Style Double Tempering)", "Indian", "Main Course"),
    ("Smoked Baingan Bharta", "Indian", "Main Course"),
    ("Kadhai Paneer with Bell Peppers", "Indian", "Main Course"),
    ("Malai Kofta in Rich Cashew Gravy", "Indian", "Main Course"),
    ("Keema Matar (Spicy Minced Lamb)", "Indian", "Main Course"),
    ("Gajar Ka Halwa with Khoya", "Indian", "Dessert"),
    ("Rice Kheer with Cardamom and Nuts", "Indian", "Dessert"),
    ("Chicken Chettinad with Fresh Roasted Spices", "Indian", "Main Course"),
    ("Aloo Paratha with Homemade White Butter", "Indian", "Breakfast"),
    ("Shahi Tukda (Royal Bread Pudding)", "Indian", "Dessert"),
    ("Hyderabadi Haleem", "Indian", "Main Course"),
    ("Kolhapuri Chicken (Fiery Maharashtrian)", "Indian", "Main Course"),
    ("Fish Fry (South Indian Rava Coating)", "Indian", "Appetizer"),
    ("Egg Roast (Kerala Style)", "Indian", "Breakfast"),
    ("Kerala Beef Fry (Ularthiyathu)", "Indian", "Main Course"),
    ("Appam with Vegetable Stew", "Indian", "Breakfast"),
    ("Dahi Vada with Sweet Tamarind Chutney", "Indian", "Snack"),
    ("Paneer Tikka with Grilled Peppers", "Indian", "Appetizer"),
    ("Mysore Pak", "Indian", "Dessert"),
    ("Bisi Bele Bath", "Indian", "Main Course"),
    ("Kashmiri Dum Aloo", "Indian", "Main Course"),
    ("Prawn Balchao", "Indian", "Main Course"),
    ("Chicken Sukka (Mangalorean)", "Indian", "Main Course"),

    # Italian
    ("Authentic Spaghetti Carbonara (Guanciale and Pecorino)", "Italian", "Main Course"),
    ("Neapolitan Margherita Pizza from Scratch", "Italian", "Main Course"),
    ("Classic Lasagna al Forno with Béchamel", "Italian", "Main Course"),
    ("Traditional Spaghetti Bolognese", "Italian", "Main Course"),
    ("Fettuccine Alfredo with Parmigiano-Reggiano", "Italian", "Main Course"),
    ("Risotto alla Milanese with Saffron", "Italian", "Main Course"),
    ("Creamy Wild Mushroom Risotto", "Italian", "Main Course"),
    ("Classic Tiramisu with Mascarpone and Espresso", "Italian", "Dessert"),
    ("Vanilla Bean Panna Cotta with Berry Coulis", "Italian", "Dessert"),
    ("Bruschetta al Pomodoro e Basilico", "Italian", "Appetizer"),
    ("Cacio e Pepe (Roman Cheese and Pepper Pasta)", "Italian", "Main Course"),
    ("Penne all'Arrabbiata", "Italian", "Main Course"),
    ("Osso Buco alla Milanese with Gremolata", "Italian", "Main Course"),
    ("Classic Tuscan Minestrone Soup", "Italian", "Soup"),
    ("Gnocchi alla Sorrentina with Baked Mozzarella", "Italian", "Main Course"),
    ("Chicken Parmigiana with Melted Mozzarella", "Italian", "Main Course"),
    ("Melanzane alla Parmigiana (Eggplant Parmesan)", "Italian", "Main Course"),
    ("Rosemary and Sea Salt Focaccia Bread", "Italian", "Baking"),
    ("Sicilian Arancini with Meat Ragu Center", "Italian", "Snack"),
    ("Beef Carpaccio with Shaved Parmesan and Truffle Oil", "Italian", "Appetizer"),
    ("Linguine alle Vongole (Clam Pasta)", "Italian", "Main Course"),
    ("Bistecca alla Fiorentina (Florentine T-Bone Steak)", "Italian", "Main Course"),
    ("Panzanella (Tuscan Tomato and Bread Salad)", "Italian", "Salad"),
    ("Insalata Caprese with Buffalo Mozzarella", "Italian", "Salad"),
    ("Ravioli Ricotta e Spinaci with Sage Butter", "Italian", "Main Course"),
    ("Saltimbocca alla Romana (Veal with Prosciutto and Sage)", "Italian", "Main Course"),
    ("Sicilian Cannoli with Sweet Ricotta Filling", "Italian", "Dessert"),
    ("Affogato al Caffè", "Italian", "Dessert"),
    ("Zuppa Toscana with Italian Sausage and Kale", "Italian", "Soup"),
    ("Creamy Polenta with Braised Short Ribs", "Italian", "Main Course"),

    # French
    ("Classic French Onion Soup with Gruyère Gratin", "French", "Soup"),
    ("Beef Bourguignon (Julia Child Style)", "French", "Main Course"),
    ("Coq au Vin (Chicken in Red Wine)", "French", "Main Course"),
    ("Provençal Ratatouille", "French", "Main Course"),
    ("Classic Crème Brûlée with Caramelized Sugar Crust", "French", "Dessert"),
    ("Buttery French Croissants from Scratch", "French", "Breakfast"),
    ("Quiche Lorraine with Bacon and Gruyère", "French", "Breakfast"),
    ("Crispy Duck Confit with Roasted Potatoes", "French", "Main Course"),
    ("Cheese Soufflé (Soufflé au Fromage)", "French", "Main Course"),
    ("Chocolate Soufflé with Crème Anglaise", "French", "Dessert"),
    ("Marseille Bouillabaisse (Seafood Stew)", "French", "Soup"),
    ("Salade Niçoise with Fresh Seared Tuna", "French", "Salad"),
    ("Tarte Tatin (Caramelized Upside-Down Apple Tart)", "French", "Dessert"),
    ("Traditional Cassoulet with Duck and White Beans", "French", "Main Course"),
    ("Steak Frites with Homemade Béarnaise Sauce", "French", "Main Course"),
    ("French Madeleines with Lemon Zest", "French", "Dessert"),
    ("French Macarons with Ganache", "French", "Dessert"),
    ("Crêpes Suzette with Orange Liqueur Flambé", "French", "Dessert"),
    ("Pot-au-Feu (French Boiled Beef and Root Vegetables)", "French", "Soup"),
    ("Gratin Dauphinois (Creamy French Potato Gratin)", "French", "Side"),
    ("Sole Meunière with Brown Butter and Lemon", "French", "Main Course"),
    ("Pork Rillettes", "French", "Appetizer"),
    ("Éclairs with Chocolate Glaze and Pastry Cream", "French", "Dessert"),
    ("Brioche Loaf", "French", "Baking"),
    ("Beef Tartare with Egg Yolk and Capers", "French", "Appetizer"),

    # Mexican & Central/South American
    ("Authentic Birria Tacos with Consomé Dip", "Mexican", "Main Course"),
    ("Tacos al Pastor with Pineapple", "Mexican", "Main Course"),
    ("Carne Asada Street Tacos", "Mexican", "Main Course"),
    ("Crispy Carnitas (Michoacán Style)", "Mexican", "Main Course"),
    ("Chicken Tinga Tostadas", "Mexican", "Main Course"),
    ("Enchiladas Suizas with Creamy Tomatillo Sauce", "Mexican", "Main Course"),
    ("Enchiladas Rojas with Queso Fresco", "Mexican", "Main Course"),
    ("Chiles Rellenos with Queso Oaxaca and Tomato Caldillo", "Mexican", "Main Course"),
    ("Mexican Street Corn (Elote Asado)", "Mexican", "Snack"),
    ("Churros with Cinnamon Sugar and Mexican Chocolate Sauce", "Mexican", "Dessert"),
    ("Tres Leches Cake (Three Milk Cake)", "Mexican", "Dessert"),
    ("Traditional Pozole Rojo with Pork and Hominy", "Mexican", "Soup"),
    ("Sopa de Tortilla (Chicken Tortilla Soup)", "Mexican", "Soup"),
    ("Authentic Mole Poblano with Turkey", "Mexican", "Main Course"),
    ("Huevos Rancheros on Warm Corn Tortillas", "Mexican", "Breakfast"),
    ("Chilaquiles Verdes with Fried Eggs and Crema", "Mexican", "Breakfast"),
    ("Tamales de Pollo en Salsa Verde", "Mexican", "Main Course"),
    ("Baja California Fish Tacos with Chipotle Crema", "Mexican", "Main Course"),
    ("Classic Guacamole with Molcajete Preparation", "Mexican", "Appetizer"),
    ("Ceviche Mixto with Lime and Habanero", "Mexican", "Appetizer"),
    ("Peruvian Lomo Saltado (Stir-Fried Beef with Fries)", "Peruvian", "Main Course"),
    ("Peruvian Ceviche Clasico with Leche de Tigre", "Peruvian", "Appetizer"),
    ("Causa Limeña (Peruvian Layered Potato Terrine)", "Peruvian", "Appetizer"),
    ("Argentine Empanadas with Ground Beef and Olives", "Argentine", "Snack"),
    ("Argentine Flank Steak with Chimichurri Sauce", "Argentine", "Main Course"),
    ("Brazilian Feijoada (Black Bean and Pork Stew)", "Brazilian", "Main Course"),
    ("Pão de Queijo (Brazilian Cheese Bread)", "Brazilian", "Snack"),
    ("Venezuelan Arepas Reina Pepiada (Chicken and Avocado)", "Venezuelan", "Breakfast"),
    ("Colombian Bandeja Paisa", "Colombian", "Main Course"),
    ("Dulce de Leche Flan", "Latin American", "Dessert"),

    # American & Modern Comfort Food
    ("Classic Smashburger with Caramelized Onions", "American", "Main Course"),
    ("Southern Buttermilk Fried Chicken", "American", "Main Course"),
    ("BBQ Pulled Pork with Tangy Vinegar Slaw", "American", "Main Course"),
    ("Slow-Smoked Texas Beef Brisket", "American", "Main Course"),
    ("Memphis Dry Rub Pork Ribs", "American", "Main Course"),
    ("Gourmet Four-Cheese Macaroni and Cheese", "American", "Main Course"),
    ("New England Clam Chowder in Bread Bowl", "American", "Soup"),
    ("Louisiana Seafood Gumbo with Andouille Sausage", "American", "Soup"),
    ("Cajun Jambalaya with Shrimp and Chicken", "American", "Main Course"),
    ("New Orleans Shrimp Po' Boy", "American", "Main Course"),
    ("Philly Cheesesteak with Provolone and Whiz", "American", "Main Course"),
    ("Maine Lobster Roll with Warm Butter", "American", "Main Course"),
    ("Crispy Buffalo Wings with Blue Cheese Dip", "American", "Appetizer"),
    ("Classic All-American Double Crust Apple Pie", "American", "Dessert"),
    ("New York Style Baked Cheesecake with Berry Compote", "American", "Dessert"),
    ("Warm Chocolate Chip Cookies with Crisp Edges and Gooey Center", "American", "Dessert"),
    ("Fudgy Dark Chocolate Walnut Brownies", "American", "Dessert"),
    ("Key Lime Pie with Graham Cracker Crust", "American", "Dessert"),
    ("Fluffy Buttermilk Pancakes with Maple Syrup", "American", "Breakfast"),
    ("Belgian Waffles with Whipped Cream and Strawberries", "American", "Breakfast"),
    ("Brioche French Toast with Cinnamon Butter", "American", "Breakfast"),
    ("Eggs Benedict with Homemade Hollandaise", "American", "Breakfast"),
    ("Southern Biscuits with Sausage Country Gravy", "American", "Breakfast"),
    ("Creamy Mashed Potatoes with Roasted Garlic and Herb Gravy", "American", "Side"),
    ("Classic Cobb Salad with Dijon Vinaigrette", "American", "Salad"),
    ("All-American Meatloaf with Brown Sugar Tomato Glaze", "American", "Main Course"),
    ("Slow-Cooker Beef Pot Roast with Carrots and Potatoes", "American", "Main Course"),
    ("Grilled Reuben Sandwich with Pastrami and Sauerkraut", "American", "Lunch"),
    ("Crispy Beer-Battered Onion Rings", "American", "Snack"),
    ("Moist Banana Nut Bread with Streusel Topping", "American", "Baking"),

    # British, German, Spanish & European
    ("Traditional British Fish and Chips with Tartar Sauce and Mushy Peas", "British", "Main Course"),
    ("Shepherd's Pie with Lamb and Crispy Mashed Potato Top", "British", "Main Course"),
    ("Cottage Pie with Seasoned Ground Beef", "British", "Main Course"),
    ("Beef Wellington with Prosciutto and Mushroom Duxelles", "British", "Main Course"),
    ("Yorkshire Pudding with Rich Onion Gravy", "British", "Side"),
    ("Full English Breakfast with Baked Beans and Black Pudding", "British", "Breakfast"),
    ("Sticky Toffee Pudding with Warm Toffee Sauce", "British", "Dessert"),
    ("Cornish Pasty", "British", "Snack"),
    ("Irish Lamb Stew with Root Vegetables and Barley", "Irish", "Soup"),
    ("Traditional Irish Soda Bread", "Irish", "Baking"),
    ("German Wiener Schnitzel with Potato Salad", "German", "Main Course"),
    ("Authentic Bavarian Soft Pretzels with Beer Cheese Dip", "German", "Baking"),
    ("Sauerbraten with Braised Red Cabbage", "German", "Main Course"),
    ("Bratwurst with Sauerkraut and Mustard", "German", "Main Course"),
    ("Austrian Apple Strudel (Apfelstrudel)", "Austrian", "Dessert"),
    ("Hungarian Beef Goulash with Egg Noodles", "Hungarian", "Soup"),
    ("Authentic Paella Valenciana with Chicken and Green Beans", "Spanish", "Main Course"),
    ("Seafood Paella (Paella de Marisco)", "Spanish", "Main Course"),
    ("Spanish Patatas Bravas with Spicy Aioli", "Spanish", "Appetizer"),
    ("Tortilla Española (Classic Potato and Onion Omelette)", "Spanish", "Breakfast"),
    ("Gambas al Ajillo (Garlic Shrimp in Olive Oil)", "Spanish", "Appetizer"),
    ("Jamón Serrano Croquetas", "Spanish", "Appetizer"),
    ("Chilled Andalusian Gazpacho", "Spanish", "Soup"),
    ("Basque Burnt Cheesecake", "Spanish", "Dessert"),
    ("Polish Pierogi with Potato and Cheese", "Polish", "Main Course"),
    ("Ukrainian Borscht with Sour Cream and Dill", "Ukrainian", "Soup"),
    ("Russian Beef Stroganoff with Tagliatelle", "Russian", "Main Course"),
    ("Portuguese Pastéis de Nata (Custard Tarts)", "Portuguese", "Dessert"),
    ("Portuguese Peri-Peri Grilled Chicken", "Portuguese", "Main Course"),
    ("Swedish Meatballs with Lingonberry Jam and Cream Sauce", "Swedish", "Main Course"),
    ("Belgian Mussels in White Wine and Garlic (Moules-Frites)", "Belgian", "Main Course")
]

SYSTEM_PROMPT = """
You are a culinary data engine. Generate a STRICT, standardized JSON recipe object matching the exact schema below.
Rules:
- EXACT times and temperatures for every step.
- Visual cues for completion (e.g. "Edges become golden brown and crisp").
- List explicit techniques used (e.g. searing, braising, double_boiling, simmering, caramelization, tempering, deglazing).
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
    prompt = f"Generate the authentic, professional recipe for: '{dish_name}' (Cuisine: {cuisine}, Category: {category}). Return ONLY valid JSON."
    
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
    print("=" * 60)
    print(" LetMeCook: Generating Next Wave of Recipes via Gemini 3.6 Flash")
    print(" Strategy: Option 2 (Pre-generating Full Deep Recipe Records)")
    print("=" * 60)

    init_db()

    existing_names = set()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM recipes")
        for row in cursor.fetchall():
            existing_names.add(row['name'].lower())

    print(f"Current recipes already in database: {len(existing_names)}")

    count = 0
    start_time = time.time()

    for idx, (dish, cuisine, category) in enumerate(BATCH_DISHES_500, 1):
        if dish.lower() in existing_names:
            print(f"[{idx}/{len(BATCH_DISHES_500)}] Skipping '{dish}' (already in DB)")
            continue

        slug = re.sub(r'[^a-zA-Z0-9_]', '', dish.lower().replace(" ", "_"))

        print(f"[{idx}/{len(BATCH_DISHES_500)}] Generating '{dish}' ({cuisine}) via Gemini 3.6 Flash...", end="", flush=True)
        try:
            recipe_data = generate_recipe(dish, cuisine, category)
            recipe_data['id'] = slug
            insert_recipe(recipe_data)
            existing_names.add(dish.lower())
            count += 1
            print(f" Done! (Total in DB: {len(existing_names)})")
        except Exception as e:
            print(f" Error: {e}")

        # Comply with 15 requests/min rate limit (4.2 seconds between requests)
        time.sleep(4.2)

    elapsed = (time.time() - start_time) / 60
    print("\n" + "=" * 60)
    print(f" Batch generation complete! Generated {count} high-fidelity recipes in {elapsed:.1f} minutes.")
    print(f" Total recipes now live in SQLite: {len(existing_names)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
