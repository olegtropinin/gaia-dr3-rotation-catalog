"""Stream the Gaia DR3 sso_observation bulk files and aggregate CCD rows into transits.

Output data/transits.npz, sorted by asteroid number, with
  num, epoch (JD), mag, rel_err (max sigma_F/F), gx, gy, gz (Gaia barycentric au)
and an index (nums, start, count) to slice one asteroid.
Only numbered asteroids (number_mp > 0) are kept.
"""
import csv, glob, gzip, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("GAIA_SSO_GLOB", os.path.join(HERE, "data", "gaia_sso", "SsoObservation_*.csv.gz"))
OUT = os.path.join(HERE, "data", "transits.npz")
GAIA_EPOCH0 = 2455197.5

MISSING = ("", "null", "NULL", "NaN")
NEEDED = ("transit_id", "epoch", "g_mag", "g_flux", "x_gaia", "y_gaia", "z_gaia")
acc = {}          # (num, transit_id) -> [n, sum_epoch, sum_mag, max_rel, sum_x, sum_y, sum_z]
t0 = time.time()
rows = 0
for path in sorted(glob.glob(SRC)):
    with gzip.open(path, "rt") as f:
        r = csv.reader(line for line in f if not line.startswith("#"))
        hdr = next(r)
        ix = {k: hdr.index(k) for k in ("number_mp", "transit_id", "epoch", "g_mag", "g_flux", "g_flux_error", "x_gaia", "y_gaia", "z_gaia")}
        for row in r:
            rows += 1
            num = row[ix["number_mp"]]
            if num in MISSING or num == "0" or any(row[ix[k]] in MISSING for k in NEEDED):
                continue
            flux = float(row[ix["g_flux"]])
            if flux <= 0:
                continue
            key = (int(num), int(row[ix["transit_id"]]))
            a = acc.get(key)
            fe = row[ix["g_flux_error"]]
            rel = (float(fe) if fe not in MISSING else 0.0) / flux
            vals = (float(row[ix["epoch"]]), float(row[ix["g_mag"]]), float(row[ix["x_gaia"]]), float(row[ix["y_gaia"]]), float(row[ix["z_gaia"]]))
            if a is None:
                acc[key] = [1, vals[0], vals[1], rel, vals[2], vals[3], vals[4]]
            else:
                a[0] += 1; a[1] += vals[0]; a[2] += vals[1]; a[3] = max(a[3], rel); a[4] += vals[2]; a[5] += vals[3]; a[6] += vals[4]
    print(f"{os.path.basename(path)}: {rows} rows, {len(acc)} transits, {time.time() - t0:.0f}s", flush=True)

keys = sorted(acc)
n = len(keys)
num = np.empty(n, np.int32); ep = np.empty(n); mag = np.empty(n, np.float32); rel = np.empty(n, np.float32)
g = np.empty((n, 3))
for k, key in enumerate(keys):
    a = acc[key]; c = a[0]
    num[k] = key[0]; ep[k] = a[1] / c + GAIA_EPOCH0; mag[k] = a[2] / c; rel[k] = a[3]; g[k] = (a[4] / c, a[5] / c, a[6] / c)
# keep time order inside each asteroid
order = np.lexsort((ep, num))
num, ep, mag, rel, g = num[order], ep[order], mag[order], rel[order], g[order]
nums, start, count = np.unique(num, return_index=True, return_counts=True)
np.savez(OUT, num=num, epoch=ep, mag=mag, rel_err=rel, gx=g[:, 0], gy=g[:, 1], gz=g[:, 2], nums=nums, start=start, count=count)
print(f"saved {OUT}: {n} transits, {len(nums)} asteroids, median {int(np.median(count))} transits/asteroid, "
      f">=25 transits: {(count >= 25).sum()}, >=40: {(count >= 40).sum()}, {time.time() - t0:.0f}s")
