"""Figure: family V-shapes coloured by Gaia spin sense (prograde should sit outside, retrograde inside)."""
import collections, csv, glob, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

F = "data/families"
prop = {}
for line in open(f"{F}/all.syn"):
    if line.startswith("%"): continue
    p = line.split()
    if p[0].isdigit(): prop[int(p[0])] = (float(p[1]), float(p[2]))
fam = {}
for line in open(f"{F}/all_tro.members"):
    if line.startswith("%"): continue
    p = line.split()
    if p[0].isdigit() and p[3] != "0": fam[int(p[0])] = int(p[3])
raw = {}
for f in glob.glob("results/*.jsonl"):
    for l in open(f):
        d = json.loads(l); raw[d["num"]] = d
tierA = {int(r["number"]) for r in csv.DictReader(open("catalog.csv")) if r["tier"] == "A"}
yk = json.load(open("yarkovsky_families.json"))
stats = {int(r[0]): r for r in yk["families"]}
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6, "savefig.dpi": 200})
BLUE, ORANGE, GREY = "#2a6fb0", "#c8641e", "#c9c9c9"
panels = [(221, "Eos"), (24, "Themis"), (15, "Eunomia"), (158, "Koronis")]
fig, axes = plt.subplots(1, 4, figsize=(7.2, 2.6), sharey=False)
members = collections.defaultdict(list)
for n, f in fam.items():
    if n in prop: members[f].append(n)
for ax, (f, name) in zip(axes, panels):
    m = members[f]
    a = np.array([prop[n][1] for n in m]); y = np.array([10 ** (0.2 * prop[n][0]) for n in m])
    ax.scatter(a, y, s=1, color=GREY, lw=0, rasterized=True)
    ours = []
    for sense, col, lab in ((1, BLUE, "prograde"), (-1, ORANGE, "retrograde")):
        s = [n for n in m if n in tierA and n != f and raw[n].get("sense") == sense]
        ys = [10 ** (0.2 * prop[n][0]) for n in s]; ours += ys
        ax.scatter([prop[n][1] for n in s], ys, s=7, color=col, lw=0, label=lab, alpha=0.85)
    ax.axvline(prop[f][1], color="#555555", lw=0.6, ls="--")
    r = stats.get(f)
    ax.set_title(f"({f}) {name}: {r[2] * 100:.0f}% of {int(r[1])}" if r else name, fontsize=8)
    ax.set_xlabel("proper a (au)")
    ax.set_ylim(0, np.percentile(ours, 99) * 1.15)       # zoom on the size range that has spin senses
axes[0].set_ylabel(r"$10^{0.2H}$  ($\propto$ 1/D)")
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, frameon=False, loc="upper center", ncol=2, fontsize=8, markerscale=2)
fig.tight_layout(rect=(0, 0, 1, 0.92))
os.makedirs("figures", exist_ok=True)
fig.savefig("figures/fig4_yarkovsky.pdf"); fig.savefig("figures/fig4_yarkovsky.png")
