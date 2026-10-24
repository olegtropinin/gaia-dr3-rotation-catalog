"""Calibrate the v2 results against LCDB periods and measure accuracy on a held-out half.

Truth: LCDB V4.0 summary periods with quality U >= 2 (2-100 h is where Gaia can say anything useful,
but 2-1000 h is kept so slow rotators count as failures when missed).
Split: asteroids with known periods are divided by a hash of their number into TUNE and TEST.
On TUNE we choose (1) the 1st/2nd-harmonic amplitude ratio above which 2P is adopted and (2) a logistic model of
P(correct | features) and its threshold for 80% precision. TEST is touched once, for the report.
Writes catalog.csv (every asteroid, with final period and probability) and report.json.
"""
import csv, glob, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TOL = 0.03
# Null test (residuals permuted within seasons, 4000 random unknown asteroids): at prob >= 0.70 only 0.8 % of
# signal-free asteroids pass, i.e. at most ~7 % of confident unknowns could be noise; at the TUNE-precision
# threshold (~0.48) up to 40 %. Chosen from the null test alone, not from TEST.
CONF_PROB_MIN = 0.70
# The chi2-curvature error ignores residual model error. With the PAB correction (v3) the median |dP/P| against
# Durech & Hanus 2023 (sidereal, same data) is 3.9e-5 (v2 without PAB: 1.6e-4); a systematic term of 5.5e-5 P in
# quadrature gives median |dP|/sigma ~0.67 (Gaussian: 0.674) on both halves of a split.
SYS_REL_ERR = 5.5e-5
CONF_MAX_P = 100.0   # referees: the 100-1000 h band is 40 % correct, so it is never 'confident' (flag slow_candidate)


def load_results(sub="results"):
    rows = []
    for f in sorted(glob.glob(os.path.join(HERE, sub, "chunk_*.jsonl"))):
        rows += [json.loads(l) for l in open(f)]
    return [r for r in rows if "p_best" in r]


def load_lcdb(path=os.path.join(HERE, "data", "lc_summary.csv")):
    lines = open(path, encoding="latin-1").read().splitlines()
    hdr = next(i for i, l in enumerate(lines) if l.lower().startswith("number,"))
    out = {}
    for r in csv.DictReader(lines[hdr + 1:], fieldnames=lines[hdr].split(",")):
        try:
            n, p = int(r["Number"]), float(r["Period"])
        except (TypeError, ValueError):
            continue
        u = (r["U"] or "").strip().rstrip("+-")
        if u in ("2", "3") and p > 0:
            out[n] = p
    return out


def is_test(num):
    return (num * 2654435761) % 1000 < 500        # deterministic 50/50 split


def final_period(r, t_harm):
    """Double the best period when the 1st harmonic dominates (single-peaked curve = half period)."""
    return r["p_best"] * 2 if (r["harm_ratio"] > t_harm and r["p_best"] * 2 <= 1000) else r["p_best"]


def match(p, q):
    return abs(p - q) / q < TOL


FEATS = ("log_gain", "log_unique", "log_n", "amp", "log_rchi2", "log_p", "log_harm_ratio")


def features(r, tbic):
    p = final_period(r, tbic)
    return np.array([math.log(max(r["gain"], 1e-9)), math.log(max(r["unique"], 1e-9)), math.log(r["n"]),
                     min(r["amp"], 2.0), math.log(max(r["rchi2"], 1e-9)), math.log(p),
                     math.log(max(r["harm_ratio"], 1e-3))])


def logistic_fit(X, y, l2=1e-2, iters=500):
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Z = np.hstack([(X - mu) / sd, np.ones((len(X), 1))])
    w = np.zeros(Z.shape[1])
    for _ in range(iters):                         # Newton steps
        p = 1 / (1 + np.exp(-Z @ w))
        g = Z.T @ (p - y) + l2 * w
        H = (Z * (p * (1 - p))[:, None]).T @ Z + l2 * np.eye(len(w))
        step = np.linalg.solve(H, g)
        w -= step
        if np.abs(step).max() < 1e-8:
            break
    return lambda X_: 1 / (1 + np.exp(-np.hstack([(X_ - mu) / sd, np.ones((len(X_), 1))]) @ w))


def calibrate(res, lcdb):
    """TUNE-only choices: doubling threshold, probability model, probability threshold (80 % precision)."""
    known = [r for r in res if r["num"] in lcdb]
    tune = [r for r in known if not is_test(r["num"])]
    grid = np.linspace(0.5, 6.0, 111)
    tbic = max(grid, key=lambda g: sum(match(final_period(r, g), lcdb[r["num"]]) for r in tune))
    Xt = np.array([features(r, tbic) for r in tune])
    yt = np.array([match(final_period(r, tbic), lcdb[r["num"]]) for r in tune], float)
    model = logistic_fit(Xt, yt)
    pt = model(Xt)
    short = np.array([final_period(r, tbic) < CONF_MAX_P for r in tune])
    order = np.argsort(-pt[short])
    prec = np.cumsum(yt[short][order]) / np.arange(1, short.sum() + 1)
    ok = np.where(prec >= 0.8)[0]
    thr = float(pt[short][order][ok.max()]) if len(ok) else 1.0
    return tbic, model, thr, yt


def confident(r, p, tbic, thr):
    return p >= max(thr, CONF_PROB_MIN) and final_period(r, tbic) < CONF_MAX_P


def tier(r, p, tbic, thr):
    """A = confident; B = above the TUNE 80 %-precision threshold but below the null-test bound; '' otherwise."""
    if final_period(r, tbic) >= CONF_MAX_P:
        return ""
    return "A" if p >= max(thr, CONF_PROB_MIN) else "B" if p >= thr else ""


def main():
    res = load_results()
    lcdb = load_lcdb()
    known = [r for r in res if r["num"] in lcdb]
    tune = [r for r in known if not is_test(r["num"])]
    test = [r for r in known if is_test(r["num"])]
    tbic, model, thr, yt = calibrate(res, lcdb)
    # 3) TEST, touched once
    Xs = np.array([features(r, tbic) for r in test])
    ys = np.array([match(final_period(r, tbic), lcdb[r["num"]]) for r in test], float)
    ps = model(Xs)
    sel = np.array([confident(r, p, tbic, thr) for r, p in zip(test, ps)])

    def bands(rows, probs, mask):
        out = {}
        for lo, hi in ((2, 10), (10, 30), (30, 100), (100, 1000)):
            idx = [i for i, r in enumerate(rows) if mask[i] and lo <= final_period(r, tbic) < hi]
            if idx:
                out[f"{lo}-{hi}h"] = {"n": len(idx), "correct": int(sum(match(final_period(rows[i], tbic), lcdb[rows[i]["num"]]) for i in idx))}
        return out

    report = {
        "n_results": len(res), "n_known_lcdb_u2plus": len(known), "n_tune": len(tune), "n_test": len(test),
        "double_harm_threshold": float(tbic), "prob_threshold": thr,
        "tune_all_match_rate": float(yt.mean()), "test_all_match_rate": float(ys.mean()),
        "test_confident": int(sel.sum()), "test_confident_correct": int(ys[sel].sum()),
        "test_confident_precision": float(ys[sel].mean()) if sel.any() else None,
        "test_recall_of_correct": float(ys[sel].sum() / max(ys.sum(), 1)),
        "test_bands_confident": bands(test, ps, sel),
    }
    json.dump(report, open(os.path.join(HERE, "report.json"), "w"), indent=1)
    print(json.dumps(report, indent=1))
    # catalog for every asteroid
    with open(os.path.join(HERE, "catalog.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["number", "period_h", "period_err_h", "alias_period_h", "amplitude_mag", "n_transits", "span_d",
                    "prob_correct", "confident", "tier", "slow_candidate", "lcdb_period_h", "split"])
        X = np.array([features(r, tbic) for r in res])
        P = model(X)
        for r, p in zip(res, P):
            fp = final_period(r, tbic)
            perr = math.hypot(r["p_err"] * (2 if fp != r["p_best"] else 1), SYS_REL_ERR * fp) if r.get("p_err") else ""
            w.writerow([r["num"], f"{fp:.5f}", f"{perr:.5f}" if perr != "" else "", f"{r['p_second']:.4f}", f"{r['amp']:.3f}",
                        r["n"], r["span"], f"{p:.3f}", int(confident(r, p, tbic, thr)), tier(r, p, tbic, thr), int(p >= thr and fp >= CONF_MAX_P), lcdb.get(r["num"], ""),
                        ("test" if is_test(r["num"]) else "tune") if r["num"] in lcdb else "unknown"])


if __name__ == "__main__":
    main()
