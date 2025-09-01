import json

from helper import (
    normalize_and_expand,
    score_recipe,
    recipe_matches_filters,
    missing_ingredients,
    DEFAULT_WEIGHTS,
)

def load_recipes(path="data/recipes.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def yesno(prompt: str) -> bool:
    return input(prompt).strip().lower() in {"y", "yes", "j", "ja", ""}

def ask_int(prompt: str, default: int) -> int:
    val = input(f"{prompt} [{default}]: ").strip()
    if not val:
        return default
    try:
        return max(1, int(val))
    except ValueError:
        return default

def main():
    recipes = load_recipes()
    print("Leftover Chef — type ingredients and get recipe matches.\n")

    while True:
        raw = input("What do you have? (comma-separated, empty to quit) ").strip()
        if not raw:
            break

        vegan = yesno("Filter: vegan? [Y/n] ")
        if not vegan:
            vegetarian = yesno("Filter: vegetarian? [Y/n] ")
        else:
            vegetarian = False
        gluten_free = yesno("Filter: gluten-free? [Y/n] ")
        use_weights = yesno("Use ingredient weights? [Y/n] ")
        top_n = ask_int("How many results", 10)
        hint_k = ask_int("How many missing-ingredient hints", 3)

        my_ings = normalize_and_expand(raw.split(","))
        weights = DEFAULT_WEIGHTS if use_weights else None

        ranked = []
        for r in recipes:
            if not recipe_matches_filters(
                r["ingredients"],
                vegetarian=vegetarian,
                vegan=vegan,
                gluten_free=gluten_free,
            ):
                continue
            r_ings = normalize_and_expand(r["ingredients"])
            s = score_recipe(my_ings, r_ings, weights=weights)
            ranked.append((s, r, r_ings))

        ranked.sort(key=lambda x: x[0], reverse=True)

        if not ranked:
            print("No matches found.\n")
            continue

        print("\nTop matches:")
        for s, r, r_ings in ranked[:top_n]:
            hints = missing_ingredients(my_ings, r_ings, k=hint_k)
            hints_str = f", missing: {', '.join(hints)}" if hints else ""
            url = r.get("url", "")
            print(f"{s:>5}  {r['title']} -> {url}{hints_str}")
        print()

if __name__ == "__main__":
    main()


