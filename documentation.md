# Leftover Chef – Documentation

## 1. Problem & Goal
Reduce food waste and save time: enter up to three ingredients you already have, receive ranked recipes with direct links.

## 2. Approach & Architecture
- **Ingredient validation**: English-only vocabulary pulled from TheMealDB (`list.php?i=list`).
- **Normalization**: lowercase + simple plural→singular; fuzzy match for close typos.
- **Retrieval**: for each valid ingredient, fetch meal IDs; prefer intersection, else union ranked by coverage.
- **Scoring**: overlap-based score (+ optional weights for fresh produce).
- **Filters**:
  - Vegan: excludes meat, seafood, dairy, eggs, animal derivatives
  - Vegetarian: excludes meat and seafood
  - Auto-detect: if inputs contain any of those, skip asking
- **Persistence**: favorites saved to `data/favorites.json`, optional CSV export.

## 3. Setup & Run
- Python 3.9+
- `pip install -r requirements.txt`
- `python -m spacy download en_core_web_sm`
- `python title.py`

## 4. User Flow
1. User types up to **3** ingredients (English).
2. App validates against API vocabulary; invalid entries get suggestions.
3. Diet prompts (skipped automatically if input already non-vegan).
4. Show **Top matches** (1–10), direct recipe links, optional missing-ingredient hints.
5. User can save favorites.

## 5. Key Design Decisions
- **Single reliable source** (TheMealDB) for consistent schema and links.
- **Strict English validation** to avoid random words (chair, book, …).
- **Intersection-first** keeps relevance high; union fallback avoids empty results.
- **Auto diet detection** improves UX.

## 6. Limitations & Future Work
- API coverage varies by ingredient naming; consider synonym tables or multiple sources.
- Optional caching for ingredient list to reduce startup latency.
- GUI (Streamlit) as a future enhancement.
- More tests (integration tests for API responses).

## 7. Testing
- Unit tests in `tests/` for normalization, filters, and scoring.
- Manual tests for typical inputs:
  - `tomato, onion` → vegetarian/vegan prompts
  - `chicken` → prompts skipped
  - invalid words → suggestions and retry

## 8. References
- TheMealDB API (free, public) – used for ingredient vocabulary and recipe details.
