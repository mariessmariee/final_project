

from typing import List, Dict

def get_recipe_suggestions(my_ingredients: List[str]) -> List[Dict]:
    # TODO: echte Logik einbauen (Web-Scraping, Matching …)
    demo_recipe = {
        "title": "Demo-Tomatenpasta",
        "url":   "https://example.com/demo-pasta",
        "matches": [i for i in my_ingredients if i in {"tomate", "pasta", "käse"}],
    }
    return [demo_recipe]
