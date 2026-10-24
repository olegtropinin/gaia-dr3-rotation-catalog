"""Run the v2 period search on every numbered asteroid in data/transits.npz.

Chunks of CHUNK asteroids: integrate their orbits together (nbody.py), compute Gaia-centric
geometry, then search periods in a process pool. One results/chunk_NNNNN.jsonl per chunk, so a
restart skips finished chunks. Usage: pipeline.py [--workers 6] [--limit-chunks N] [--only NUM,...]
"""
import argparse, json, os, sys, time
from multiprocessing import Pool
import numpy as np
import geom, nbody, period2

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, os.environ.get("PIPELINE_RESULTS", "results"))
NULL_SEED = os.environ.get("PIPELINE_NULL")   # set: permute residuals within seasons (false-alarm test)
CHUNK = 2000


def log(msg):
    line = time.strftime("%H:%M:%S ") + msg
    print(line, flush=True)
    with open(os.path.join(HERE, "pipeline.log"), "a") as f:
        f.write(line + "\n")


def work(args):
    num, arrays = args
    try:
        prep = period2.prepare(*arrays)
        if prep is None:
            return {"num": int(num), "skip": "too few transits after clipping"}
        if NULL_SEED is not None:
            t, y, w, base = prep
            sw = np.sqrt(w)
            c, *_ = np.linalg.lstsq(base * sw[:, None], y * sw, rcond=None)
            fit = base @ c
            res = y - fit
            rng = np.random.default_rng(int(NULL_SEED) + int(num))
            season = base[:, :-1].argmax(axis=1)
            for s_ in np.unique(season):           # shuffle residuals within each season: keeps sampling, errors and season levels
                m = np.where(season == s_)[0]
                res[m] = res[rng.permutation(m)]
            prep = (t, fit + res, w, base)
        res = period2.search(*prep)
        res["num"] = int(num)
        return res
    except Exception as e:  # keep the chunk alive; record the failure
        return {"num": int(num), "error": repr(e)[:200]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit-chunks", type=int, default=0)
    ap.add_argument("--only", default="")
    ap.add_argument("--only-file", default="", help="file with one asteroid number per line")
    a = ap.parse_args()
    os.makedirs(RES, exist_ok=True)
    # dict(): an NpzFile re-reads and decompresses the whole array on every T["key"] access
    T = dict(np.load(os.path.join(HERE, "data", "transits.npz")))
    els = geom.load_elements()
    planets = nbody.Planets()
    nums, start, count = T["nums"], T["start"], T["count"]
    ok = (count >= period2.MIN_TRANSITS) & np.isin(nums, list(els.keys()))
    if a.only:
        ok &= np.isin(nums, [int(x) for x in a.only.split(",")])
    if a.only_file:
        ok &= np.isin(nums, [int(x) for x in open(a.only_file).read().split()])
    idx = np.where(ok)[0]
    log(f"targets: {len(idx)} asteroids with >= {period2.MIN_TRANSITS} transits and elements")
    # Integrate every target orbit once, one vectorised run per element epoch: per-step Python
    # overhead is shared by all asteroids instead of paid again for each chunk.
    t0 = time.time()
    orbit = {}                       # num -> (group, column)
    groups = []
    by_epoch = {}
    for k in idx:
        by_epoch.setdefault(els[int(nums[k])][0], []).append(k)
    for ep, ks in sorted(by_epoch.items(), key=lambda x: -len(x[1])):
        E = np.array([els[int(nums[k])][1:] for k in ks])
        lo = min(T["epoch"][start[k]] for k in ks) - 6
        hi = max(T["epoch"][start[k] + count[k] - 1] for k in ks) + 6
        gt, gr = nbody.integrate(E, ep, lo, hi, planets)
        groups.append((gt, gr))
        for j, k in enumerate(ks):
            orbit[int(nums[k])] = (len(groups) - 1, j)
    log(f"orbits: {len(idx)} asteroids in {len(groups)} epoch groups, {time.time() - t0:.0f}s")
    done_chunks = 0
    for c0 in range(0, len(idx), CHUNK):
        sel = idx[c0:c0 + CHUNK]
        out = os.path.join(RES, f"chunk_{int(nums[sel[0]]):07d}.jsonl" if not a.only else "only.jsonl")
        if os.path.exists(out) and not a.only:
            continue
        t0 = time.time()
        jobs = []
        for k in sel:
            g, j = orbit[int(nums[k])]
            gt, gr = groups[g]
            s, n = start[k], count[k]
            jd = T["epoch"][s:s + n]
            gb = np.column_stack([T["gx"][s:s + n], T["gy"][s:s + n], T["gz"][s:s + n]])
            t = jd.copy()
            for _ in range(3):
                ast = nbody.interp_positions(gt, gr, j, t).astype(float)
                d = np.linalg.norm(ast - gb, axis=1)
                t = jd - d * period2.LIGHT_DAY_PER_AU
            rh = ast - planets.pos("10", t).T
            r = np.linalg.norm(rh, axis=1)
            cosa = np.sum(-rh * (gb - ast), axis=1) / (r * d)
            alpha = np.degrees(np.arccos(np.clip(cosa, -1, 1)))
            jobs.append((nums[k], (T["mag"][s:s + n].astype(float), T["rel_err"][s:s + n].astype(float), r, d, alpha, t)))
        t1 = time.time()
        with Pool(a.workers) as pool:
            results = pool.map(work, jobs, chunksize=8)
        with open(out + ".tmp", "w") as f:
            for r_ in results:
                f.write(json.dumps(r_) + "\n")
        os.replace(out + ".tmp", out)
        good = sum(1 for r_ in results if "p_best" in r_)
        log(f"chunk {c0 // CHUNK + 1}/{(len(idx) + CHUNK - 1) // CHUNK}: {len(sel)} asteroids, {good} solved, "
            f"geometry {t1 - t0:.0f}s, search {time.time() - t1:.0f}s")
        done_chunks += 1
        if a.limit_chunks and done_chunks >= a.limit_chunks:
            break


if __name__ == "__main__":
    main()
