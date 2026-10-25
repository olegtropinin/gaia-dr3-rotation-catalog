"""Checks requested by the referees: confusion matrix, matched control, U>=3- calibration, pilot vs v2."""
import csv, json, os, sys, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compare_lit import load

R = {int(r["number"]): r for r in csv.DictReader(open("catalog.csv"))}
lines = open("data/lc_summary.csv", encoding="latin-1").read().splitlines()
h = next(i for i, l in enumerate(lines) if l.lower().startswith("number,"))
U = {}
for r in csv.DictReader(lines[h + 1:], fieldnames=lines[h].split(",")):
    try:
        U[int(r["Number"])] = ((r["U"] or "").strip(), float(r["Period"]), (r["IsBinary"] or "").strip())
    except (TypeError, ValueError):
        pass


def rel(p, q):
    for name, k in (("match", 1), ("half", 0.5), ("double", 2)):
        if abs(p - k * q) / (k * q) < 0.03:
            return name
    return "other"


test_conf = [r for r in R.values() if r["split"] == "test" and r["confident"] == "1"]
print("1) TEST confident confusion:", dict(collections.Counter(rel(float(r["period_h"]), float(r["lcdb_period_h"])) for r in test_conf)))
lo = [r for r in test_conf if float(r["period_h"]) < 100]
print("   confident without the 100-1000 h band:", sum(rel(float(r["period_h"]), float(r["lcdb_period_h"])) == "match" for r in lo), "/", len(lo))

d = "data"
same = [{int(l.split("\t")[0]) for l in open(os.path.join(d, "durech2023.tsv"))},
        set(load(os.path.join(d, "lit", "cellino2024.csv"), "Name", "Prot")),
        set(load(os.path.join(d, "lit", "maclennan2026.csv"), "Number", "Prot"))]
in_same = set().union(*same)
ctrl = [r for r in test_conf + [r for r in R.values() if r["split"] == "tune" and r["confident"] == "1"] if int(r["number"]) not in in_same]
ok = sum(rel(float(r["period_h"]), float(r["lcdb_period_h"])) == "match" for r in ctrl)
print(f"2) matched control (LCDB-known, confident, absent from D&H/Cellino/MacLennan; TUNE+TEST): {ok}/{len(ctrl)} = {ok / max(len(ctrl), 1):.2f}")
ctrl_t = [r for r in ctrl if r["split"] == "test"]
okt = sum(rel(float(r["period_h"]), float(r["lcdb_period_h"])) == "match" for r in ctrl_t)
print(f"   TEST only: {okt}/{len(ctrl_t)}; by band:", {b: (sum(rel(float(r['period_h']), float(r['lcdb_period_h'])) == 'match' for r in ctrl if lo_ <= float(r['period_h']) < hi_), sum(1 for r in ctrl if lo_ <= float(r['period_h']) < hi_)) for b, (lo_, hi_) in {'2-10': (2, 10), '10-30': (10, 30), '30-100': (30, 100), '100+': (100, 1e9)}.items()})
print("   n_transits median: control", np.median([int(r["n_transits"]) for r in ctrl]), "new", np.median([int(r["n_transits"]) for r in csv.DictReader(open("new_candidates.csv"))]), "TEST conf", np.median([int(r["n_transits"]) for r in test_conf]))

for name, keep in (("U>=3-", lambda u: u in ("3", "3-")), ("U=2/2+/2-", lambda u: u in ("2", "2+", "2-"))):
    sub = [r for r in test_conf if keep(U.get(int(r["number"]), ("",))[0])]
    m = sum(rel(float(r["period_h"]), float(r["lcdb_period_h"])) == "match" for r in sub)
    print(f"3) TEST confident with LCDB {name}: {m}/{len(sub)} = {m / max(len(sub), 1):.2f}")
binaries = [r for r in test_conf if U.get(int(r["number"]), ("", 0, ""))[2] not in ("", "-")]
print("   confident TEST that are LCDB binaries:", len(binaries))
dp = np.array([abs(float(r["period_h"]) - float(r["lcdb_period_h"])) / float(r["lcdb_period_h"]) for r in test_conf])
print("   |dP/P| of confident TEST matches: median", f"{np.median(dp[dp < .03]):.5f}", "90%", f"{np.percentile(dp[dp < .03], 90):.5f}")

pilot = json.load(open("../sci/candidates68.json")) if os.path.exists("../sci/candidates68.json") else []
cands42 = list(csv.DictReader(open(os.environ.get("PILOT_CANDIDATES", "data/pilot42_candidates.csv"))))
print("4) pilot candidates.csv columns:", list(cands42[0].keys())[:10])
