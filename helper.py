import spacy

_nlp = None

_SYNONYMS = {
    "scallion": {"green onion", "spring onion"},
    "garbanzo": {"chickpea", "chickpeas"},
    "coriander": {"cilantro"},
    "bell pepper": {"capsicum"},
    "courgette": {"zucchini"},
    "aubergine": {"eggplant"}
}

def _get_nlp():
    """Lazy-load, nur Tokenisierung/Tagging/Lemma nötig."""
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
    return _nlp

def _normalize_raw_list(items):
    return [x.strip().lower() for x in items if isinstance(x, str) and x.strip()]

def lemmatize(tokens):
    """Lemmas als Kleinbuchstaben, nur alphabetische Tokens."""
    if not tokens:
        return []
    doc = _get_nlp()(" , ".join(tokens))
    return [t.lemma_.lower().strip() for t in doc if not t.is_space and t.is_alpha]

def expand_synonyms(tokens):
    """Fügt einfache Synonyme hinzu (Map oben)."""
    expanded = set(tokens)
    for t in list(tokens):
        for k, vals in _SYNONYMS.items():
            if t == k or t in vals:
                expanded.add(k)
                expanded |= set(vals)
    return sorted(expanded)

def normalize_and_expand(raw_tokens):
    """lower -> Lemma -> Synonyme -> unique+sorted."""
    base = _normalize_raw_list(raw_tokens)
    lemmas = lemmatize(base)
    expanded = expand_synonyms(lemmas)
    return sorted(set(expanded))

def score_recipe(user_ings, recipe_ings, weights=None):
    """
    user_ings: Liste[str] (schon normalisiert/expandiert)
    recipe_ings: Liste[str] (schon normalisiert/expandiert)
    weights: optional dict[str,float], z.B. {"garlic": 1.2}
    Rückgabe: float (höher = besser)
    """
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
