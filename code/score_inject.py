"""Injection-recovery on 4,000 real Gaia samplings: completeness and precision of tier A, P/2P, spin sense."""
import json, numpy as np
import calibrate2 as c
res = c.load_results(); lcdb = c.load_lcdb(); tb, model, thr, _ = c.calibrate(res, lcdb)
inj = [r for r in c.load_results(__import__("os").environ.get("INJ_DIR", "results_inject_perm")) if "inj_p" in r]
P = model(np.array([c.features(r, tb) for r in inj]))
fp = np.array([c.final_period(r, tb) for r in inj]); tp = np.array([r["inj_p"] for r in inj])
A = np.array([c.confident(r, p, tb, thr) for r, p in zip(inj, P)])
ok = np.abs(fp - tp) / tp < c.TOL
half = np.abs(fp - tp / 2) / (tp / 2) < c.TOL; dbl = np.abs(fp - 2 * tp) / (2 * tp) < c.TOL
amp = np.array([r["inj_amp"] for r in inj]); n = np.array([r["n"] for r in inj])
sense_ok = np.array([r.get("sense") == r["inj_sense"] for r in inj])
out = {"n": len(inj), "all_correct": round(float(ok.mean()), 3), "tierA_n": int(A.sum()),
       "tierA_precision": round(float(ok[A].mean()), 3), "tierA_completeness": round(float((ok & A).mean()), 3),
       "tierA_errors": {"P/2": int((half & A).sum()), "2P": int((dbl & A).sum()), "other": int((A & ~ok & ~half & ~dbl).sum())},
       "sense_correct_among_tierA_correct": round(float(sense_ok[A & ok].mean()), 3)}
def tab(x, edges, name):
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (x >= lo) & (x < hi)
        rows.append({"bin": [lo, hi], "n": int(m.sum()), "completeness": round(float((ok & A)[m].mean()), 3),
                     "precision": round(float(ok[A & m].mean()), 3) if (A & m).any() else None})
    out[name] = rows
tab(amp, [0.1, 0.2, 0.3, 0.45, 0.61], "by_amplitude"); tab(tp, [2, 5, 10, 30, 100.1], "by_period_h"); tab(n, [25, 30, 40, 60, 10000], "by_n_transits")
json.dump(out, open(__import__("os").environ.get("INJ_DIR", "results_inject_perm") + "_report.json", "w"), indent=1)
print(json.dumps(out, indent=1))
