# 🍽️ Leftover Chef

Leftover Chef turns the ingredients you already have into instant dinner ideas.  
Just type up to **three ingredients** and get a ranked list of real recipes with direct links — saving time, money, and reducing food waste.

## ✨ What it does

- **Ingredient validation** – only real ingredients are accepted  
- **Smart matching** – recipes ranked by how many of your ingredients they use  
- **Diet filters** – vegan/vegetarian filters available *(skips automatically if you already typed meat, fish, eggs, or dairy)*  
- **Direct links** – jump straight to the recipe page  
- **Favorites** – save your favorite recipes for later  

## 🚀 Quick Start

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python title.py
```

---

## ⚡ How to use it

```bash
python title.py
```

When prompted, enter your ingredients (up to three) like: 

```
pasta, onion, garlic
```

- Choose vegan/vegetarian options
- Select how many recipes to display
- Decide whether to show missing ingredients


Leftover Chef will print a ranked list of matching recipes and direct links.

## Enjoy finding dinner ideas in seconds!
