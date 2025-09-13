import sys, json, csv, time
from pathlib import Path
from typing import List, Dict
from helper import normalize_and_expand, score_recipe, recipe_matches_filters, missing_ingredients, DEFAULT_WEIGHTS
from api_client import search_by_ingredients

DATA_PATH = Path("data/recipes.json")
FAV_PATH = Path("data/favorites.json")

def yesno_strict(prompt: str, default_yes: bool = True) -> bool:
    default = "yes" if default_yes else "no"
    ans = input(f"{prompt} (yes/no, Enter = {default}): ").strip().lower()
    if ans == "":
        return default_yes
    if ans in {"y","yes"}:
        return True
    if ans in {"n","no"}:
        return False
    print("Input error: please answer 'yes' or 'no' only. Exiting.")
    sys.exit(2)

def ask_int_strict(prompt: str, default: int, min_v: int, max_v: int) -> int:
    raw = input(f"{prompt} (integer {min_v}-{max_v}, Enter = {default}): ").strip()
    if raw == "":
        return default
    try:
        v = int(raw)
    except ValueError:
        print("Input error: please enter a whole number. Exiting.")
        sys.exit(2)
    if not (min_v <= v <= max_v):
        print(f"Input error: value must be between {min_v} and {max_v}. Exiting.")
        sys.exit(2)
    return v

def parse_ingredients(raw: str, max_n: int = 3) -> List[str]:
    toks = [t for t in (x.strip() for x in raw.split(",")) if t]
    if len(toks) > max_n:
        print(f"Note: I will use only the first {max_n} ingredients: {', '.join(toks[:max_n])}")
        toks = toks[:max_n]
    return toks

def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def print_header(title: str):
    line = "─" * max(24, len(title) + 4)
    print(f"\n┌{line}┐")
    print(f"│  {title}  │")
    print(f"└{line}┘")

def print_table(rows: List[Dict], start_index: int = 1):
    if not rows:
        print("No matches found.\n")
        return
    w_idx = len(str(start_index + len(rows) - 1))
    w_score = 6
    w_title = max(12, min(56, max(len(r['title']) for r in rows)))
    print(f"{'No.':>{w_idx}}  {'Score':>{w_score}}  {'Title':<{w_title}}  URL  Missing")
    print("-" * (w_idx + w_score + w_title + 14))
    for i, r in enumerate(rows, start_index):
        url = r['url'] or ""
        print(f"{i:>{w_idx}}  {r['score']:>{w_score}.2f}  {r['title']:<{w_title}}  {url}  {r['missing']}")

def rank_and_filter(recipes: List[Dict], user_tokens: List[str], vegan: bool, vegetarian: bool, gluten_free: bool, prioritize_fresh: bool, show_hints: bool) -> List[Dict]:
    expanded = normalize_and_expand(user_tokens)
    weights = DEFAULT_WEIGHTS if prioritize_fresh else None
    out = []
    for r in recipes:
        if not recipe_matches_filters(r.get("ingredients", []), vegetarian=vegetarian, vegan=vegan, gluten_free=gluten_free):
            continue
        r_ings = normalize_and_expand(r.get("ingredients", []))
        s = score_recipe(expanded, r_ings, weights=weights)
        hints = ", ".join(missing_ingredients(expanded, r_ings, k=3)) if show_hints else ""
        out.append({"score": s, "title": r.get("title",""), "url": r.get("url",""), "missing": hints})
    out.sort(key=lambda x: (-x["score"], x["title"].lower()))
    return out

def paginate(rows: List[Dict], page_size: int):
    for i in range(0, len(rows), page_size):
        yield i, rows[i:i+page_size]

def favorites_load() -> List[Dict]:
    return load_json(FAV_PATH, [])

def favorites_save(picks: List[Dict]):
    existing = favorites_load()
    seen = {(x.get("url",""), x.get("title","").lower()) for x in existing}
    for p in picks:
        key = (p.get("url",""), p.get("title","").lower())
        if key not in seen:
            existing.append(p)
            seen.add(key)
    save_json(FAV_PATH, existing)

def favorites_view():
    items = favorites_load()
    print_header("Favorites")
    if not items:
        print("No favorites yet.")
        return
    print_table(items)

def favorites_remove_by_index():
    items = favorites_load()
    if not items:
        print("No favorites to remove.")
        return
    print_table(items)
    raw = input("Enter indices to remove (e.g., 1,3) or press Enter to cancel: ").strip()
    if not raw:
        return
    idxs = []
    for t in (x.strip() for x in raw.split(",")):
        if t.isdigit():
            idxs.append(int(t))
    keep = []
    for i, row in enumerate(items, 1):
        if i not in idxs:
            keep.append(row)
    save_json(FAV_PATH, keep)
    print("Updated favorites.")

def favorites_export_csv():
    items = favorites_load()
    if not items:
        print("No favorites to export.")
        return
    path = Path("data/favorites.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["title","url","score","missing"])
        w.writeheader()
        for r in items:
            w.writerow({"title": r.get("title",""), "url": r.get("url",""), "score": r.get("score",""), "missing": r.get("missing","")})
    print(f"Exported to {path}")

def menu_favorites():
    while True:
        print("\nFavorites menu: [v]iew, [r]emove, e[x]port csv, [b]ack")
        ans = input("Choose: ").strip().lower()
        if ans in {"v","view"}:
            favorites_view()
        elif ans in {"r","remove"}:
            favorites_remove_by_index()
        elif ans in {"x","export"}:
            favorites_export_csv()
        elif ans in {"b","back",""}:
            return
        else:
            print("Unknown option.")

def fetch_recipes(user_tokens: List[str]) -> List[Dict]:
    try:
        time.time()
        api_data = search_by_ingredients(user_tokens)
        if api_data:
            return api_data
        local = load_json(DATA_PATH, [])
        return local
    except Exception:
        local = load_json(DATA_PATH, [])
        return local

def show_results_and_save(ranked: List[Dict], page_size: int):
    if not ranked:
        print("No matches found.")
        return
    page_gen = list(paginate(ranked, page_size))
    page = 0
    while True:
        start_idx, chunk = page_gen[page]
        print_header(f"Top matches (page {page+1}/{len(page_gen)})")
        print_table(chunk, start_index=start_idx+1)
        ans = input("\nOptions: [s]ave indices, [n]ext, [p]rev, [f]avorites menu, [q]uit results: ").strip().lower()
        if ans in {"s","save"}:
            pick = input("Enter indices to save (e.g., 1,3) or press Enter to cancel: ").strip()
            if pick:
                idxs = []
                for t in (x.strip() for x in pick.split(",")):
                    if t.isdigit():
                        idxs.append(int(t))
                to_save = []
                for global_idx in idxs:
                    if 1 <= global_idx <= len(ranked):
                        to_save.append(ranked[global_idx-1])
                favorites_save(to_save)
                print(f"Saved {len(to_save)} favorite(s).")
        elif ans in {"n","next"}:
            if page < len(page_gen)-1:
                page += 1
            else:
                print("No next page.")
        elif ans in {"p","prev"}:
            if page > 0:
                page -= 1
            else:
                print("No previous page.")
        elif ans in {"f","fav","favorites"}:
            menu_favorites()
        elif ans in {"q","quit",""}:
            break
        else:
            print("Unknown option.")

def main():
    print_header("Leftover Chef")
    print("Enter up to 3 ingredients you already have, separated by commas.")
    print("Example: eggs, cheese, onion")
    while True:
        raw = input("\nWhat do you have? (empty to quit) ").strip()
        if not raw:
            break
        user_tokens = parse_ingredients(raw, max_n=3)
        vegan = yesno_strict("Are you vegan?", default_yes=False)
        vegetarian = False if vegan else yesno_strict("Are you vegetarian?", default_yes=False)
        gluten_free = yesno_strict("Are you gluten-free?", default_yes=False)
        prioritize_fresh = yesno_strict("Should I prioritize fresh ingredients when ranking (this can change the order)?", default_yes=True)
        top_n = ask_int_strict("How many recipes should I show", default=10, min_v=1, max_v=50)
        show_hints = yesno_strict("Show up to 3 missing ingredients per recipe (so you know what else you'd need)?", default_yes=True)
        page_size = ask_int_strict("Recipes per page", default=min(10, top_n), min_v=1, max_v=max(10, top_n))
        src = fetch_recipes(user_tokens)
        ranked = rank_and_filter(src, user_tokens, vegan, vegetarian, gluten_free, prioritize_fresh, show_hints)
        ranked = ranked[:top_n]
        show_results_and_save(ranked, page_size)

if __name__ == "__main__":
    main()