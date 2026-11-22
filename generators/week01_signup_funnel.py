"""Synthetic signup-funnel dataset for week 1 (fictional app "Trilha").
Planted signals:
- paid_social: lots of signups, weak activation
- referral: best end-to-end conversion
- onboarding v2 released 2026-10-15 -> higher, faster activation
- ~3% duplicated signup events (data-quality trap)
- data snapshot 2026-11-16 -> late cohorts are immature
"""
import random, sqlite3, os
from datetime import datetime, timedelta

import sys; random.seed(int(sys.argv[1]) if len(sys.argv)>1 else 42)
START = datetime(2026, 9, 1)
END = datetime(2026, 11, 15, 23, 59)
SNAPSHOT = datetime(2026, 11, 16)
V2 = datetime(2026, 10, 15)

channels = {  # weight, p_signup, p_activate, p_purchase
    "organic":     (0.35, 0.22, 0.50, 0.30),
    "paid_search": (0.25, 0.25, 0.47, 0.26),
    "paid_social": (0.28, 0.33, 0.28, 0.14),
    "referral":    (0.12, 0.38, 0.62, 0.40),
}
devices = [("mobile", 0.62), ("desktop", 0.38)]
countries = [("BR", 0.55), ("MX", 0.15), ("AR", 0.12), ("CO", 0.10), ("CL", 0.08)]

def pick(pairs):
    r, acc = random.random(), 0
    for k, w in pairs:
        acc += w
        if r <= acc:
            return k
    return pairs[-1][0]

users, events = [], []
eid = 0
def add(uid, name, ts):
    global eid
    if ts <= SNAPSHOT:
        eid += 1
        events.append((eid, uid, name, ts.strftime("%Y-%m-%d %H:%M:%S")))

total_seconds = int((END - START).total_seconds())
N = 9000
for uid in range(1, N + 1):
    ch = pick([(k, v[0]) for k, v in channels.items()])
    _, ps, pa, pp = channels[ch]
    dev = pick(devices)
    ctry = pick(countries)
    first = START + timedelta(seconds=random.randint(0, total_seconds))
    users.append((uid, first.strftime("%Y-%m-%d %H:%M:%S"), ch, dev, ctry))
    add(uid, "landing_view", first)
    # extra visits (noise)
    for _ in range(random.choice([0, 0, 0, 1, 2])):
        add(uid, "landing_view", first + timedelta(hours=random.uniform(1, 240)))
    if dev == "mobile":
        ps *= 0.92
    if random.random() > ps:
        continue
    su = first + timedelta(minutes=random.expovariate(1 / 45))
    if random.random() < 0.15:
        su += timedelta(days=random.uniform(1, 10))  # came back later
    add(uid, "signup", su)
    if random.random() < 0.03:  # duplicated tracking event
        add(uid, "signup", su + timedelta(seconds=random.randint(1, 5)))
    v2 = su >= V2
    pa_eff = min(pa * (1.28 if v2 else 1.0), 0.95)
    if random.random() > pa_eff:
        continue
    mean_h = 20 if v2 else 44
    act = su + timedelta(hours=random.expovariate(1 / mean_h))
    add(uid, "onboarding_complete", act)
    if random.random() > pp:
        continue
    pur = act + timedelta(days=random.expovariate(1 / 4))
    add(uid, "first_purchase", pur)

events.sort(key=lambda e: e[3])
events = [(i + 1, u, n, t) for i, (_, u, n, t) in enumerate(events)]

os.makedirs("data", exist_ok=True)
db = "data/trilha_funnel.db"
if os.path.exists(db):
    os.remove(db)
con = sqlite3.connect(db)
con.executescript("""
CREATE TABLE users (
  user_id INTEGER PRIMARY KEY,
  first_seen_at TEXT NOT NULL,
  acquisition_channel TEXT NOT NULL,
  device TEXT NOT NULL,
  country TEXT NOT NULL
);
CREATE TABLE events (
  event_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(user_id),
  event_name TEXT NOT NULL,
  event_at TEXT NOT NULL
);
""")
con.executemany("INSERT INTO users VALUES (?,?,?,?,?)", users)
con.executemany("INSERT INTO events VALUES (?,?,?,?)", events)
con.execute("CREATE INDEX ix_ev_user ON events(user_id, event_name, event_at)")
con.commit()
con.execute("VACUUM")
con.close()

import csv
for name, rows, hdr in [("users", users, ["user_id","first_seen_at","acquisition_channel","device","country"]),
                        ("events", events, ["event_id","user_id","event_name","event_at"])]:
    with open(f"data/{name}.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(hdr); w.writerows(rows)
print(len(users), "users", len(events), "events")
