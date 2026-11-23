"""Build docs/week-NN/index.html from templates/week-NN.html.

Usage:
  python build.py 01              # questions + hints only (solutions locked)
  python build.py 01 --solutions  # release solutions + takeaways (the following week)

Solutions live in solutions/ (gitignored, never pushed):
  solutions/week-NN-<theme>.sql      SQL answers, split by `-- QN ---` markers
  solutions/week-NN-takeaways.json   [{"en": [...], "pt": [...]}, ...] one entry per question

When locked, the page gets `null` for both, so no answers end up in the HTML.
A locked build doesn't need the solutions/ files at all.
"""
import glob, json, sys

args = [a for a in sys.argv[1:] if not a.startswith("--")]
wk = args[0] if args else "01"
release = "--solutions" in sys.argv

html = open(f"templates/week-{wk}.html", encoding="utf-8").read()

if release:
    sql_file = [f for f in glob.glob(f"solutions/week-{wk}-*.sql")][0]
    parts = open(sql_file, encoding="utf-8").read().split("-- Q")[1:]
    solutions = [p.split("\n", 1)[1].strip() for p in parts]
    takeaways = json.load(open(f"solutions/week-{wk}-takeaways.json", encoding="utf-8"))
    assert len(solutions) == len(takeaways), f"{len(solutions)} solutions vs {len(takeaways)} takeaways"
    sol_js = json.dumps(solutions, ensure_ascii=False, indent=1)
    take_js = json.dumps(takeaways, ensure_ascii=False, indent=1)
    state = f"{len(solutions)} solutions RELEASED"
else:
    sol_js = take_js = "null"
    state = "solutions LOCKED (hints only)"

html = html.replace("__SOLUTIONS__", sol_js).replace("__TAKEAWAYS__", take_js)
open(f"docs/week-{wk}/index.html", "w", encoding="utf-8").write(html)
print(f"built docs/week-{wk}/index.html: {state}")
