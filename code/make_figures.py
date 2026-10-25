"""Figures for the DR3 catalogue paper: comparison with LCDB, reliability diagram, null-test trade-off."""
import csv, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import calibrate2 as c

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6, "savefig.dpi": 200})
INK, MUTED, BLUE, ORANGE = "#1f1f1f", "#8a8a8a", "#2a6fb0", "#c8641e"
R = list(csv.DictReader(open("catalog.csv")))
test = [r for r in R if r["split"] == "test"]

# 1. our period vs LCDB, TEST half
fig, ax = plt.subplots(figsize=(3.6, 3.4))
x = np.logspace(np.log10(2), np.log10(1000), 50)
for k, ls in ((1, "-"), (0.5, "--"), (2, ":")):
    ax.plot(x, k * x, ls, color=MUTED, lw=0.7, zorder=1)
for tier, col, lab, s in (("B", ORANGE, "tier B", 5), ("A", BLUE, "tier A", 5)):
    rows = [r for r in test if r["tier"] == tier]
    ax.scatter([float(r["lcdb_period_h"]) for r in rows], [float(r["period_h"]) for r in rows], s=s, lw=0, alpha=0.6, color=col, label=f"{lab} (n={len(rows)})", zorder=2)
ax.set(xscale="log", yscale="log", xlim=(2, 1000), ylim=(2, 1000), xlabel="LCDB period (h)", ylabel="Gaia DR3 period, this work (h)")
ax.legend(frameon=False, loc="upper left", fontsize=8)
ax.text(700, 330, "P/2", color=MUTED, fontsize=7); ax.text(300, 700, "2P", color=MUTED, fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig1_lcdb.pdf")); fig.savefig(os.path.join(OUT, "fig1_lcdb.png"))

# 2. reliability diagram on TEST (all solutions)
st = json.load(open("stats_final.json"))
fig, ax = plt.subplots(figsize=(3.4, 3.2))
ax.plot([0, 1], [0, 1], color=MUTED, lw=0.7)
pred = [b["pred"] for b in st["prob_calibration_test"]]; obs = [b["obs"] for b in st["prob_calibration_test"]]; n = [b["n"] for b in st["prob_calibration_test"]]
err = [1.96 * np.sqrt(o * (1 - o) / k) for o, k in zip(obs, n)]
ax.errorbar(pred, obs, yerr=err, fmt="o", ms=4, color=BLUE, lw=0.8, capsize=2)
for p, o, k in zip(pred, obs, n):
    ax.text(p + 0.02, o - 0.06, f"{k}", fontsize=7, color=MUTED)
ax.set(xlim=(0, 1), ylim=(0, 1), xlabel="predicted probability of a correct period", ylabel="observed fraction correct (TEST)")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig2_reliability.pdf")); fig.savefig(os.path.join(OUT, "fig2_reliability.png"))

# 3. threshold trade-off: null pass rate and TEST precision (two panels, one quantity each)
res = c.load_results(); lcdb = c.load_lcdb(); tbic, model, thr, _ = c.calibrate(res, lcdb)
null = c.load_results("results_null_block_all" if os.path.isdir("results_null_block_all") else "results_null_block")
Pn = model(np.array([c.features(r, tbic) for r in null])); sn = np.array([c.final_period(r, tbic) < 100 for r in null])
tr = [r for r in res if r["num"] in lcdb and c.is_test(r["num"])]
Pt = model(np.array([c.features(r, tbic) for r in tr])); stt = np.array([c.final_period(r, tbic) < 100 for r in tr])
okt = np.array([c.match(c.final_period(r, tbic), lcdb[r["num"]]) for r in tr])
th = np.linspace(0.3, 0.95, 66)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.4, 2.6))
a1.plot(th, [100 * (sn & (Pn >= t)).mean() for t in th], color=INK, lw=1.2)
a1.set(xlabel="probability threshold", ylabel="signal-free asteroids passing (%)", title="block null test (32,229 asteroids)")
a2.plot(th, [100 * okt[stt & (Pt >= t)].mean() for t in th], color=BLUE, lw=1.2)
a2.set(xlabel="probability threshold", ylabel="precision on TEST (%)", title="held-out LCDB asteroids")
for a in (a1, a2):
    a.axvline(thr, color=MUTED, lw=0.7, ls="--"); a.axvline(c.CONF_PROB_MIN, color=ORANGE, lw=0.9)
    a.title.set_fontsize(9)
a1.text(c.CONF_PROB_MIN + 0.01, a1.get_ylim()[1] * 0.85, "tier A", color=ORANGE, fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig3_threshold.pdf")); fig.savefig(os.path.join(OUT, "fig3_threshold.png"))
print("figures in", OUT)
