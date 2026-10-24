"""Observation geometry for Gaia asteroid photometry without per-object Horizons queries.

Asteroid: two-body propagation of JPL osculating elements (heliocentric ecliptic J2000).
Gaia:     barycentric position from gaiadr3.sso_observation (x_gaia, y_gaia, z_gaia; ICRS, au).
Sun:      barycentric position from a single Horizons vector table, interpolated.
Returns heliocentric distance r, Gaia distance delta (au) and phase angle alpha (deg).
"""
import gzip, json, math, os, urllib.parse, urllib.request
import numpy as np

GM_SUN = 2.959122082855911e-4          # au^3 / day^2 (Gaussian constant squared)
OBLIQ = math.radians(84381.448 / 3600)  # J2000 obliquity
EC2EQ = np.array([[1, 0, 0], [0, math.cos(OBLIQ), -math.sin(OBLIQ)], [0, math.sin(OBLIQ), math.cos(OBLIQ)]])
HERE = os.path.dirname(os.path.abspath(__file__))


def load_elements(path=os.path.join(HERE, "data", "ELEMENTS.NUMBR.gz")):
    """number -> (epoch_jd, a, e, i, w, node, M) with angles in radians."""
    out = {}
    with gzip.open(path, "rt") as f:
        for line in f:
            # Fixed layout: number in columns 0-5, name in 7-23 (may contain spaces), then
            # Epoch(MJD) a e i w Node M H G Ref separated by spaces.
            if not line[:6].strip().isdigit():
                continue
            try:
                num = int(line[:6])
                epoch, a, e, i, w, node, M = (float(x) for x in line[25:].split()[:7])
            except ValueError:
                continue
            out[num] = (epoch + 2400000.5, a, e, math.radians(i), math.radians(w), math.radians(node), math.radians(M))
    return out


def kepler_positions(el, jd):
    """Heliocentric equatorial position (au) of one asteroid at an array of JD."""
    epoch, a, e, i, w, node, M0 = el
    n = math.sqrt(GM_SUN / a ** 3)
    M = M0 + n * (np.asarray(jd) - epoch)
    E = M.copy()
    for _ in range(30):                     # Newton iteration, converges for e < 0.99
        dE = (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
        E -= dE
        if np.max(np.abs(dE)) < 1e-12:
            break
    xp, yp = a * (np.cos(E) - e), a * math.sqrt(1 - e * e) * np.sin(E)
    cw, sw, cn, sn, ci, si = math.cos(w), math.sin(w), math.cos(node), math.sin(node), math.cos(i), math.sin(i)
    # perifocal -> ecliptic
    R = np.array([[cn * cw - sn * sw * ci, -cn * sw - sn * cw * ci],
                  [sn * cw + cn * sw * ci, -sn * sw + cn * cw * ci],
                  [sw * si, cw * si]])
    ecl = R @ np.vstack([xp, yp])
    return (EC2EQ @ ecl).T


class SunTable:
    """Barycentric Sun position (ICRS, au) from Horizons, cached on disk, linear interpolation."""
    def __init__(self, start="2014-07-01", stop="2018-01-01", step="1d", cache=os.path.join(HERE, "data", "sun_bary.json")):
        if not os.path.exists(cache):
            q = {"format": "json", "COMMAND": "10", "EPHEM_TYPE": "VECTORS", "CENTER": "500@0", "REF_PLANE": "FRAME",
                 "START_TIME": start, "STOP_TIME": stop, "STEP_SIZE": step, "VEC_TABLE": "1", "CSV_FORMAT": "YES", "OUT_UNITS": "AU-D"}
            res = json.load(urllib.request.urlopen("https://ssd.jpl.nasa.gov/api/horizons.api?" + urllib.parse.urlencode(q), timeout=300))["result"]
            rows = []
            for line in res.split("$$SOE")[1].split("$$EOE")[0].strip().splitlines():
                c = [x.strip() for x in line.split(",")]
                rows.append([float(c[0]), float(c[2]), float(c[3]), float(c[4])])
            json.dump(rows, open(cache, "w"))
        t = np.array(json.load(open(cache)))
        self.jd, self.xyz = t[:, 0], t[:, 1:]

    def __call__(self, jd):
        jd = np.asarray(jd)
        return np.column_stack([np.interp(jd, self.jd, self.xyz[:, k]) for k in range(3)])


def geometry(el, jd_obs, gaia_bary, sun):
    """r, delta, alpha (deg) and light-time-corrected time for each observation.
    jd_obs: TCB-ish JD at Gaia; gaia_bary: (N,3) au ICRS."""
    jd_obs = np.asarray(jd_obs)
    sun_b = sun(jd_obs)
    t = jd_obs.copy()
    for _ in range(3):                      # iterate light time
        ast_b = kepler_positions(el, t) + sun(t)
        delta = np.linalg.norm(ast_b - gaia_bary, axis=1)
        t = jd_obs - delta * 0.0057755183
    ast_h = ast_b - sun(t)
    r = np.linalg.norm(ast_h, axis=1)
    to_sun, to_obs = -ast_h, gaia_bary - ast_b
    cosa = np.sum(to_sun * to_obs, axis=1) / (r * delta)
    return r, delta, np.degrees(np.arccos(np.clip(cosa, -1, 1))), t
