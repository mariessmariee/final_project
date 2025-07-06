from scraper import get_demo_recipe_list
from matcher import score_recipe

def main():
    ingredients_raw = input("Ingredients (comma-separated): ")
    my_ingredients = [x.strip().lower() for x in ingredients_raw.split(",") if x.strip()]

    if not my_ingredients:
        print("No ingredients given – exiting.")
        return

    recipes = get_demo_recipe_list()

    for r in recipes:
        r["score"] = score_recipe(my_ingredients, r["ingredients"])

    recipes.sort(key=lambda r: r["score"], reverse=True)

    print("\nTop matches:")
    for r in recipes:
        print(f"- {r['title']} (score {r['score']}) :: {r['url']}")

if __name__ == "__main__":
    main()
