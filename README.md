# Rotation periods of 41,842 asteroids from Gaia DR3 sparse photometry

Status: **draft, not yet released.** Version 2 of the method behind
[gaia-asteroid-periods](https://github.com/olegtropinin/gaia-asteroid-periods) (pilot on 600 asteroids,
RNAAS submission AAS82759), now run on every numbered asteroid with at least 25 Gaia DR3 transits.
Author: Oleg Tropynin, independent researcher, Kazakhstan.

## What is in it

| File | Rows | Content |
|---|---|---|
| `data/gaia_dr3_rotation_periods.csv` | 41,842 | every solved asteroid, with tier, probability and flags |
| `data/novel_tierA.csv` | 837 | tier-A periods with no published period found anywhere we checked |
| `validation/stats_final.json` | | every number quoted below, computed from the catalogue |
| `validation/report.json`, `lit_report.json` | | calibration report and literature comparison |
| `validation/REVIEW_BRIEF.md` | | the brief given to two independent referees (see below) |
| `paper/` | | figures (and the draft manuscript) |
| `code/` | | the full pipeline |

Columns of the catalogue:
- `period_h`, `period_err_h`: rotation period and its 1-sigma error. The error is the chi2-curvature
  error plus a systematic 2.4e-4 P in quadrature (see *Period errors*).
- `tier`: `A` = confident; `B` = probable; empty = not reliable.
- `prob_correct`: calibrated probability that the period is right within 3 %.
- `slow_candidate`: the best period is 100-1000 h and the probability is high. These are **never**
  confident, because only about 40 % of them are right.
- `second_period_h`: the deepest periodogram minimum that is not a x1, x2 or x0.5 alias of the best one.
- `amplitude_mag`, `n_transits`, `span_d`.
- `lcdb_period_h`, `lcdb_split`: LCDB V4.0 period (quality U >= 2), and whether the asteroid was in the
  TUNE or TEST half, or is `unknown`.
- `novel`: the asteroid is in `novel_tierA.csv`.

## Method in one paragraph

Gaia DR3 `sso_observation` CCD rows are averaged per transit (3.07 M transits, 156,789 numbered
asteroids). Geometry comes from osculating elements integrated numerically with RK4 (Sun and the four
giant planets). It matches JPL Horizons to 0.0007 mag in reduced magnitude. The model has one offset
per observing season, a linear phase-angle term and a second-order Fourier series in rotational phase.
Periods of 2-1000 h are scanned. The doubled period is adopted when the first harmonic dominates the
second (A1/A2 > 1.15), because most asteroid lightcurves are double-peaked. A logistic model gives
`prob_correct` from the periodogram features.

## How reliable it is

Asteroids with a known LCDB period were split once, by a hash of their number, into TUNE (4,779) and
TEST (4,834). Everything was chosen on TUNE or on a null test, and TEST was used only to report.

| | TEST precision |
|---|---|
| tier A (prob >= 0.70, P < 100 h) | **86.3 %** (1079/1250); 2-10 h 87 %, 10-30 h 85 %, 30-100 h 80 % |
| tier B (0.478 <= prob < 0.70) | 67 % (473/706) |
| all solutions | 45.5 % |

Errors among tier-A TEST results: 156 other periods, 11 at 2P, 4 at P/2. The probabilities are
calibrated on TEST: predicted 0.15 / 0.39 / 0.60 / 0.77 / 0.94, observed 0.14 / 0.42 / 0.66 / 0.79 / 0.89.

How the tier-A threshold was set:
- **Null test.** Residuals were permuted within seasons for 4,000 random asteroids without a known
  period. This keeps the sampling, the errors and the season levels, but removes any rotation.
- At the TUNE 80 %-precision threshold (0.478), 6.9 % of these signal-free asteroids would pass. That
  could make up to ~40 % of the "confident" unknown periods noise.
- At 0.70, only 0.8 % pass. This is why tier A starts at 0.70. The threshold came from the null test,
  not from TEST.

How the precision transfers to the new periods:
- The new periods belong to asteroids that other Gaia DR3 analyses did not publish. TEST asteroids are
  brighter and better studied.
- The nearest analogue with known answers: TEST asteroids that are absent from all six catalogues below.
  Tier A gets **137/161 = 85 %** right on them (95 % CI 80-91 %).
- For the new periods we therefore expect about 85 %, not more.

## Comparison with other catalogues (tier A, agreement within 3 %)

| Catalogue | Data | Agreement |
|---|---|---|
| Durech & Hanus 2023 | Gaia DR3 | 3046/3117 = 97.7 % |
| Cellino et al. 2024 | Gaia DR3 | 2709/2765 = 98.0 % |
| MacLennan et al. 2026 | Gaia DR3 | 2525/2580 = 97.9 % |
| Vavilov & Carry 2025 | TESS | 589/660 = 89.2 % |
| Erasmus et al. 2020 | ATLAS | 158/228 = 69.3 % |
| McNeill et al. 2023 | TESS | 407/774 = 52.6 % |

The three Gaia rows use the same data, so they show consistency, not accuracy.

On TEST asteroids that are also in an independent catalogue, here is how often each side agrees with LCDB:

| Subset | This work | The catalogue |
|---|---|---|
| Vavilov & Carry (362) | 320 | 316 |
| Erasmus (114) | 86 | 89 |
| McNeill (332) | 302 | 211 |

The low agreement with McNeill et al. mostly reflects that catalogue.

## Novelty of the 837

A period counts as novel when it is a tier-A period for an asteroid that has none of the following:
- an LCDB V4.0 period;
- an entry in the six catalogues above;
- an entry in DAMIT;
- a period in about 180 VizieR tables with asteroid rotation periods (5.0 M rows);
- a mention in the full text of the Minor Planet Bulletin, vols. 50-53.

Before these checks there were 912 such periods; 75 were already published. Where a published period
exists (56 cases), we agree with it in 38 (68 %).

Not checked: Behrend's Geneva page, ZTF catalogues outside VizieR, individual papers.

The breakdown of the 837 by period: 602 at 2-10 h, 140 at 10-30 h, 95 at 30-100 h.

## Period errors

The chi2-curvature error alone is too small, by a factor of about 25. The model fits a single
(synodic-like) period over about 3 years. Against Durech & Hanus (sidereal periods from the same data),
the median |dP/P| is 1.6e-4, about P/P_orbit. A systematic term of 2.4e-4 P in quadrature gives a median
|dP|/sigma of 0.65, against 0.674 for a Gaussian, on both halves of a split.

## Known limitations

- **P versus 2P.** The A1/A2 rule is crude. A model-based test (ellipsoid or convex fit at P and 2P) is
  planned for DR4.
- **Synodic effect.** It is not modelled. Phase-angle-bisector correction is planned for DR4.
- **Slow rotators (100-1000 h)** are flagged, not trusted. A single-period model also cannot describe
  tumblers.
- **Truth set.** The LCDB truth includes U = 2 (TEST precision is 81 % on U >= 3- and 78 % on U = 2,
  before tiering).
- **Pilot candidates.** Of the 42 candidates in the pilot note:
  - 35 agree with v2;
  - 4 flagged "low" are doubled by v2;
  - for 3 flagged "high" (39932, 109412, 13686), v2 prefers a slow solution with low probability.
    Those 3 are ambiguous.
- **Independent review.** Two independent referees (statistics and planetary science) read
  `validation/REVIEW_BRIEF.md`. The tiers, the null test, the matched control, the slow-rotator flag and
  the period-error term are the changes made in response.

## Reproduce

`code/prep_gaia.py` (bulk DR3 files → transits) → `code/pipeline.py --workers 10` (~10 min on 10 cores)
→ `code/calibrate2.py` → `code/compare_lit.py`, `make_new.py`, `stats_final.py`, `make_figures.py`.
Null test: `PIPELINE_RESULTS=results_null PIPELINE_NULL=1 python pipeline.py --only-file <list>`.

## Acknowledgements

ESA Gaia / DPAC; JPL Horizons and SBDB; LCDB (Warner, Harris & Pravec); VizieR (CDS). The analysis was
designed, coded and checked with the help of an AI assistant (Claude, Anthropic) under the author's
direction.
