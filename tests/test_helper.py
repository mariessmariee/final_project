from helper import normalize_and_expand, recipe_matches_filters, score_recipe

def test_normalize_and_expand():
    toks = normalize_and_expand(["scallions", "tomatoes"])
    assert "tomato" in toks
    assert any(x in toks for x in ["scallion","green onion","spring onion"])

def test_recipe_matches_filters():
    assert recipe_matches_filters(["tomato","cheese"], vegetarian=True)
    assert not recipe_matches_filters(["chicken","tomato"], vegetarian=True)

def test_score_recipe():
    u = normalize_and_expand(["egg","cheese"])
    r = normalize_and_expand(["cheese","egg"])
    s = score_recipe(u, r)
    assert s > 0
