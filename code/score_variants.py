"""Apply the TUNE-calibrated model (from the main run) to the null and fine-grid runs."""
import numpy as np
import calibrate2 as c

res = c.load_results(); lcdb = c.load_lcdb()
tbic, model, thr, _ = c.calibrate(res, lcdb)
main = {r["num"]: r for r in res}

null = c.load_results("results_null")
P = model(np.array([c.features(r, tbic) for r in null]))
fa = [r for r, p in zip(null, P) if c.confident(r, p, tbic, thr)]
same = [r for r in null if r["num"] in main]
mainP = model(np.array([c.features(main[r["num"]], tbic) for r in same]))
real_conf = sum(c.confident(main[r["num"]], p, tbic, thr) for r, p in zip(same, mainP))
print(f"NULL (residuals permuted within seasons), {len(null)} asteroids: {len(fa)} pass as confident "
      f"= {len(fa) / len(null):.4f}; same asteroids with real data: {real_conf} confident")
if fa:
    print("   false alarms period bands:", np.histogram([c.final_period(r, tbic) for r in fa], [2, 10, 30, 100])[0])

fine = c.load_results("results_fine")
test = [r for r in fine if r["num"] in lcdb and c.is_test(r["num"])]
for name, rows in (("coarse 0.5/T", [main[r["num"]] for r in test if r["num"] in main]), ("coarse 0.1/T", test)):
    Pp = model(np.array([c.features(r, tbic) for r in rows]))
    allm = sum(c.match(c.final_period(r, tbic), lcdb[r["num"]]) for r in rows)
    sel = [r for r, p in zip(rows, Pp) if c.confident(r, p, tbic, thr)]
    m = sum(c.match(c.final_period(r, tbic), lcdb[r["num"]]) for r in sel)
    print(f"TEST {name}: all {allm}/{len(rows)} = {allm / len(rows):.3f}; confident {m}/{len(sel)} = {m / len(sel):.3f}")
changed = sum(abs(r["p_best"] - main[r["num"]]["p_best"]) / main[r["num"]]["p_best"] > 0.01 for r in test if r["num"] in main)
print("best period changed (>1 %) between grids:", changed, "of", len(test))
