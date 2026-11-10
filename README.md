# Outfit Swipe

Mobile-first swipe deck (Tinder-style) to calibrate a personal menswear style.
Right = like, left = nope, up = love. Optional note per card. Progress saved in localStorage.
"Resultados" → "Copiar resultados" gives compact JSON `[{id, verdict, note?}]`.

- `data.json` — 193 outfits with source, lanes, and 22–40 `facet:value` tags each.
- `vocab.json` — controlled vocabulary of tag facets/values.
- `analyze.py` — `python3 analyze.py results.json` → like-rate per tag, strong yes/no, LIKE∩NOPE overlap.

Images are public outfit photos collected for personal style research; each entry links to its source.
