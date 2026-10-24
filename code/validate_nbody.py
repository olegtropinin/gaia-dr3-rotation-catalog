"""Same comparison as validate_geom.py, but with numerically integrated orbits (nbody.py)."""
import csv, glob, io, json, os, time, urllib.parse, urllib.request
import numpy as np
import geom, nbody

OLD = os.path.expanduser("~/sciagent/data/obs")
TAP = "https://gea.esac.esa.int/tap-server/tap/sync"
def gaia(q):
    body = urllib.parse.urlencode({"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": q}).encode()
    return list(csv.DictReader(io.StringIO(urllib.request.urlopen(urllib.request.Request(TAP, data=body), timeout=300).read().decode())))

els = geom.load_elements()
pl = nbody.Planets()
files = [f for f in sorted(glob.glob(f"{OLD}/*.json"))[:400:20]]
recs = [json.load(open(f)) for f in files]
recs = [r for r in recs if r["geo"] and r["num"] in els]
nums = [r["num"] for r in recs]
E = np.array([els[n][1:] for n in nums]); epoch = els[nums[0]][0]
assert all(els[n][0] == epoch for n in nums)
t0 = time.time()
gt, gr = nbody.integrate(E, epoch, 2456700.0, None, pl)
print(f"integrated {len(nums)} asteroids over {len(gt)} days in {time.time()-t0:.1f}s")
out = []
for k, rec in enumerate(recs):
    rows = gaia(f"SELECT transit_id, epoch, x_gaia, y_gaia, z_gaia FROM gaiadr3.sso_observation WHERE number_mp={rec['num']}")
    tr = {}
    for r in rows:
        tr.setdefault(r["transit_id"], []).append([float(r["epoch"]), float(r["x_gaia"]), float(r["y_gaia"]), float(r["z_gaia"])])
    arr = np.array(sorted([np.mean(v, axis=0) for v in tr.values()], key=lambda x: x[0]))
    jd = arr[:, 0] + 2455197.5
    idx = [int(np.argmin(np.abs(jd - t))) for t in np.array(rec["obs"])[:, 0]]
    jd, gaia_b = jd[idx], arr[idx, 1:4]
    t = jd.copy()
    for _ in range(3):
        ast = nbody.interp_positions(gt, gr, k, t)
        d = np.linalg.norm(ast - gaia_b, axis=1)
        t = jd - d * 0.0057755183
    sun = pl.pos("10", t).T
    rh = ast - sun; r = np.linalg.norm(rh, axis=1)
    cosa = np.sum(-rh * (gaia_b - ast), axis=1) / (r * d)
    al = np.degrees(np.arccos(np.clip(cosa, -1, 1)))
    g = np.array(rec["geo"])
    dm = np.abs(5*np.log10(r*d) - 5*np.log10(g[:,0]*g[:,1])).max()
    out.append((rec["num"], np.abs(r-g[:,0]).max(), np.abs(d-g[:,1]).max(), np.abs(al-g[:,2]).max(), dm))
    print(f"{rec['num']:>7} dr={out[-1][1]:.6f} dDelta={out[-1][2]:.6f} dalpha={out[-1][3]:.4f} dmag={dm:.5f}")
w = np.array([x[1:] for x in out])
print("WORST:", w.max(axis=0))
