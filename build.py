"""Build docs/week-NN/index.html from templates/week-NN.html + solutions/week-NN-*.sql.
Usage: python build.py 01
"""
import glob, json, sys

wk = sys.argv[1] if len(sys.argv) > 1 else "01"
sql_file = glob.glob(f"solutions/week-{wk}-*.sql")[0]
parts = open(sql_file, encoding="utf-8").read().split("-- Q")[1:]
solutions = [p.split("\n", 1)[1].strip() for p in parts]
html = open(f"templates/week-{wk}.html", encoding="utf-8").read()
html = html.replace("__SOLUTIONS__", json.dumps(solutions, ensure_ascii=False, indent=1))
open(f"docs/week-{wk}/index.html", "w", encoding="utf-8").write(html)
print(f"built docs/week-{wk}/index.html with {len(solutions)} solutions")
