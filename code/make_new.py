"""New candidates (confident, no LCDB, absent from 6 catalogues) and the matched-control precision for them."""
import csv, collections, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compare_lit import load

D = "data"
same = [{int(l.split("\t")[0]) for l in open(os.path.join(D, "durech2023.tsv"))},
        set(load(os.path.join(D, "lit", "cellino2024.csv"), "Name", "Prot")),
        set(load(os.path.join(D, "lit", "maclennan2026.csv"), "Number", "Prot"))]
indep = [set(load(os.path.join(D, "lit", "mcneill2023_tess.csv"), "Object", "Prot")),
         set(load(os.path.join(D, "lit", "vavilov2025_tess.csv"), "MPC", "Per")),
         set(load(os.path.join(D, "lit", "erasmus2020_atlas.csv"), "Planet", "Prot"))]
in_any = set().union(*same, *indep)
R = list(csv.DictReader(open("catalog.csv")))
conf = [r for r in R if r["confident"] == "1"]
new = [r for r in conf if not r["lcdb_period_h"] and int(r["number"]) not in in_any]
ok = lambda r: abs(float(r["period_h"]) - float(r["lcdb_period_h"])) / float(r["lcdb_period_h"]) < 0.03
band = lambda p: "2-10" if p < 10 else "10-30" if p < 30 else "30-100"
# matched control: LCDB-known, confident, TEST half, absent from all six catalogues
ctrl = [r for r in conf if r["split"] == "test" and int(r["number"]) not in in_any]
print("confident", len(conf), "| new", len(new), dict(collections.Counter(band(float(r["period_h"])) for r in new)))
print(f"matched control (TEST, absent from all six): {sum(map(ok, ctrl))}/{len(ctrl)} = {sum(map(ok, ctrl)) / len(ctrl):.3f}")
# re-weight control precision by band and transit bin to the new population
def cell(r):
    n = int(r["n_transits"]); return (band(float(r["period_h"])), "25-30" if n < 30 else "30-40" if n < 40 else "40+")
cc = collections.defaultdict(lambda: [0, 0])
for r in ctrl:
    c = cc[cell(r)]; c[0] += ok(r); c[1] += 1
allc = collections.defaultdict(lambda: [0, 0])
for r in [r for r in conf if r["split"] == "test"]:
    c = allc[cell(r)]; c[0] += ok(r); c[1] += 1
nc = collections.Counter(cell(r) for r in new)
exp = sum(n * (cc[k][0] / cc[k][1] if cc[k][1] >= 15 else allc[k][0] / allc[k][1]) for k, n in nc.items())
print(f"expected correct among new, control precision re-weighted by (band, transits): {exp:.0f} = {exp / len(new):.3f}")
for k in sorted(nc):
    print(f"   {k}: new {nc[k]:4d} | control {cc[k][0]}/{cc[k][1]} | all TEST {allc[k][0]}/{allc[k][1]}")
lo, hi = np.percentile(np.random.default_rng(0).binomial(len(ctrl), sum(map(ok, ctrl)) / len(ctrl), 20000) / len(ctrl), [2.5, 97.5])
print(f"control 95% interval {lo:.3f}-{hi:.3f}")
with open("new_candidates.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=R[0].keys()); w.writeheader(); w.writerows(new)
