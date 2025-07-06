def score_recipe(my_ingredients, recipe_ingredients):
    return len(set(my_ingredients) & set(recipe_ingredients))
