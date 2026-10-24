"""All numbers quoted in the README and the paper draft, computed from the current catalog.csv (tier A)."""
import csv, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compare_lit import load
import calibrate2 as c

R = list(csv.DictReader(open("catalog.csv")))
rep = json.load(open("report.json")); lit = json.load(open("lit_report.json"))
ok = lambda r: abs(float(r["period_h"]) - float(r["lcdb_period_h"])) / float(r["lcdb_period_h"]) < c.TOL
def rel(p, q):
    for n, k in (("match", 1), ("half", .5), ("double", 2)):
        if abs(p - k * q) / (k * q) < c.TOL: return n
    return "other"
test = [r for r in R if r["split"] == "test"]
A_test = [r for r in test if r["tier"] == "A"]
B_test = [r for r in test if r["tier"] == "B"]
conf_mat = {}
for r in A_test:
    k = rel(float(r["period_h"]), float(r["lcdb_period_h"])); conf_mat[k] = conf_mat.get(k, 0) + 1
bands = {}
for lo, hi in ((2, 10), (10, 30), (30, 100)):
    s = [r for r in A_test if lo <= float(r["period_h"]) < hi]
    bands[f"{lo}-{hi}h"] = [sum(map(ok, s)), len(s)]
# calibration of prob on TEST
calib = []
for lo, hi in ((0, .3), (.3, .5), (.5, .7), (.7, .85), (.85, 1.01)):
    s = [r for r in test if lo <= float(r["prob_correct"]) < hi]
    calib.append({"bin": [lo, hi], "n": len(s), "pred": round(float(np.mean([float(r["prob_correct"]) for r in s])), 3), "obs": round(sum(map(ok, s)) / len(s), 3)})
# period precision of matches
dp = np.array([abs(float(r["period_h"]) - float(r["lcdb_period_h"])) / float(r["lcdb_period_h"]) for r in A_test if ok(r)])
# independent three-way, TEST only
D = "data"
three = {}
for name, path, nc, pc in (("McNeill 2023 TESS", "mcneill2023_tess.csv", "Object", "Prot"), ("Vavilov & Carry 2025 TESS", "vavilov2025_tess.csv", "MPC", "Per"), ("Erasmus 2020 ATLAS", "erasmus2020_atlas.csv", "Planet", "Prot")):
    ref = load(os.path.join(D, "lit", path), nc, pc)
    s = [r for r in A_test if int(r["number"]) in ref]
    three[name] = {"n": len(s), "ours_vs_lcdb": sum(map(ok, s)), "theirs_vs_lcdb": sum(abs(ref[int(r["number"])] - float(r["lcdb_period_h"])) / float(r["lcdb_period_h"]) < c.TOL for r in s)}
novel = list(csv.DictReader(open("new_candidates_A_novel.csv")))
new6 = list(csv.DictReader(open("new_candidates.csv")))
_six = set()
for path, nc, pc in (("cellino2024.csv", "Name", "Prot"), ("maclennan2026.csv", "Number", "Prot"), ("mcneill2023_tess.csv", "Object", "Prot"),
                     ("vavilov2025_tess.csv", "MPC", "Per"), ("erasmus2020_atlas.csv", "Planet", "Prot")):
    _six |= set(load(os.path.join(D, "lit", path), nc, pc))
_six |= {int(l.split("\t")[0]) for l in open(os.path.join(D, "durech2023.tsv"))}
ctrl = [r for r in A_test if int(r["number"]) not in _six]


def null_stats():
    res = c.load_results(); lc = c.load_lcdb(); tb, model, thr, _ = c.calibrate(res, lc)
    out = {"tune_thr": round(thr, 3), "tierA_thr": c.CONF_PROB_MIN, "n_solved_unknown": sum(r["num"] not in lc for r in res)}
    for name, sub in (("white", "results_null"), ("block", "results_null_block")):
        null = c.load_results(sub)
        P = model(np.array([c.features(r, tb) for r in null]))
        sh = np.array([c.final_period(r, tb) < c.CONF_MAX_P for r in null])
        out[name] = {"n": len(null), "pass_at_tune_thr": round(float((sh & (P >= thr)).mean()), 4),
                     "pass_at_0.70": round(float((sh & (P >= 0.70)).mean()), 4), "pass_at_tierA": round(float((sh & (P >= c.CONF_PROB_MIN)).mean()), 4)}
    return out


def pilot_check():
    cat = {int(r["number"]): r for r in R}
    out = {"match": 0, "x2": 0, "x0.5": 0, "differs": 0, "absent": 0, "differs_list": []}
    for p in csv.DictReader(open("/Users/oleg/work/gaia-asteroid-periods/data/candidates.csv")):
        n, pp = int(p["number"]), float(p["period_h"])
        if n not in cat:
            out["absent"] += 1; continue
        q = float(cat[n]["period_h"])
        k = rel(q, pp)
        k = {"match": "match", "double": "x2", "half": "x0.5"}.get(k, "differs")
        out[k] += 1
        if k != "match":
            out["differs_list"].append([n, p["reliability"], pp, q, cat[n]["tier"]])
    return out
out = {
    "targets": 42195, "solved": len(R), "known_lcdb": sum(r["split"] != "unknown" for r in R), "n_test": len(test),
    "tierA_total": sum(r["tier"] == "A" for r in R), "tierB_total": sum(r["tier"] == "B" for r in R),
    "slow_candidates": sum(r["slow_candidate"] == "1" for r in R),
    "tierA_unknown": sum(r["tier"] == "A" and r["split"] == "unknown" for r in R),
    "test_tierA": [sum(map(ok, A_test)), len(A_test)], "test_tierB": [sum(map(ok, B_test)), len(B_test)],
    "test_all": [sum(map(ok, test)), len(test)], "test_tierA_confusion": conf_mat, "test_tierA_bands": bands,
    "test_recall_tierA": round(sum(map(ok, A_test)) / sum(map(ok, test)), 3),
    "prob_calibration_test": calib, "dP_over_P_matches_median": float(np.median(dp)), "dP_over_P_matches_p90": float(np.percentile(dp, 90)),
    "thresholds": {"double_harm": rep["double_harm_threshold"], "prob_tune80": rep["prob_threshold"], "prob_null": c.CONF_PROB_MIN, "max_period_h": c.CONF_MAX_P},
    "same_data_agreement": {k: [v["agree"], v["n"]] for k, v in lit.items() if isinstance(v, dict) and "Gaia" in k},
    "independent_agreement": {k: [v["agree"], v["n"]] for k, v in lit.items() if isinstance(v, dict) and "Gaia" not in k},
    "three_way_test_tierA": three,
    "new_tierA_vs_6_catalogues": len(new6), "new_tierA_published_elsewhere": len(new6) - len(novel), "new_tierA_novel": len(novel),
    "novel_bands": {b: sum(1 for r in novel if lo <= float(r["period_h"]) < hi) for b, (lo, hi) in {"2-10h": (2, 10), "10-30h": (10, 30), "30-100h": (30, 100)}.items()},
    "matched_control_tierA": [sum(map(ok, ctrl)), len(ctrl)], "null_test": null_stats(),
    "pilot42_vs_v3": pilot_check(),
}
json.dump(out, open("stats_final.json", "w"), indent=1)
print(json.dumps(out, indent=1))


def extras():
    """Referee round-2 checks: LCDB quality, anatomy of the tier-A errors, spin sense vs published poles."""
    import collections, glob
    lines = open(os.path.join(D, "lc_summary.csv"), encoding="latin-1").read().splitlines()
    h = next(i for i, l in enumerate(lines) if l.lower().startswith("number,"))
    U = {}
    for r in csv.DictReader(lines[h + 1:], fieldnames=lines[h].split(",")):
        try: U[int(r["Number"])] = (r["U"] or "").strip()
        except (TypeError, ValueError): pass
    q = {}
    for name, keep in (("U>=3-", ("3", "3-")), ("U=2/2+", ("2", "2+")), ("U=2-", ("2-",))):
        s = [r for r in A_test if U.get(int(r["number"])) in keep]
        q[name] = [sum(map(ok, s)), len(s)]
    va = load(os.path.join(D, "lit", "vavilov2025_tess.csv"), "MPC", "Per")
    anat = collections.defaultdict(lambda: {"n": 0, "tess_with_us": 0, "tess_with_lcdb": 0, "tess_n": 0})
    for r in A_test:
        n, p, l = int(r["number"]), float(r["period_h"]), float(r["lcdb_period_h"])
        k = "match" if ok(r) else "x2" if rel(p, l) != "other" else "1 c/d alias of LCDB" if abs(abs(48 / p - 48 / l) - 1) < 0.06 else "other"
        a = anat[k]; a["n"] += 1
        if n in va:
            a["tess_n"] += 1; a["tess_with_us"] += abs(p - va[n]) / va[n] < c.TOL; a["tess_with_lcdb"] += abs(l - va[n]) / va[n] < c.TOL
    raw = {}
    for f in glob.glob("results/*.jsonl"):
        for l in open(f):
            d = json.loads(l); raw[d["num"]] = d
    tierA = {int(r["number"]) for r in R if r["tier"] == "A"}
    def sense_agree(poles):
        t = a = 0
        for n, bs in poles.items():
            if n not in tierA or "sense" not in raw.get(n, {}) or len({b > 0 for b in bs}) > 1 or min(abs(b) for b in bs) < 20:
                continue
            t += 1; a += (bs[0] > 0) == (raw[n]["sense"] == 1)
        return [a, t]
    dhp = collections.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(D, "durech2023_poles.csv"))):
        try:
            dhp[int(r["Number"])] += [float(r["beta1"])] + ([float(r["beta2"])] if r["beta2"].strip() else [])
        except ValueError: pass
    ids = {r["id"]: int(r["number"]) for r in csv.DictReader(open(os.path.join(D, "damit_asteroids.csv"), encoding="utf-8-sig")) if r["number"].isdigit()}
    dmp = collections.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(D, "damit_models.csv"), encoding="utf-8-sig")):
        try:
            if r["asteroid_id"] in ids: dmp[ids[r["asteroid_id"]]].append(float(r["beta"]))
        except ValueError: pass
    return {"test_tierA_by_lcdb_quality": q, "test_tierA_anatomy": dict(anat),
            "spin_sense_vs_durech2023": sense_agree(dhp), "spin_sense_vs_damit": sense_agree(dmp),
            "spin_sense_vs_damit_not_in_durech": sense_agree({n: b for n, b in dmp.items() if n not in dhp}),
            "tierA_unknown_with_sense": sum(1 for r in R if r["tier"] == "A" and r["split"] == "unknown")}


out.update(extras())
json.dump(out, open("stats_final.json", "w"), indent=1)
