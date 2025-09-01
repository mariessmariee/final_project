import json
from helper import normalize_and_expand, score_recipe

def load_recipes(path="data/recipes.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    ingredients = input("What do you have? (comma-separated) ")
    my_ings = normalize_and_expand(ingredients.split(","))
    recipes = load_recipes()

    scored = []
    for r in recipes:
        recipe_ings = normalize_and_expand(r["ingredients"])
        s = score_recipe(my_ings, recipe_ings)
        scored.append((s, r))

    scored.sort(key=lambda x: x[0], reverse=True)

    print("\nTop matches:")
    for s, r in scored[:10]:
        print(f"{s:>5}  {r['title']}  -> {r['url']}")

if __name__ == "__main__":
    main()
