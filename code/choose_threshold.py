"""Tier-A threshold from the null tests, by a rule fixed in advance (independent of TEST).

Rule: the smallest probability t such that the projected number of noise periods,
max(white, block null pass rate at t) x (number of solved asteroids without an LCDB period),
is at most 5 % of the uncatalogued tier-A list at t. Noise matches no catalogue, so it all lands there.
Writes threshold.json; calibrate2.py reads it through the CONF_PROB_MIN environment variable.
"""
import csv, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calibrate2 as c
from compare_lit import load

MAX_NOISE_SHARE = 0.05
res = c.load_results(); lcdb = c.load_lcdb(); tb, model, thr, _ = c.calibrate(res, lcdb)
D = "data"
known = {int(l.split("\t")[0]) for l in open(os.path.join(D, "durech2023.tsv"))}
for path, nc, pc in (("cellino2024.csv", "Name", "Prot"), ("maclennan2026.csv", "Number", "Prot"), ("mcneill2023_tess.csv", "Object", "Prot"),
                     ("vavilov2025_tess.csv", "MPC", "Per"), ("erasmus2020_atlas.csv", "Planet", "Prot")):
    known |= set(load(os.path.join(D, "lit", path), nc, pc))
unk = [r for r in res if r["num"] not in lcdb]
Pu = model(np.array([c.features(r, tb) for r in unk]))
short_u = np.array([c.final_period(r, tb) < c.CONF_MAX_P for r in unk])
uncat = np.array([r["num"] not in known for r in unk])
rates = {}
for name in ("results_null", "results_null_block"):
    nl = c.load_results(name)
    rates[name] = (model(np.array([c.features(r, tb) for r in nl])), np.array([c.final_period(r, tb) < c.CONF_MAX_P for r in nl]))
chosen = None
rows = []
for t in np.round(np.arange(0.5, 0.996, 0.05), 2):        # coarse 0.05 grid: robust, conservative
    pass_max = max(float((s & (p >= t)).mean()) for p, s in rates.values())
    noise = pass_max * len(unk)
    novel = int((short_u & uncat & (Pu >= t)).sum())
    rows.append([float(t), pass_max, noise, novel])
    if chosen is None and novel and noise <= MAX_NOISE_SHARE * novel:
        chosen = float(t)
json.dump({"threshold": chosen, "rule": f"noise <= {MAX_NOISE_SHARE} x uncatalogued tier A", "n_unknown": len(unk),
           "curve": rows}, open("threshold.json", "w"), indent=0)
print("tier-A threshold:", chosen)
