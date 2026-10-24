"""Compare two-body geometry (geom.py) with JPL Horizons on asteroids from the first run."""
import csv, glob, io, json, os, sys, urllib.parse, urllib.request
import numpy as np
import geom

OLD = os.path.expanduser("~/sciagent/data/obs")
TAP = "https://gea.esac.esa.int/tap-server/tap/sync"


def gaia(q):
    body = urllib.parse.urlencode({"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": q}).encode()
    return list(csv.DictReader(io.StringIO(urllib.request.urlopen(urllib.request.Request(TAP, data=body), timeout=300).read().decode())))


els = geom.load_elements()
print("elements loaded:", len(els))
sun = geom.SunTable()
files = sorted(glob.glob(f"{OLD}/*.json"))[:400:20]
worst = []
for f in files:
    rec = json.load(open(f))
    num = rec["num"]
    if not rec["geo"] or num not in els:
        continue
    rows = gaia(f"SELECT transit_id, epoch, x_gaia, y_gaia, z_gaia FROM gaiadr3.sso_observation WHERE number_mp={num}")
    tr = {}
    for r in rows:
        tr.setdefault(r["transit_id"], []).append([float(r["epoch"]), float(r["x_gaia"]), float(r["y_gaia"]), float(r["z_gaia"])])
    arr = np.array(sorted([np.mean(v, axis=0) for v in tr.values() if v], key=lambda x: x[0]))
    jd = arr[:, 0] + 2455197.5
    # match to the first run's transits by time (same averaging)
    old = np.array(rec["obs"])[:, 0]
    idx = [int(np.argmin(np.abs(jd - t))) for t in old]
    r, d, a, _ = geom.geometry(els[num], jd[idx], arr[idx, 1:4], sun)
    g = np.array(rec["geo"])
    dr, dd, da = np.abs(r - g[:, 0]).max(), np.abs(d - g[:, 1]).max(), np.abs(a - g[:, 2]).max()
    dmag = np.abs(5 * np.log10(r * d) - 5 * np.log10(g[:, 0] * g[:, 1])).max()
    worst.append((num, dr, dd, da, dmag))
    print(f"{num:>7}  max|dr|={dr:.5f} au  max|dDelta|={dd:.5f} au  max|dalpha|={da:.3f} deg  max|dmag|={dmag:.4f}")
w = np.array([x[1:] for x in worst])
print("WORST over", len(w), "asteroids: dr", w[:, 0].max(), "dDelta", w[:, 1].max(), "dalpha", w[:, 2].max(), "dmag", w[:, 3].max())
