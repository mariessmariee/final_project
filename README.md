# Leftover Chef

Turn random leftovers into tasty meals right from your terminal.  
Enter ingredients you have, and Leftover Chef scrapes a few public recipe sites, scores each recipe by ingredient overlap, and shows you the best matches.

---

## Installation

```bash
# clone the repo
git clone https://github.com/<your-username>/final_project.git
cd final_project

# (optional) create & activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows ➜ .venv\Scripts\activate

# install required dependencies
pip install -r requirements.txt
```               <!-- ← THIS closes the Installation code block -->

---

## Usage

```bash
python title.py
```               <!-- ← THIS closes the Usage code block -->

When prompted, type something like:

```
tomato, onion, pasta, cheese
```

Leftover Chef will list the top-scoring recipes and the ingredients they match.

---

## Roadmap

| Feature                         | Status      |
|---------------------------------|-------------|
| Basic CLI & scraping            | **Done**    |
| Smarter ingredient matching     | In progress |
| Save favourite recipes to CSV   | In progress |
| Tiny Flask web UI               | Planned     |

---

*Built for my Python course — happy cooking & coding!*

