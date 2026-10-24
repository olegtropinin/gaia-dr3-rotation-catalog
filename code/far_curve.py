"""Trade-off of the probability threshold: null pass rate vs TEST precision vs number of new candidates."""
import csv, numpy as np
import calibrate2 as c
res = c.load_results(); lcdb = c.load_lcdb()
tbic, model, thr, _ = c.calibrate(res, lcdb)
main = {r["num"]: r for r in res}
null = c.load_results("results_null")
Pn = model(np.array([c.features(r, tbic) for r in null])); short_n = np.array([c.final_period(r, tbic) < 100 for r in null])
test = [r for r in res if r["num"] in lcdb and c.is_test(r["num"])]
Pt = model(np.array([c.features(r, tbic) for r in test])); short_t = np.array([c.final_period(r, tbic) < 100 for r in test])
ok_t = np.array([c.match(c.final_period(r, tbic), lcdb[r["num"]]) for r in test])
newset = {int(r["number"]) for r in csv.DictReader(open("new_candidates.csv"))}
unk = [r for r in res if r["num"] not in lcdb]
Pu = model(np.array([c.features(r, tbic) for r in unk])); short_u = np.array([c.final_period(r, tbic) < 100 for r in unk])
# same 4000 asteroids with real data
same = [main[r["num"]] for r in null]
Ps = model(np.array([c.features(r, tbic) for r in same])); short_s = np.array([c.final_period(r, tbic) < 100 for r in same])
print("thr   null_pass  real_pass(same 4000)  implied_false_share  TEST_prec  TEST_n  unknown_conf")
for th in (thr, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95):
    npass = (short_n & (Pn >= th)).mean()
    rpass = (short_s & (Ps >= th)).sum()
    sel = short_t & (Pt >= th)
    print(f"{th:.3f}  {npass:.4f}     {rpass:5d}                {npass * len(null) / max(rpass, 1):.2f}               "
          f"{ok_t[sel].mean():.3f}     {sel.sum():5d}   {(short_u & (Pu >= th)).sum()}")
