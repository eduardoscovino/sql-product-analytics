# SQL for Product Analytics

A weekly series of hands-on SQL cases for product analytics. Each week has one business case with 8 questions of increasing difficulty (aggregations → JOINs → subqueries → window functions), written for PMs, POs and junior analysts, and you solve it in an interactive SQL playground that runs entirely in the browser (SQLite compiled to WebAssembly via [sql.js](https://github.com/sql-js/sql.js)). Nothing to install, no account needed.

**▶ Play:** `https://<your-user>.github.io/sql-product-analytics/`

| Week | Theme | Playground |
|------|-------|------------|
| 01 | The Signup Funnel: traffic, channel quality, onboarding impact, goal tracking | [`docs/week-01`](docs/week-01/) |

## Repository layout

```
docs/                  # published by GitHub Pages
  index.html           # series landing page (PT/EN)
  week-01/             # self-contained playground: page + engine + data
templates/             # page source per week (case text + questions, PT/EN)
solutions/             # answers: SQL + takeaways (gitignored, local only until release)
generators/            # Python scripts that create each week's synthetic data
build.py               # python build.py 01 -> docs/week-01/index.html (solutions locked)
                       # python build.py 01 --solutions  (release week: solutions published)
```

## Adding a new week
1. Write `generators/weekNN_<theme>.py` and run it to produce the CSVs.
2. Copy `templates/week-01.html` to `templates/week-NN.html`, edit the case and the `Q` array, write `solutions/week-NN-<theme>.sql` and `solutions/week-NN-takeaways.json`, put the CSVs + `sql-wasm.*` in `docs/week-NN/`, and run `python build.py NN`.
3. Add the week to `docs/index.html` and to the table above.

## Run locally
```bash
cd docs && python -m http.server 8000
# open http://localhost:8000
```
(Opening `index.html` directly from disk won't work: browsers block `fetch()` on `file://`.)

---
Data is synthetic and generated for teaching. Companies in the cases are fictional.
