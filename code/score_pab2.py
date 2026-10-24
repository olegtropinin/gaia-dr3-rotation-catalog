import collections, numpy as np
import calibrate2 as c
lcdb = c.load_lcdb()
for name, sub in (("v3 (scale 1)", "results_pab"), ("v3 + scale 2", "results_pab2")):
    res = [r for r in c.load_results(sub) if r["num"] in lcdb]
    tbic, model, thr, _ = c.calibrate(res, lcdb)
    test = [r for r in res if c.is_test(r["num"])]
    P = model(np.array([c.features(r, tbic) for r in test]))
    ok = np.array([c.match(c.final_period(r, tbic), lcdb[r["num"]]) for r in test])
    for th in (0.70, 0.80):
        A = np.array([p >= max(thr, th) and c.final_period(r, tbic) < 100 for r, p in zip(test, P)])
        print(f"{name}: all {ok.mean():.3f} | prob>={th}: {ok[A].sum()}/{A.sum()} = {ok[A].mean():.3f}")
    if "pab_scale" in res[0]:
        print("   scale chosen:", collections.Counter(r["pab_scale"] for r in res),
              "| doubled & scale 2:", sum(1 for r in res if r["pab_scale"] == 2 and r["harm_ratio"] > tbic))
