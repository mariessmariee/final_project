from helper import score_recipe, normalize_and_expand

def test_score_basic():
    s1 = score_recipe(["pasta","tomato"], ["pasta","tomato","garlic"])
    s2 = score_recipe(["pasta"], ["pasta","tomato","garlic"])
    assert s1 > s2

def test_synonym_and_lemma():
    u = normalize_and_expand(["scallions"])
    assert any(x in u for x in ["scallion", "green onion", "spring onion"])
