"""Rotation-period search v3 = v2 + phase-angle-bisector (PAB) correction of the rotational phase.

The observed rotational phase drifts by -s*lambda_PAB/360 cycles (s = +1 prograde, -1 retrograde,
unknown), so the Fourier terms use 2*pi*(f*t - s*lam/360); both senses are tried and the better kept.

v2 notes:

Model for reduced magnitude y(t): one offset per observing season + linear phase term +
Fourier series in rotational phase. v2 changes against v1:
  * scan 2-1000 h (slow rotators) with a coarse grid, then refine the 30 deepest minima;
  * period uncertainty from the curvature of chi2 at the minimum;
  * P versus 2P decided later from BIC of a 4th-order model at both candidates (feature stored);
  * a richer feature vector for calibration on thousands of known periods.
"""
import os
import numpy as np

P_MIN_H, P_MAX_H = 2.0, 1000.0
ERR_FLOOR = 0.03
MIN_TRANSITS = 25
LIGHT_DAY_PER_AU = 0.0057755183
COARSE_STEP = float(os.environ.get("PERIOD2_COARSE", 0.5))   # coarse grid step in units of 1/span


def design(t, alpha, season, f, order, off=0.0):
    """Design matrix for one frequency (rotations/day)."""
    cols = [season, alpha[:, None]]
    ph = 2 * np.pi * f * t + off
    for k in range(1, order + 1):
        cols += [np.cos(k * ph)[:, None], np.sin(k * ph)[:, None]]
    return np.hstack(cols)


def chi2_grid(t, y, sw, base, freqs, order=2, chunk=3000, off=0.0):
    """Weighted chi2 of the Fourier model for many frequencies at once."""
    out = np.empty(len(freqs))
    b = y * sw
    Bw = base * sw[:, None]
    for a in range(0, len(freqs), chunk):
        f = freqs[a:a + chunk]
        ph = 2 * np.pi * np.outer(f, t) + off
        parts = [np.broadcast_to(Bw, (len(f),) + Bw.shape)]
        for k in range(1, order + 1):
            parts += [(np.cos(k * ph) * sw)[..., None], (np.sin(k * ph) * sw)[..., None]]
        A = np.concatenate(parts, axis=2)
        AtA = np.einsum("fni,fnj->fij", A, A) + 1e-10 * np.eye(A.shape[2])
        Atb = np.einsum("fni,n->fi", A, b)
        x = np.linalg.solve(AtA, Atb[..., None])[..., 0]
        out[a:a + chunk] = np.sum(b * b) - np.einsum("fi,fi->f", x, Atb)   # residual = b'b - x'A'b
    return out


def fit(t, y, w, base, f, order, off=0.0):
    A = np.hstack([base, design(t, base[:, -1], base[:, :-1], f, order, off)[:, base.shape[1]:]])
    sw = np.sqrt(w)
    x, *_ = np.linalg.lstsq(A * sw[:, None], y * sw, rcond=None)
    return float(np.sum(w * (y - A @ x) ** 2)), x, A.shape[1]


def prepare(mag, rel_err, r, delta, alpha, t_lt, lam):
    """Reduced magnitudes, weights, season design. Returns None if too few transits."""
    y = mag - 5 * np.log10(r * delta)
    sig = np.hypot(1.0857 * rel_err, ERR_FLOOR)
    w = 1 / sig ** 2
    t = t_lt
    season = np.concatenate([[0], np.cumsum(np.diff(t) > 60)])
    S = np.eye(season.max() + 1)[season]
    base = np.hstack([S, alpha[:, None]])
    lam = np.unwrap(np.radians(lam))
    for _ in range(2):        # clip gross outliers against the phase-curve-only model
        sw = np.sqrt(w)
        c, *_ = np.linalg.lstsq(base * sw[:, None], y * sw, rcond=None)
        res = y - base @ c
        mad = np.median(np.abs(res - np.median(res))) * 1.4826 + 1e-3
        keep = np.abs(res) < 5 * mad
        if keep.all():
            break
        t, y, w, base, lam = t[keep], y[keep], w[keep], base[keep], lam[keep]
        base = base[:, np.concatenate([base[:, :-1].any(axis=0), [True]])]   # drop seasons emptied by clipping
    if len(t) < MIN_TRANSITS:
        return None
    return t, y, w, base, lam


def search(t, y, w, base, lam, n_refine=30):
    best = None
    for sense in (1, -1):
        r = search_one(t, y, w, base, -sense * lam, n_refine)
        r["sense"] = sense
        if best is None or r["chi_best"] < best["chi_best"]:
            best = r
    return best


def search_one(t, y, w, base, off, n_refine=30):
    span = t.max() - t.min()
    sw = np.sqrt(w)
    c, *_ = np.linalg.lstsq(base * sw[:, None], y * sw, rcond=None)
    chi_null = float(np.sum(w * (y - base @ c) ** 2))
    f_lo, f_hi = 24 / P_MAX_H, 24 / P_MIN_H
    coarse = np.arange(f_lo, f_hi, COARSE_STEP / span)
    chi_c = chi2_grid(t, y, sw, base, coarse, off=off)
    # local minima of the coarse periodogram, deepest first
    lm = np.where((chi_c[1:-1] <= chi_c[:-2]) & (chi_c[1:-1] <= chi_c[2:]))[0] + 1
    lm = lm[np.argsort(chi_c[lm])][:n_refine]
    cand = []
    for i in lm:
        fine = np.linspace(coarse[i] - 0.6 / span, coarse[i] + 0.6 / span, 49)
        fine = fine[(fine > f_lo * 0.98) & (fine < f_hi * 1.02)]
        cf = chi2_grid(t, y, sw, base, fine, off=off)
        j = int(np.argmin(cf))
        # curvature-based uncertainty from a parabola through the minimum region
        lo, hi = max(j - 3, 0), min(j + 4, len(fine))
        sigma_f = np.nan
        if hi - lo >= 5:
            pcoef = np.polyfit(fine[lo:hi] - fine[j], cf[lo:hi], 2)
            if pcoef[0] > 0:
                n_par = base.shape[1] + 4
                rchi = cf[j] / max(len(t) - n_par, 1)
                sigma_f = float(np.sqrt(2 * rchi / (2 * pcoef[0])))
        cand.append((float(cf[j]), float(fine[j]), sigma_f))
    cand.sort()
    best_chi, f_best, sigma_f = cand[0]
    # second independent minimum: away from f_best and its x2 / x0.5 aliases
    second = next((c for c in cand[1:] if all(abs(c[1] - g) > 3 / span for g in (f_best, 2 * f_best, f_best / 2))), cand[-1])
    # P versus 2P: compare a 4th-order model at f_best and f_best/2 by BIC
    n = len(t)
    chi4_p, x4p, k4 = fit(t, y, w, base, f_best, 4, off)
    chi4_2p, x42, _ = fit(t, y, w, base, f_best / 2, 4, off) if f_best / 2 >= f_lo else (np.inf, None, k4)
    bic_p = chi4_p + k4 * np.log(n)
    bic_2p = chi4_2p + k4 * np.log(n)
    # amplitude of the order-2 model at f_best
    chi2_b, x2, _ = fit(t, y, w, base, f_best, 2, off)
    grid = np.linspace(0, 2 * np.pi, 200)
    four = sum(x2[-4 + 2 * (k - 1)] * np.cos(k * grid) + x2[-3 + 2 * (k - 1)] * np.sin(k * grid) for k in (1, 2))
    # Shape test for P vs 2P: an elongated body gives a double-peaked curve, i.e. the 2nd harmonic
    # dominates at the true period. If the 1st harmonic dominates at f_best, f_best is likely the
    # single-peaked half period.
    a1, a2 = float(np.hypot(x2[-4], x2[-3])), float(np.hypot(x2[-2], x2[-1]))
    return {
        "n": n, "span": round(float(span), 1), "seasons": int(base.shape[1] - 1),
        "f_best": f_best, "p_best": 24 / f_best, "p_err": (24 * sigma_f / f_best ** 2) if np.isfinite(sigma_f) else None,
        "p_second": 24 / second[1], "chi_null": chi_null, "chi_best": best_chi, "chi_second": second[0],
        "gain": chi_null / best_chi, "unique": second[0] / best_chi, "rchi2": best_chi / max(n - base.shape[1] - 4, 1),
        "dbic_double": float(bic_p - bic_2p), "chi4_ratio": float(chi4_2p / chi4_p) if np.isfinite(chi4_2p) else None,
        "amp": float(four.max() - four.min()), "a1": a1, "a2": a2, "harm_ratio": a1 / (a2 + 1e-6),
    }
