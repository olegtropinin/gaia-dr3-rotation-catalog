# Rotation periods for the whole Gaia DR3 asteroid sample: method and results (review brief)

Author: independent researcher (Oleg Tropynin). Purpose of the pipeline: be ready to process Gaia DR4
(~Dec 2026) within a day of release. A first note on 42 candidates from a 600-asteroid pilot is under
editorial consideration at RNAAS; this run is the full-DR3 version with a new method (v2).

## Data
- Gaia DR3 `sso_observation`, all 20 bulk files (23.3 M CCD rows). Rows grouped by (number_mp, transit_id)
  and averaged -> 3,069,170 transits of 156,789 numbered asteroids. Per-transit error: max sigma_F/F over CCDs.
- Targets: 42,195 asteroids with >= 25 transits (median for all asteroids is 17).
- Geometry: osculating elements (JPL ELEMENTS.NUMBR, epoch 2026-Jun) integrated numerically back to
  2014-2017 with RK4 (step 1 d; Sun + Jupiter, Saturn, Uranus, Neptune from JPL Horizons vectors).
  Gaia's barycentric position is taken from the data. Light-time iterated 3x. Checked against Horizons on
  19 asteroids: |dDelta| <= 0.0005 au, |dalpha| <= 0.009 deg, reduced-magnitude error <= 0.0007 mag.
  (A two-body Kepler solution was rejected: errors up to 0.13 mag.)

## Model and period search
- Reduced magnitude y = G - 5 log10(r Delta). Model: one constant per observing season (gap > 60 d) +
  linear phase-angle term + Fourier series of order 2 in rotational phase. Weights 1/sigma^2,
  sigma = hypot(1.0857 sigma_F/F, 0.03 mag). Two passes of 5-MAD clipping against the no-rotation model.
- Frequency scan: periods 2-1000 h, coarse grid step 0.5/T (T = time span), refine the 30 deepest
  minima on a fine grid; period error from the curvature of chi2 at the minimum.
- P vs 2P: an elongated body gives a double-peaked lightcurve, so at the true period the 2nd harmonic
  dominates. If A1/A2 (amplitudes of 1st/2nd harmonics at the best period) > threshold, 2P is adopted.
  The threshold (1.15) was chosen on the TUNE half (below). A BIC comparison of 4th-order models at P and
  2P was tried first and rejected: it preferred the half period.
- Features per asteroid: gain = chi2_null/chi2_best, unique = chi2_second/chi2_best (second = deepest
  minimum not within 3/T of f, 2f or f/2), n transits, amplitude, reduced chi2, period, A1/A2.

## Calibration and validation
- Truth: LCDB V4.0 summary periods with quality U >= 2 (any of 2, 2+, 2-, 3, 3-; binaries not excluded).
  Match = within 3 %.
- Split: known asteroids split 50/50 by a hash of their number into TUNE (4,779) and TEST (4,834).
  On TUNE: the A1/A2 threshold, then a logistic regression P(correct | features), then a probability
  threshold giving 80 % precision on TUNE (0.518). TEST is used once, for the report.

## Results
- 41,842 asteroids solved (353 dropped: too few transits after clipping); runtime ~10 min on 10 cores.
- TEST, all solutions: 45.5 % match LCDB (TUNE 44.2 %).
- TEST, confident (prob >= 0.518): 1,909 asteroids, **1,507 correct = 78.9 %**; recall 68.5 % of all
  correct TEST solutions.
  By period band (confident TEST): 2-10 h 1000/1244 (80 %), 10-30 h 362/441 (82 %),
  30-100 h 112/142 (79 %), 100-1000 h 33/82 (40 %).
  By number of transits: 25-30: 72 %, 30-40: 82 %, 40-60: 80 %, >= 60: 79 %.
- Probability calibration on TEST (all solutions): predicted 0.15/0.39/0.59/0.77/0.94 vs observed
  0.14/0.42/0.66/0.79/0.89 in bins 0-0.3/0.3-0.5/0.5-0.7/0.7-0.85/0.85-1.
- Confident overall: 9,251 (5,530 of them have no LCDB period).
- Comparison of confident periods with published catalogues (agree = within 3 %):

  | Catalogue | Data | n | agree | factor-2 | other |
  |---|---|---|---|---|---|
  | Durech & Hanus 2023 | Gaia DR3 | 4507 | 92.4 % | 26 | 317 |
  | Cellino et al. 2024 | Gaia DR3 | 3966 | 92.9 % | 16 | 267 |
  | MacLennan et al. 2026 | Gaia DR3 | 3707 | 92.8 % | 14 | 252 |
  | Vavilov & Carry 2025 | TESS | 1067 | 79.9 % | 38 | 177 |
  | Erasmus et al. 2020 | ATLAS | 338 | 59.5 % | 1 | 136 |
  | McNeill et al. 2023 | TESS | 1277 | 46.0 % | 17 | 672 |

  Three-way check where LCDB also has the asteroid: McNeill subset (947): ours agree with LCDB 793,
  McNeill agree with LCDB 560. Erasmus subset (338): ours 237, theirs 264. Vavilov subset (1066):
  ours 861, theirs 875.
- **New: 1,982 confident periods absent from LCDB and from all six catalogues above.** Bands: 2-10 h 1237,
  10-30 h 269, 30-100 h 204, 100-1000 h 272. Sum of calibrated probabilities = 1,439 (73 %). 862 of them
  have only 25-30 transits (the 72 % precision bin).

## Known limitations (author's own list)
- Novelty for the 1,982 was checked only against LCDB V4.0 and the six catalogues; the pilot also checked
  DAMIT, 113+66 VizieR tables and Minor Planet Bulletin full text, which is not yet repeated here.
- LCDB-known asteroids are brighter / better observed than the unknown ones; TEST precision is measured
  on that population.
- The 100-1000 h band is unreliable (40 %).
- Same-data catalogues (Gaia DR3) agreeing at 92 % is a consistency check, not independent truth.
- No pole/shape solutions; only sidereal-vs-synodic is ignored (single-period model over ~3 years).
