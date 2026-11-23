"""Build docs/week-NN/index.html from templates/week-NN.html + solutions/week-NN-*.sql.

Usage:
  python build.py 01              # questions + hints only (solutions locked)
  python build.py 01 --solutions  # release solutions + takeaways (the following week)

When locked, neither the SQL nor the takeaways are written to the HTML,
so they can't be found by viewing the page source.
"""
import glob, json, re, sys

args = [a for a in sys.argv[1:] if not a.startswith("--")]
wk = args[0] if args else "01"
release = "--solutions" in sys.argv

sql_file = glob.glob(f"solutions/week-{wk}-*.sql")[0]
parts = open(sql_file, encoding="utf-8").read().split("-- Q")[1:]
solutions = [p.split("\n", 1)[1].strip() for p in parts]
html = open(f"templates/week-{wk}.html", encoding="utf-8").read()

if release:
    html = html.replace("__SOLUTIONS__", json.dumps(solutions, ensure_ascii=False, indent=1))
else:
    html = html.replace("__SOLUTIONS__", "null")
    # drop each question's takeaways: `,\n  take:{en:[...],\n pt:[...]}` (closes right before the question's `}`)
    html, n = re.subn(r",\s*take:\{en:\[.*?\]\}(?=\})", "", html, flags=re.S)
    assert n == len(solutions), f"stripped {n} takeaway blocks, expected {len(solutions)}"

open(f"docs/week-{wk}/index.html", "w", encoding="utf-8").write(html)
state = f"{len(solutions)} solutions RELEASED" if release else "solutions LOCKED (hints only)"
print(f"built docs/week-{wk}/index.html: {state}")
