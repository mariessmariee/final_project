import requests
from typing import List, Dict, Any, Optional

BASE = "https://www.themealdb.com/api/json/v1/1"

def _get(url: str, params: dict | None = None) -> dict:
    r = requests.get(url, params=params, timeout=20, headers={"User-Agent": "LeftoverChef/1.0"})
    r.raise_for_status()
    return r.json()

def filter_by_ingredient(ingredient: str) -> List[Dict[str, Any]]:
    data = _get(f"{BASE}/filter.php", {"i": ingredient})
    meals = data.get("meals") or []
    return meals

def lookup_meal(meal_id: str) -> Optional[Dict[str, Any]]:
    data = _get(f"{BASE}/lookup.php", {"i": meal_id})
    meals = data.get("meals") or []
    return meals[0] if meals else None

def search_by_ingredients(ingredients: List[str], max_ids: int = 50) -> List[Dict[str, Any]]:
    ing = [x.strip().lower() for x in ingredients if x.strip()]
    if not ing:
        return []
    result_sets = []
    for token in ing:
        meals = filter_by_ingredient(token)
        result_sets.append({m["idMeal"] for m in meals})
    common_ids = set.intersection(*result_sets) if result_sets else set()
    if not common_ids and len(result_sets) == 1:
        common_ids = result_sets[0]
    ids = list(common_ids)[:max_ids]
    detailed = []
    for meal_id in ids:
        m = lookup_meal(meal_id)
        if not m:
            continue
        detailed.append(_meal_to_app(m))
    return detailed

def _meal_to_app(m: Dict[str, Any]) -> Dict[str, Any]:
    ings = []
    for i in range(1, 21):
        name = (m.get(f"strIngredient{i}") or "").strip()
        if name:
            ings.append(name.lower())
    url = m.get("strSource") or m.get("strYoutube") or ""
    return {
        "title": m.get("strMeal") or "",
        "ingredients": ings,
        "url": url,
        "id": m.get("idMeal") or "",
        "area": m.get("strArea") or "",
        "category": m.get("strCategory") or "",
    }
