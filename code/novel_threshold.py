"""Novel-list threshold: noise bound (null test x number of unknowns) vs size vs agreement with published periods."""
import csv, json, re, numpy as np
import calibrate2 as c
res = c.load_results(); lcdb = c.load_lcdb(); tb, model, thr, _ = c.calibrate(res, lcdb)
null = c.load_results(__import__("os").environ.get("NULL_DIR", "results_null"))
Pn = model(np.array([c.features(r, tb) for r in null])); sn = np.array([c.final_period(r, tb) < 100 for r in null])
unk = [r for r in res if r["num"] not in lcdb]
n_unk = len(unk)
cat = {int(r["number"]): r for r in csv.DictReader(open("catalog.csv"))}
new = [int(r["number"]) for r in csv.DictReader(open("new_candidates.csv"))]
pub = json.load(open("novelty_v3/published_periods.json"))
pubset = set(json.load(open("novelty_v3/published_tierA.json")))
print(f"solved unknowns: {n_unk}")
print("thr   null_pass  noise_bound  novel_n  noise_share_bound  agree_published")
for t in (0.70, 0.75, 0.80, 0.85, 0.90, 0.95):
    pas = float((sn & (Pn >= t)).mean())
    nov = [n for n in new if float(cat[n]["prob_correct"]) >= t and n not in pubset]
    comp = [n for n in new if float(cat[n]["prob_correct"]) >= t and str(n) in pub]
    ag = sum(any(re.match(r"^[\d.]+$", q) and float(q) > 0 and abs(float(cat[n]["period_h"]) - float(q)) / float(q) < .03 for q in pub[str(n)]) for n in comp)
    print(f"{t:.2f}  {pas:.4f}     {pas * n_unk:6.0f}       {len(nov):5d}    {min(1, pas * n_unk / max(len(nov), 1)):.3f}             {ag}/{len(comp)}")
