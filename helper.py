 import spacy
    _NLP = spacy.load("en_core_web_sm", disable=["ner", "parser"])
    _USE_SPACY = True
except Exception:
    _NLP = None
    _USE_SPACY = False

_SYNONYMS = {
    "scallion": {"green onion", "spring onion"},
    "garbanzo": {"chickpea", "chickpeas"},
    "coriander": {"cilantro"},
    "bell pepper": {"capsicum"},
    "courgette": {"zucchini"},
    "aubergine": {"eggplant"}
}

DEFAULT_WEIGHTS = {
    "spinach": 1.3, "herb": 1.2, "basil": 1.2, "cilantro": 1.2, "coriander": 1.2,
    "lemon": 1.2, "zucchini": 1.2, "eggplant": 1.2, "aubergine": 1.2,
    "bell pepper": 1.1, "capsicum": 1.1,
    "cheese": 0.9, "butter": 0.9, "olive oil": 0.9
}

def _normalize_raw_list(items):
    return [x.strip().lower() for x in items if isinstance(x, str) and x.strip()]

def _simple_lemma(token: str) -> str:
    if token.endswith("ies") and len(token) > 3:
        return token[:-3] + "y"
    if token.endswith("es") and len(token) > 2:
        return token[:-2]
    if token.endswith("s") and len(token) > 1:
        return token[:-1]
    return token

def lemmatize(tokens):
    if _USE_SPACY:
        doc = _NLP(" , ".join(tokens))
        return [t.lemma_.lower().strip() for t in doc if not t.is_space and t.is_alpha]
    return [_simple_lemma(t) for t in tokens]

def expand_synonyms(tokens):
    expanded = set(tokens)
    for t in list(tokens):
        for k, vals in _SYNONYMS.items():
            if t == k or t in vals:
                expanded.add(k)
                expanded |= set(vals)
    return sorted(expanded)

def normalize_and_expand(raw_tokens):
    base = _normalize_raw_list(raw_tokens)
    lemmas = lemmatize(base)
    expanded = expand_synonyms(lemmas)
    return sorted(set(expanded))

_MEAT = {"chicken","beef","pork","bacon","ham","turkey","fish","salmon","tuna","shrimp","chorizo"}
_DAIRY = {"milk","cheese","butter","yogurt","cream"}
_GLUTEN = {"wheat","flour","pasta","bread","noodle","noodles"}

def recipe_matches_filters(recipe_ings: list[str], vegetarian=False, vegan=False, gluten_free=False) -> bool:
    ings = set(normalize_and_expand(recipe_ings))
    if vegan:
        if _MEAT & ings:
            return False
        if _DAIRY & ings:
            return False
        if "egg" in ings:
            return False
    elif vegetarian:
        if _MEAT & ings:
            return False
    if gluten_free:
        if _GLUTEN & ings:
            return False
    return True

def score_recipe(user_ings, recipe_ings, weights=None):
    u = set(user_ings)
    base = 0.0
    for ing in set(recipe_ings):
        if ing in u:
            w = 1.0 if not weights else float(weights.get(ing, 1.0))
            base += w
    recall = base / max(len(set(recipe_ings)), 1)
    precision = base / max(len(u), 1)
    f1 = 0.0 if (precision + recall) == 0 else 2 * (precision * recall) / (precision + recall)
    return round(base + f1, 3)

def missing_ingredients(user_ings: list[str], recipe_ings: list[str], k: int = 3) -> list[str]:
    u = set(user_ings)
    miss = [ing for ing in recipe_ings if ing not in u]
    return miss[:k]