import requests, difflib
from typing import List, Dict, Any, Optional, Set, Tuple

BASE = "https://www.themealdb.com/api/json/v1/1"

def _get(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    r = requests.get(url, params=params, timeout=20, headers={"User-Agent": "LeftoverChef/1.0"})
    r.raise_for_status()
    return r.json()

def _singular(tok: str) -> str:
    if tok.endswith("ies") and len(tok) > 3:
        return tok[:-3] + "y"
    if tok.endswith("es") and len(tok) > 2:
        return tok[:-2]
    if tok.endswith("s") and len(tok) > 1:
        return tok[:-1]
    return tok

def _load_ingredient_vocab() -> Set[str]:
    data = _get(f"{BASE}/list.php", {"i": "list"})
    items = data.get("meals") or []
    vocab = set()
    for it in items:
        name = (it.get("strIngredient") or "").strip().lower()
        if name:
            vocab.add(name)
    return vocab

ING_VOCAB = _load_ingredient_vocab()

def validate_to_vocab(raw_tokens: List[str]) -> Tuple[List[str], List[str], Dict[str, str]]:
    valid: List[str] = []
    invalid: List[str] = []
    suggest: Dict[str, str] = {}
    seen = set()
    for t in raw_tokens:
        t0 = t.strip().lower()
        if not t0:
            continue
        t1 = _singular(t0)
        if t1 in ING_VOCAB and t1 not in seen:
            valid.append(t1); seen.add(t1); continue
        cand = difflib.get_close_matches(t1, list(ING_VOCAB), n=1, cutoff=0.86)
        if cand and cand[0] not in seen:
            valid.append(cand[0]); seen.add(cand[0])
        else:
            invalid.append(t)
            m = difflib.get_close_matches(t1, list(ING_VOCAB), n=1, cutoff=0.6)
            if m:
                suggest[t] = m[0]
    return valid, invalid, suggest

def filter_by_ingredient(ingredient: str) -> List[Dict[str, Any]]:
    data = _get(f"{BASE}/filter.php", {"i": ingredient})
    return data.get("meals") or []

def lookup_meal(meal_id: str) -> Optional[Dict[str, Any]]:
    data = _get(f"{BASE}/lookup.php", {"i": meal_id})
    meals = data.get("meals") or []
    return meals[0] if meals else None

def _meal_to_app(m: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    url = (m.get("strSource") or "").strip()
    if not url:
        return None
    ings = []
    for i in range(1, 21):
        name = (m.get(f"strIngredient{i}") or "").strip()
        if name:
            ings.append(name.lower())
    return {
        "title": m.get("strMeal") or "",
        "ingredients": ings,
        "url": url,
        "id": m.get("idMeal") or "",
        "area": m.get("strArea") or "",
        "category": m.get("strCategory") or "",
    }

def search_by_ingredients(ingredients: List[str], max_ids: int = 50) -> List[Dict[str, Any]]:
    if not ingredients:
        return []
    result_sets = []
    id_counts: Dict[str, int] = {}
    for token in ingredients:
        meals = filter_by_ingredient(token)
        ids = {m["idMeal"] for m in meals}
        result_sets.append(ids)
        for mid in ids:
            id_counts[mid] = id_counts.get(mid, 0) + 1
    if not any(result_sets):
        return []
    common_ids = set.intersection(*result_sets) if len(result_sets) > 1 else result_sets[0]
    if common_ids:
        ids_ordered = list(common_ids)[:max_ids]
    else:
        ids_ordered = [mid for mid, _ in sorted(id_counts.items(), key=lambda kv: (-kv[1], kv[0]))][:max_ids]
    detailed = []
    for meal_id in ids_ordered:
        m = lookup_meal(meal_id)
        if not m:
            continue
        app = _meal_to_app(m)
        if app:
            detailed.append(app)
    return detailed
