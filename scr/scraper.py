import argparse, json, sys, re
from pathlib import Path
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup

DATA_PATH = Path("data/recipes.json")

def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()

def _load() -> List[Dict[str, Any]]:
    if DATA_PATH.exists():
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def _save(items: List[Dict[str, Any]]):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def _dedupe(recipes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for r in recipes:
        key = (r.get("url","").strip(), r.get("title","").strip().lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out

def _parse_jsonld(soup: BeautifulSoup):
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        for c in items:
            node = None
            if c.get("@type") == "Recipe" or (isinstance(c.get("@type"), list) and "Recipe" in c["@type"]):
                node = c
            if not node and "@graph" in c:
                for g in c["@graph"]:
                    if g.get("@type") == "Recipe":
                        node = g
                        break
            if not node:
                continue
            title = node.get("name") or node.get("headline")
            ings = node.get("recipeIngredient") or node.get("ingredients")
            if title and ings:
                yield title, ings

def _normalize_ings(ings: List[str]) -> List[str]:
    out = []
    for raw in ings:
        t = _clean(raw)
        t = re.sub(r"\b(\d+([.,]\d+)?)\b", "", t)
        t = re.sub(r"\b(teaspoons?|tsp|tablespoons?|tbsp|cups?|gramm?s?|g|kg|ml|l|ounces?|oz)\b", "", t)
        t = re.sub(r"[^\w\s\-]", " ", t)
        t = re.sub(r"\s+", " ", t).strip()
        tokens = t.split()
        if not tokens:
            continue
        out.append(tokens[-1])
    out = [x for x in out if len(x) >= 2]
    return sorted(list(dict.fromkeys(out)))

def fetch_recipe(url: str) -> Dict[str, Any] | None:
    if "allrecipes.com/recipe/" not in url:
        return None
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
    except Exception as e:
        print(f"[warn] fetch failed {url}: {e}", file=sys.stderr)
        return None
    soup = BeautifulSoup(r.text, "lxml")
    for title, ings in _parse_jsonld(soup):
        ings_norm = _normalize_ings(ings)
        if ings_norm:
            return {"title": title.strip(), "ingredients": ings_norm, "url": url}
    print(f"[warn] no recipe found on {url}", file=sys.stderr)
    return None

def merge(new_items: List[Dict[str,Any]]):
    data = _load()
    merged = _dedupe(data + new_items)
    _save(merged)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", nargs="*")
    ap.add_argument("--file")
    args = ap.parse_args()
    urls = []
    if args.url: urls.extend(args.url)
    if args.file:
        urls.extend([ln.strip() for ln in Path(args.file).read_text(encoding="utf-8").splitlines() if ln.strip()])
    if not urls:
        print("Provide --url ... or --file seed_urls.txt", file=sys.stderr)
        sys.exit(2)
    new_items = []
    for u in urls:
        item = fetch_recipe(u)
        if item:
            print(f"[ok] {item['title']} ({u})")
            new_items.append(item)
    if new_items:
        merge(new_items)
        print(f"[done] merged {len(new_items)} recipes into {DATA_PATH}")

if __name__ == "__main__":
    main()
