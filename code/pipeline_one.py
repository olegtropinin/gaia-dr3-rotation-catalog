"""Geometry + prepare() for single asteroids, same steps as pipeline.py (for re-checks)."""
import os, numpy as np
import geom, nbody, period2
HERE = os.path.dirname(os.path.abspath(__file__))
T = dict(np.load(os.path.join(HERE, "data", "transits.npz")))
els = geom.load_elements(); planets = nbody.Planets()

def prep(num):
    k = int(np.where(T["nums"] == num)[0][0]); s, n = T["start"][k], T["count"][k]
    jd = T["epoch"][s:s + n]
    gt, gr = nbody.integrate(np.array([els[num][1:]]), els[num][0], jd.min() - 6, jd.max() + 6, planets)
    gb = np.column_stack([T["gx"][s:s + n], T["gy"][s:s + n], T["gz"][s:s + n]])
    t = jd.copy()
    for _ in range(3):
        ast = nbody.interp_positions(gt, gr, 0, t).astype(float)
        d = np.linalg.norm(ast - gb, axis=1); t = jd - d * period2.LIGHT_DAY_PER_AU
    rh = ast - planets.pos("10", t).T; r = np.linalg.norm(rh, axis=1)
    alpha = np.degrees(np.arccos(np.clip(np.sum(-rh * (gb - ast), axis=1) / (r * d), -1, 1)))
    return period2.prepare(T["mag"][s:s + n].astype(float), T["rel_err"][s:s + n].astype(float), r, d, alpha, t)
