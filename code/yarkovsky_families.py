"""Yarkovsky test with Gaia spin senses: in a collisional family, prograde rotators drift outward
(larger proper a) and retrograde inward, so members outside the parent's a should be mostly prograde.

Families and proper elements: AstDyS (Knezevic & Milani; all_tro.members, all.syn, June 2024).
Spin sense: tier-A periods of this catalogue (PAB fit). Centre of a family = proper a of its namesake
(the largest remnant). Statistic: fraction of 'Yarkovsky-consistent' members (prograde outside,
retrograde inside); 0.5 if there is no effect. Binomial tail probability under 0.5.
"""
import csv, glob, json, math, os, collections
import numpy as np

F = "data/families"
prop = {}
for line in open(f"{F}/all.syn"):
    if line.startswith("%"): continue
    p = line.split()
    if p[0].isdigit(): prop[int(p[0])] = (float(p[1]), float(p[2]))          # H, proper a
fam = {}
for line in open(f"{F}/all_tro.members"):
    if line.startswith("%"): continue
    p = line.split()
    if p[0].isdigit() and p[3] != "0": fam[int(p[0])] = int(p[3])
raw = {}
for f in glob.glob("results/*.jsonl"):
    for l in open(f):
        d = json.loads(l); raw[d["num"]] = d
tierA = {int(r["number"]) for r in csv.DictReader(open("catalog.csv")) if r["tier"] == "A"}


def binom_tail(k, n):          # P(X >= k), X ~ Bin(n, 0.5)
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n


per = collections.defaultdict(lambda: [0, 0, 0, 0])   # pro_out, pro_in, ret_out, ret_in
for n in tierA:
    f = fam.get(n)
    if not f or f not in prop or n not in prop or n == f: continue
    s = raw[n].get("sense")
    out = prop[n][1] > prop[f][1]
    per[f][(0 if s == 1 else 2) + (0 if out else 1)] += 1
tot = np.sum(list(per.values()), axis=0)
k, N = int(tot[0] + tot[3]), int(tot.sum())
print(f"all families: members with spin sense {N}; prograde out {tot[0]}, prograde in {tot[1]}, retrograde out {tot[2]}, retrograde in {tot[3]}")
print(f"Yarkovsky-consistent {k}/{N} = {k / N:.3f}; P(>= this | no effect) = {binom_tail(k, N):.2e}")
rows = []
for f, (po, pi, ro, ri) in per.items():
    n = po + pi + ro + ri
    if n >= 25:
        rows.append((f, n, (po + ri) / n, binom_tail(po + ri, n), po, pi, ro, ri))
rows.sort(key=lambda x: -x[1])
print("family  n   consistent  p        pro_out pro_in ret_out ret_in")
for f, n, fr, p, po, pi, ro, ri in rows[:20]:
    print(f"{f:6d} {n:4d}   {fr:.2f}      {p:.1e}  {po:5d} {pi:6d} {ro:7d} {ri:6d}")
json.dump({"total": tot.tolist(), "consistent": [k, N], "p_value": binom_tail(k, N),
           "families": [list(map(float, r)) for r in rows]}, open("yarkovsky_families.json", "w"), indent=0)


# Robustness: (1) centre = median proper a of ALL family members (not only ours); (2) only asteroids
# without a pole in Durech & Hanus 2023 (shows that the new spin senses carry the signal too).
allmem = collections.defaultdict(list)
for n, f in fam.items():
    if n in prop: allmem[f].append(prop[n][1])
med = {f: float(np.median(v)) for f, v in allmem.items()}
dh = set()
for r in csv.DictReader(open("data/durech2023_poles.csv")):
    try: dh.add(int(r["Number"]))
    except ValueError: pass
for label, centre, keep in (("centre = median of members", med, lambda n: True),
                            ("namesake centre, no D&H pole", {f: prop[f][1] for f in prop}, lambda n: n not in dh),
                            ("median centre, no D&H pole", med, lambda n: n not in dh)):
    k = N = 0
    for n in tierA:
        f = fam.get(n)
        if not f or f not in centre or n not in prop or n == f or not keep(n): continue
        out = prop[n][1] > centre[f]; pro = raw[n].get("sense") == 1
        N += 1; k += out == pro
    print(f"{label}: consistent {k}/{N} = {k / N:.3f}, p = {binom_tail(k, N):.1e}")
