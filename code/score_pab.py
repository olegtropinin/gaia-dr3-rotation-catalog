"""v2 vs v3 (PAB) on the LCDB-known asteroids: same TUNE-only procedure, report TEST."""
import collections, numpy as np
import calibrate2 as c
lcdb = c.load_lcdb()
for name, sub in (("v2", "results"), ("v3 PAB", "results_pab")):
    res = [r for r in c.load_results(sub) if r["num"] in lcdb]
    tbic, model, thr, _ = c.calibrate(res, lcdb)
    test = [r for r in res if c.is_test(r["num"])]
    P = model(np.array([c.features(r, tbic) for r in test]))
    ok = np.array([c.match(c.final_period(r, tbic), lcdb[r["num"]]) for r in test])
    A = np.array([c.confident(r, p, tbic, thr) for r, p in zip(test, P)])
    B = np.array([(p >= thr) and c.final_period(r, tbic) < 100 for r, p in zip(test, P)])
    print(f"{name}: doubling {tbic:.2f}, thr {thr:.3f} | TEST all {ok.mean():.3f} | tier A {ok[A].sum()}/{A.sum()} = {ok[A].mean():.3f} | "
          f"prob>=thr,<100h {ok[B].sum()}/{B.sum()} = {ok[B].mean():.3f}")
    if "sense" in res[0]:
        print("   sense counts:", collections.Counter(r["sense"] for r in res))
