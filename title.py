"""
Leftover Chef – Einstiegspunkt.

Aufruf:
    python title.py
"""

from helper import get_recipe_suggestions

def main() -> None:
    ingredients = input("Welche Zutaten hast du? (Komma-getrennt) > ").split(",")
    cleaned = [i.strip().lower() for i in ingredients if i.strip()]
    if not cleaned:
        print("⚠️  Keine Zutaten eingegeben.")
        return

    recipes = get_recipe_suggestions(cleaned)

    print("\nTop-Treffer:")
    for i, rec in enumerate(recipes, 1):
        print(f"{i}) {rec['title']} – passt zu: {', '.join(rec['matches'])}")
        print(f"   {rec['url']}")
    print("\nGuten Appetit!")

if __name__ == "__main__":
    main()
