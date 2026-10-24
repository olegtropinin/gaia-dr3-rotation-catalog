"""Which tier-A new candidates already have a published period (VizieR rotation tables, MPB, DAMIT).

A VizieR hit counts only when the asteroid is matched in an identifier column (not LCNum/recno/...) and the
row carries a non-empty period. Writes published_tierA.json and ../new_candidates_A_novel.csv.
"""
import csv, json, re
cand = {c["num"]: c for c in json.load(open("candidates68.json"))}
names = {c["name"].lower().replace(" ", "").replace("_", ""): n for n, c in cand.items() if c["name"]}
PER = re.compile(r"^(Per|Period|Prot|P|Psyn|Psid|Per1|Trot|Prot1|Ps)$", re.I)
IDC = re.compile(r"^(Num|Number|No|MPC|Name|Ast|Asteroid|Object|ID|Desig|Design|SSO|MP|Nb|AstNum|Number_mp|Planet|Target|Seq)$", re.I)
NOT_ID = re.compile(r"(LCNum|recno|Nobs|Npts|Night|Ref)", re.I)


def num_of(rec):
    for k, v in rec.items():
        if not IDC.match(k) or NOT_ID.search(k):
            continue
        v = (v or "").strip()
        m = re.match(r"^\(?(\d+)\)?$", v)
        if m and int(m.group(1)) in cand:
            return int(m.group(1))
        key = re.sub(r"[()\s_]", "", v).lower()
        if key in names:
            return names[key]
    return None


# column metadata from TAP_SCHEMA (unit, description): a period column counts only if it is a rotation period,
# and its value is converted to hours (Liberato+2024 'Per' is an astrometric wobble period; Erasmus+2019 is in minutes)
meta = json.load(open("hit_table_columns.json"))
TO_H = {"h": 1.0, "min": 1 / 60, "d": 24.0, "s": 1 / 3600}
found = {}
for f in ("novelty_vizier.json", "novelty_catalogs.json"):
    for t, rows in json.load(open(f))["hits"].items():
        for rec in rows:
            pk = [k for k in rec if PER.match(k) and (rec[k] or "").strip() not in ("", "nan", "NaN")]
            pk = [k for k in pk if "wobble" not in meta.get(t, {}).get(k, {}).get("desc", "").lower()
                  and "orbit" not in meta.get(t, {}).get(k, {}).get("desc", "").lower()]
            n = num_of(rec) if pk else None
            if n:
                unit = meta.get(t, {}).get(pk[0], {}).get("unit", "h")
                try:
                    val = str(round(float(rec[pk[0]]) * TO_H.get(unit, 1.0), 6))
                except ValueError:
                    continue
                found.setdefault(n, []).append((t, val))
mpb = {int(x) for x in json.load(open("mpb_hits.json"))}
damit = set(json.load(open("damit_hits.json")))
A = {int(r["number"]): r for r in csv.DictReader(open("../new_candidates.csv"))}
fa = {n for n in A if n in found}
pub = fa | {n for n in A if n in mpb} | {n for n in A if n in damit}
print(f"tier-A new {len(A)}: VizieR {len(fa)}, MPB {sum(n in mpb for n in A)}, DAMIT {sum(n in damit for n in A)} "
      f"-> already published {len(pub)}, novel {len(A) - len(pub)}")
tabs = {}
agree = 0
for n in fa:
    for t, p in found[n]:
        tabs[t] = tabs.get(t, 0) + 1
    agree += any(float(p) > 0 and abs(float(A[n]["period_h"]) - float(p)) / float(p) < 0.03 for t, p in found[n] if re.match(r"^[\d.]+$", p))
print("tables:", sorted(tabs.items(), key=lambda x: -x[1])[:12])
print(f"agree with a published VizieR period (3 %): {agree}/{len(fa)}")
json.dump(sorted(pub), open("published_tierA.json", "w"))
json.dump({str(n): [p for t, p in v] for n, v in found.items()}, open("published_periods.json", "w"))
with open("../new_candidates_A_novel.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=next(iter(A.values())).keys()); w.writeheader()
    w.writerows(r for n, r in A.items() if n not in pub)
