# Rotation periods of 41,842 asteroids from Gaia DR3 sparse photometry

Status: **draft, not yet released.** This is version 3 of the method first piloted in
[gaia-asteroid-periods](https://github.com/olegtropinin/gaia-asteroid-periods) (600 asteroids; RNAAS
submission AAS82759). It now runs on every numbered asteroid with at least 25 Gaia DR3 transits.
Author: Oleg Tropynin, independent researcher, Kazakhstan.

## Contents

| File | Rows | Content |
|---|---|---|
| `data/gaia_dr3_rotation_periods.csv` | 41,842 | every solved asteroid, with its tier, probability and flags |
| `data/novel_tierA.csv` | 1,284 | tier-A periods with no published period found anywhere we checked |
| `validation/stats_final.json` | | every number quoted below, computed from the catalogue |
| `validation/report.json`, `lit_report.json` | | the calibration report and the literature comparison |
| `validation/REVIEW_BRIEF.md` | | the brief given to two independent referees (written for v2) |
| `paper/` | | the draft manuscript (`catalog.tex`, `catalog.pdf`) and its figures |
| `code/` | | the full pipeline |

Catalogue columns:
- `period_h`, `period_err_h`: the rotation period and its 1-sigma error (see *Period errors*).
- `tier`: `A` means confident, `B` means probable. Empty means not reliable.
- `prob_correct`: the calibrated probability that the period is correct within 3 %.
- `slow_candidate`: the best period is 100-1000 h and the probability is high. These periods are
  **never** treated as confident, because only about 40 % of them are correct.
- `second_period_h`: the deepest periodogram minimum that is not an alias (x1, x2 or x0.5) of the best one.
- `amplitude_mag`, `n_transits`, `span_d`: amplitude, number of transits and time span.
- `lcdb_period_h`, `lcdb_split`: the LCDB V4.0 period (quality U >= 2) and the split the asteroid belongs
  to: TUNE, TEST or `unknown`.
- `novel`: the asteroid is listed in `novel_tierA.csv`.

## Method

Data:
- Gaia DR3 `sso_observation` CCD rows are averaged per transit: 3.07 M transits of 156,789 numbered asteroids.
- Geometry comes from osculating elements integrated numerically with RK4, using the Sun and the four
  giant planets. Reduced magnitudes match JPL Horizons to 0.0007 mag.

Model:
- one offset per observing season;
- a linear phase-angle term;
- a second-order Fourier series in rotational phase.

The rotational phase is corrected for the phase-angle bisector (PAB). The observed phase drifts by
-s * lambda_PAB / 360 cycles, where s = +1 for prograde and -1 for retrograde rotation. Both senses are
tried and the better fit is kept.

Search and scoring:
- Periods from 2 to 1000 h are scanned.
- When the first harmonic dominates the second (A1/A2 > 1.20), the doubled period is adopted, because
  most asteroid lightcurves are double-peaked.
- A logistic model turns the periodogram features into `prob_correct`.

The PAB correction is the main change from v2. On the same TEST set (below), it:
- raises the fraction of correct periods from 45.5 % to 52.6 % over all solutions;
- raises the number of confident periods from 1,250 to 1,753, while precision goes up from 86.3 % to 87.8 %;
- cuts the median disagreement with the sidereal periods of Durech & Hanus 2023 by a factor of four,
  from 1.6e-4 to 3.9e-5 relative.

## Reliability

Asteroids with a known LCDB period were split once, by a hash of their number, into TUNE (4,779) and
TEST (4,834). Every choice was made on TUNE or on a null test. TEST was used only to report results.

| Group | TEST precision |
|---|---|
| tier A (prob >= 0.70, P < 100 h) | **87.8 %** (1540/1753): 2-10 h 89 %, 10-30 h 87 %, 30-100 h 84 % |
| tier B (prob between 0.384 and 0.70) | 62 % (595/953) |
| all solutions | 52.6 % |

Errors among the tier-A TEST results: 200 other periods, 11 at 2P and 2 at P/2.

The probabilities are calibrated on TEST:

| | | | | | |
|---|---|---|---|---|---|
| predicted | 0.16 | 0.39 | 0.60 | 0.78 | 0.95 |
| observed | 0.14 | 0.41 | 0.69 | 0.80 | 0.89 |

**How the tier-A threshold was chosen: the null test.** Residuals were permuted within seasons for
4,000 random asteroids without a known period. This keeps the sampling, the errors and the season
levels, but removes any rotation.
- At the TUNE threshold for 80 % precision (0.384), 19.8 % of these signal-free asteroids would pass.
- At 0.70, only 0.85 % pass, so at most about 6 % of the confident unknown periods could be noise.

Tier A therefore starts at 0.70. This threshold came from the null test, not from TEST.

**Transfer to the new periods.** TEST asteroids are brighter and better studied than asteroids without a
period. The nearest analogue with known answers is the set of TEST asteroids absent from all six
catalogues below. Tier A is correct for **242/278 = 87 %** of them (95 % CI 83-91 %).

## Comparison with other catalogues

Tier A, agreement within 3 %:

| Catalogue | Data | Agreement |
|---|---|---|
| Durech & Hanus 2023 | Gaia DR3 | 4241/4287 = 98.9 % |
| Cellino et al. 2024 | Gaia DR3 | 3336/3402 = 98.1 % |
| MacLennan et al. 2026 | Gaia DR3 | 3113/3178 = 98.0 % |
| Vavilov & Carry 2025 | TESS | 830/926 = 89.6 % |
| Erasmus et al. 2020 | ATLAS | 222/334 = 66.5 % |
| McNeill et al. 2023 | TESS | 567/1078 = 52.6 % |

The three Gaia rows use the same data, so they measure consistency, not accuracy.

For TEST asteroids that are also in an independent catalogue, both periods can be checked against LCDB:

| Catalogue | n | This work agrees with LCDB | The catalogue agrees with LCDB |
|---|---|---|---|
| Vavilov & Carry | 487 | 435 | 419 |
| Erasmus et al. | 175 | 133 | 135 |
| McNeill et al. | 447 | 411 | 273 |

## The 1,284 novel periods

1,400 tier-A asteroids have no period in LCDB V4.0 or in the six catalogues above. Of these, 116 have a
published period in one of:
- DAMIT;
- about 180 VizieR tables with asteroid rotation periods (5.0 M rows; matched on identifier columns only);
- the full text of the Minor Planet Bulletin, vols. 50-53.

Where a published period exists (89 cases), this work agrees with it in 63 (71 %).

The remaining **1,284** are novel. By period:

| Period | Count |
|---|---|
| 2-10 h | 977 |
| 10-30 h | 201 |
| 30-100 h | 106 |

The expected precision is about 87 %.

Not checked: Behrend's Geneva page, ZTF catalogues outside VizieR, and individual papers.

## Period errors

The error from the chi2 curvature alone is too small. Against Durech & Hanus (sidereal periods from the
same data), the median |dP/P| is 3.9e-5. Adding a systematic 5.5e-5 P in quadrature gives
median |dP|/sigma of about 0.67, against 0.674 for a Gaussian, on both halves of a split.

## Known limitations

- **P versus 2P.** The A1/A2 rule is crude. A model-based test (an ellipsoid or convex fit at P and at 2P)
  is planned for DR4.
- **Slow rotators (100-1000 h)** are flagged, not trusted. Tumblers are outside a single-period model.
- **The LCDB truth set** includes quality U = 2.
- **Pilot candidates.** Of the 42 in the pilot note:
  - 35 agree with v3;
  - v3 doubles the period of the 4 flagged "low";
  - for 3 flagged "high" (39932, 109412, 13686), v3 prefers a slow solution and none of them is tier A,
    so those 3 are ambiguous.
- **Independent review.** Two independent referees (statistics, and planetary science) reviewed v2. In
  response, v3 adds:
  - the tiers;
  - the null test;
  - the matched control;
  - the slow-rotator flag;
  - the period-error term;
  - the PAB correction.

## Reproduce

1. `code/prep_gaia.py`: bulk DR3 files to transits.
2. `PIPELINE_PAB=1 code/pipeline.py --workers 10`: about 20 min on 10 cores.
3. `code/calibrate2.py`.
4. `code/compare_lit.py`, `make_new.py`, `stats_final.py` and `make_figures.py`.

Null test: `PIPELINE_PAB=1 PIPELINE_NULL=1 PIPELINE_RESULTS=results_null python pipeline.py --only-file <list>`.

## Acknowledgements

ESA Gaia and DPAC; JPL Horizons and SBDB; LCDB (Warner, Harris & Pravec); VizieR (CDS). The analysis was
designed, coded and checked with the help of an AI assistant (Claude, Anthropic) under the author's
direction.
