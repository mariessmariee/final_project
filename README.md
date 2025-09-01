# 🍽️ Leftover Chef

*Turn random fridge finds into instant dinner ideas.*

Leftover Chef is a Python script that asks what ingredients you have, scrapes a handful of recipe sites, and shows the dishes that use the most of your list, saving you time, money, and food waste.

<p align="center">
  <!-- Drop a GIF or screenshot called demo.gif in media/ to show it off -->
  <img src="media/demo.gif" alt="Leftover Chef demo" width="700">
</p>

---

## ✨ Features
- **Instant suggestions** – type `tomato, onion, pasta…`, get recipes in seconds.  
- **Ingredient scoring** – dishes are ranked by overlap with what you already own.  
- **Portable** – runs anywhere Python 3.8+ is available.

---

## 🚀 Quick start

```bash
# 1 Clone the repo
git clone https://github.com/yourusername/final_project.git
cd final_project

# 2 (optional) Create & activate a virtual environment
python -m venv .venv
source .venv/bin/activate     # Windows ➜ .venv\Scripts\activate

# 3 Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 4 Run it
python title.py
```

---

## ⚡ Usage

```bash
python title.py
```

When prompted, try something like:

```
pasta, onion, garlic, cheese
```

Leftover Chef will print a ranked list of matching recipes and direct links.

