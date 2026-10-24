"""Vectorised orbit integration for many asteroids at once.

Asteroids are test particles in the barycentric ICRS frame, attracted by the Sun, Jupiter,
Saturn, Uranus and Neptune whose positions come from Horizons tables (cached, interpolated).
Initial conditions: JPL osculating heliocentric elements at their epoch (MJD 61200 for the
current ELEMENTS.NUMBR). Integration: fixed-step 8th-order... no -- classic RK4 with a 1-day
step, which keeps main-belt position errors far below 1e-4 au over a decade.
The trajectory is stored on a daily grid and interpolated (cubic) at observation times.
"""
import json, math, os, urllib.parse, urllib.request
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
GM_SUN = 2.959122082855911e-4
# GM in units of GM_sun (IAU / DE440 ratios)
BODIES = {"10": 1.0, "5": 1 / 1047.348644, "6": 1 / 3497.901768, "7": 1 / 22902.98, "8": 1 / 19412.26}
OBLIQ = math.radians(84381.448 / 3600)
EC2EQ = np.array([[1, 0, 0], [0, math.cos(OBLIQ), -math.sin(OBLIQ)], [0, math.sin(OBLIQ), math.cos(OBLIQ)]])


def horizons_vectors(body, start, stop, step="1d"):
    cache = os.path.join(HERE, "data", f"vec_{body}_{start}_{stop}_{step}.npy")
    if os.path.exists(cache):
        return np.load(cache)
    q = {"format": "json", "COMMAND": body, "EPHEM_TYPE": "VECTORS", "CENTER": "500@0", "REF_PLANE": "FRAME",
         "START_TIME": start, "STOP_TIME": stop, "STEP_SIZE": step, "VEC_TABLE": "2", "CSV_FORMAT": "YES", "OUT_UNITS": "AU-D"}
    res = json.load(urllib.request.urlopen("https://ssd.jpl.nasa.gov/api/horizons.api?" + urllib.parse.urlencode(q), timeout=600))["result"]
    rows = []
    for line in res.split("$$SOE")[1].split("$$EOE")[0].strip().splitlines():
        c = [x.strip() for x in line.split(",")]
        rows.append([float(c[0])] + [float(x) for x in c[2:8]])
    a = np.array(rows)
    np.save(cache, a)
    return a


class Planets:
    def __init__(self, start="2013-01-01", stop="2027-01-01"):
        self.tab = {b: horizons_vectors(b, start, stop) for b in BODIES}
        self.jd = self.tab["10"][:, 0]

    def pos(self, b, jd):
        t = self.tab[b]
        return np.array([np.interp(jd, t[:, 0], t[:, k]) for k in (1, 2, 3)])

    def vel(self, b, jd):
        t = self.tab[b]
        return np.array([np.interp(jd, t[:, 0], t[:, k]) for k in (4, 5, 6)])


def elements_to_state(a, e, i, w, node, M):
    """Heliocentric ecliptic osculating elements (arrays) -> equatorial position, velocity (au, au/day)."""
    E = M.copy()
    for _ in range(50):
        dE = (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
        E -= dE
    cosE, sinE = np.cos(E), np.sin(E)
    n = np.sqrt(GM_SUN / a ** 3)
    xp, yp = a * (cosE - e), a * np.sqrt(1 - e * e) * sinE
    vxp = -a * n * sinE / (1 - e * cosE)
    vyp = a * n * np.sqrt(1 - e * e) * cosE / (1 - e * cosE)
    cw, sw, cn, sn, ci, si = np.cos(w), np.sin(w), np.cos(node), np.sin(node), np.cos(i), np.sin(i)
    P = np.array([cn * cw - sn * sw * ci, sn * cw + cn * sw * ci, sw * si])
    Q = np.array([-cn * sw - sn * cw * ci, -sn * sw + cn * cw * ci, cw * si])
    r = P * xp + Q * yp
    v = P * vxp + Q * vyp
    return EC2EQ @ r, EC2EQ @ v                     # shapes (3, N)


def integrate(elements, epoch_jd, jd_start, jd_end, planets, step=1.0):
    """Integrate from the elements' epoch back to jd_start (or forward, if jd_start is later).

    elements: (N,6) a,e,i,w,node,M (rad). Returns the daily grid (T,) and barycentric positions
    (T,3,N) as float32, keeping only times up to jd_end (None keeps everything) to save memory.
    """
    a, e, i, w, node, M = elements.T
    rh, vh = elements_to_state(a, e, i, w, node, M)
    r = rh + planets.pos("10", epoch_jd)[:, None]
    v = vh + planets.vel("10", epoch_jd)[:, None]

    def acc(jd, r):
        out = np.zeros_like(r)
        for b, mu in BODIES.items():
            d = planets.pos(b, jd)[:, None] - r
            out += GM_SUN * mu * d / np.sum(d * d, axis=0) ** 1.5
        return out

    def run(t0, t1):
        n = int(round(abs(t1 - t0) / step))
        h = math.copysign(step, t1 - t0)
        ts, rs = [], []
        rr, vv, t = r0.copy(), v0.copy(), t0
        for _ in range(n):
            k1v, k1r = acc(t, rr), vv
            k2v, k2r = acc(t + h / 2, rr + h / 2 * k1r), vv + h / 2 * k1v
            k3v, k3r = acc(t + h / 2, rr + h / 2 * k2r), vv + h / 2 * k2v
            k4v, k4r = acc(t + h, rr + h * k3r), vv + h * k3v
            rr = rr + h / 6 * (k1r + 2 * k2r + 2 * k3r + k4r)
            vv = vv + h / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
            t += h
            if jd_end is None or t <= jd_end + 3:
                ts.append(t); rs.append(rr.astype(np.float32))
        return np.array(ts), np.array(rs)

    r0, v0 = r, v
    tb, rb = run(epoch_jd, jd_start)                # backwards to the start of Gaia observations
    order = np.argsort(tb)
    return tb[order], rb[order]


def interp_positions(grid_t, grid_r, k, jd):
    """Cubic (Catmull-Rom) interpolation of asteroid k at times jd; grid is uniform."""
    h = grid_t[1] - grid_t[0]
    x = (np.asarray(jd) - grid_t[0]) / h
    i = np.clip(np.floor(x).astype(int), 1, len(grid_t) - 3)
    s = (x - i)[:, None]
    p0, p1, p2, p3 = grid_r[i - 1, :, k], grid_r[i, :, k], grid_r[i + 1, :, k], grid_r[i + 2, :, k]
    return 0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s ** 2 + (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3)
