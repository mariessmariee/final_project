import sys, json
from pathlib import Path
from typing import List, Dict
from helper import normalize_and_expand, score_recipe, recipe_matches_filters, missing_ingredients, DEFAULT_WEIGHTS
from api_client import search_by_ingredients

FAV_PATH = Path("data/favorites.json")

def yesno_strict(prompt: str) -> bool:
    ans = input(f"{prompt} (yes/no): ").strip().lower()
    if ans in {"y","yes"}:
        return True
    if ans in {"n","no"}:
        return False
    print("Input error: please answer 'yes' or 'no'. Exiting.")
    sys.exit(2)

def ask_int_1_10(prompt: str) -> int:
    raw = input(f"{prompt} (1-10): ").strip()
    if not raw.isdigit():
        print("Input error: please enter a number between 1 and 10. Exiting.")
        sys.exit(2)
    v = int(raw)
    if not (1 <= v <= 10):
        print("Input error: value must be between 1 and 10. Exiting.")
        sys.exit(2)
    return v

def parse_ingredients(raw: str, max_n: int = 3) -> List[str]:
    toks = []
    for x in raw.split(","):
        t = x.strip().lower()
        if t and t.replace(" ", "").isalpha() and len(t) >= 2:
            toks.append(t)
    if not toks:
        print("Input error: please enter words like 'tomato, cucumber'. Exiting.")
        sys.exit(2)
    if len(toks) > max_n:
        print(f"Note: I will use only the first {max_n} ingredients: {', '.join(toks[:max_n])}")
        toks = toks[:max_n]
    return toks

def save_favorites(picks: list[dict]):
    FAV_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    try:
        existing = json.loads(FAV_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    by_key = {(x.get("url",""), x.get("title","").lower()): x for x in existing}
    for p in picks:
        key = (p.get("url",""), p.get("title","").lower())
        by_key[key] = p
    FAV_PATH.write_text(json.dumps(list(by_key.values()), ensure_ascii=False, indent=2), encoding="utf-8")

def print_header(title: str):
    line = "─" * max(24, len(title) + 4)
    print(f"\n┌{line}┐")
    print(f"│  {title}  │")
    print(f"└{line}┘")

def print_table(rows: List[Dict]):
    if not rows:
        print("No matches found.\n")
        return
    w_idx = len(str(len(rows)))
    w_score = 6
    w_title = max(12, min(56, max(len(r['title']) for r in rows)))
    print(f"{'#':>{w_idx}}  {'Score':>{w_score}}  {'Title':<{w_title}}  URL  Missing")
    print("-" * (w_idx + w_score + w_title + 14))
    for i, r in enumerate(rows, 1):
        url = r['url'] or ""
        print(f"{i:>{w_idx}}  {r['score']:>{w_score}.2f}  {r['title']:<{w_title}}  {url}  {r['missing']}")

def main():
    print_header("Leftover Chef")
    print("Enter up to 3 ingredients you already have, separated by commas.")
    print("Example: tomato, cucumber or eggs, cheese, onion")
    while True:
        raw = input("\nWhat do you have? (empty to quit) ").strip()
        if not raw:
            break
        user_tokens = parse_ingredients(raw, max_n=3)
        vegan = yesno_strict("Are you vegan?")
        vegetarian = False if vegan else yesno_strict("Are you vegetarian?")
        prioritize_fresh = yesno_strict("Should I prioritize fresh ingredients when ranking?")
        top_n = ask_int_1_10("How many recipes should I show")
        show_hints = yesno_strict("Show up to 3 missing ingredients per recipe?")
        api_recipes = search_by_ingredients(user_tokens)
        if not api_recipes:
            print("No recipes with a webpage source were found for your ingredients.")
            continue
        expanded_for_score = normalize_and_expand(user_tokens)
        weights = DEFAULT_WEIGHTS if prioritize_fresh else None
        ranked = []
        for r in api_recipes:
            if not recipe_matches_filters(r["ingredients"], vegetarian=vegetarian, vegan=vegan, gluten_free=False):
                continue
            r_ings = normalize_and_expand(r["ingredients"])
            s = score_recipe(expanded_for_score, r_ings, weights=weights)
            hints = ", ".join(missing_ingredients(expanded_for_score, r_ings, k=3)) if show_hints else ""
            ranked.append({"score": s, "title": r["title"], "url": r.get("url",""), "missing": hints})
        ranked.sort(key=lambda x: x["score"], reverse=True)
        if not ranked:
            print("No matches found after applying filters.")
            continue
        print_header("Top matches")
        print_table(ranked[:top_n])
        to_save = input("\nSave favorites? Enter indices (e.g., 1,3) or press Enter to skip: ").strip()
        if to_save:
            idxs = []
            for t in (x.strip() for x in to_save.split(",")):
                if t.isdigit():
                    idxs.append(int(t))
            picks = [ranked[i-1] for i in idxs if 1 <= i <= len(ranked)]
            if picks:
                save_favorites(picks)
                print(f"Saved {len(picks)} favorite(s).")

if __name__ == "__main__":
    main()
