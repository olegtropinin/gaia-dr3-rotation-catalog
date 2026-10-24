# Rotation periods and spin senses of asteroids from Gaia DR3 sparse photometry

Status: **draft, not yet released.** This is version 3 of the method first piloted in
[gaia-asteroid-periods](https://github.com/olegtropinin/gaia-asteroid-periods) (600 asteroids; RNAAS
submission AAS82759). It now runs on every numbered asteroid with at least 25 Gaia DR3 transits.
Author: Oleg Tropynin, independent researcher, Kazakhstan.

## Headline numbers

All numbers are in `validation/stats_final.json`.

**Solved:** 41,842 asteroids.

**Tier A (confident): 6,238 periods.**
- Held-out TEST asteroids: 89.3 % correct (1303/1459).
- TEST asteroids whose LCDB period has quality U >= 3-: **95.4 %** (354/371).
- Each tier-A period comes with a spin sense (prograde or retrograde). It agrees with published pole
  solutions for **98 %** of asteroids in Durech & Hanus 2023 and **97.5 %** in DAMIT.

**861 tier-A periods with no published value** in any source we checked:
- expected precision about 90 %;
- noise from the null tests: at most 3.7 % of this list.

## Contents

| File | Rows | Content |
|---|---|---|
| `data/gaia_dr3_rotation_periods.csv` | 41,842 | every solved asteroid, with tier, probability, spin sense and flags |
| `data/novel_tierA.csv` | 861 | tier-A periods with no published period found in the sources checked |
| `validation/stats_final.json` | | every number quoted here, computed from the catalogue |
| `validation/report.json`, `lit_report.json` | | calibration report, literature comparison |
| `validation/REVIEW_BRIEF*.md` | | the briefs given to the independent referees (rounds 1 and 2) |
| `paper/` | | draft manuscript (`catalog.tex`, `catalog.pdf`) and figures |
| `code/` | | the full pipeline |

Columns:
- `period_h`, `period_err_h`: the period and its 1-sigma error (see *Period errors*).
- `tier`: `A` = confident. `B` = probable, but B is **not** reliable for asteroids without a known
  period: 18 % of signal-free asteroids reach it in the null test.
- `prob_correct`: probability that the period is correct within 3 %, fitted on TUNE and checked on TEST.
- `spin_sense`: `prograde` or `retrograde`, given for tier A only.
- `slow_candidate`: the best period is 100-1000 h. Such periods are never confident, because only about
  40 % of them are correct.
- `second_period_h`: the deepest periodogram minimum that is not an x1, x2 or x0.5 alias.
- `amplitude_mag`: a lower limit, because the photometry is sparse.
- `n_transits`, `span_d`.
- `lcdb_period_h`, `lcdb_split`: the LCDB V4.0 period (U >= 2), with the asteroid's split (TUNE, TEST
  or `unknown`).
- `novel`: 1 if the asteroid is in `novel_tierA.csv`.

## Method

**Data.** Gaia DR3 `sso_observation` CCD rows are averaged per transit: 3.07 M transits of 156,789
numbered asteroids.

**Geometry.** Osculating elements are integrated with RK4 (Sun plus the four giant planets).
Reduced magnitudes match JPL Horizons to 0.0007 mag.

**Model.** The fit has:
- one offset per observing season;
- a linear phase-angle term;
- a second-order Fourier series in rotational phase, corrected for the phase-angle bisector (PAB).

**PAB correction.** The observed phase drifts by -s * lambda_PAB / 360 cycles (s = +1 prograde, -1
retrograde). Both senses are fitted and the better one is kept. This is what makes the spin sense
measurable.

**Search.**
- Periods of 2-1000 h are scanned.
- The doubled period is adopted when A1/A2 > 1.20.
- A logistic model fitted on TUNE gives `prob_correct`.

## Validation design

Known LCDB asteroids are split once, by a hash of their number, into TUNE (4,779) and TEST (4,834).

Fitted on TUNE:
- the doubling threshold;
- the logistic model.

Chosen from the null tests, never from TEST: the tier-A threshold (0.80).

Used only for reporting: TEST.

Two null tests (4,000 random asteroids without a known period) keep the real sampling, errors and
season levels but remove rotation:
- **white:** residuals permuted within seasons;
- **block:** residual blocks of one day permuted, so correlated systematics survive.

The rule, fixed before choosing the threshold: noise that could reach tier A must stay below 5 % even
inside the uncatalogued subset. Noise periods match no catalogue, so they all end up there.

| Threshold | White null pass | Block null pass | Noise bound (x 32,229 unknowns) |
|---|---|---|---|
| 0.384 (TUNE 80 % precision) | 19.8 % | 18.4 % | — |
| 0.70 | 0.85 % | 1.12 % | 274-363 |
| **0.80 (tier A)** | 0.10 % | 0.05 % | 16-32, i.e. <= 3.7 % of the 861 |

## Reliability

**TEST precision.**

| | TEST precision |
|---|---|
| tier A | **89.3 %** (1303/1459): 2-10 h 90 %, 10-30 h 88 %, 30-100 h 83 % |
| tier A, LCDB U >= 3- | **95.4 %** (354/371) |
| tier A, LCDB U = 2/2+ | 89.1 % (935/1049) |
| tier A, LCDB U = 2- | 36 % (14/39) |
| tier B | 67 % (832/1247), but see the null test |

**Where the 156 tier-A "errors" come from.** Many are errors in the truth set.
- 58 differ from LCDB by exactly **1 cycle/day** in lightcurve frequency. That is the daily alias of
  single-site ground-based photometry, and almost all are U = 2 or 2- entries.
- 6 are factor-2 differences.
- 92 are other.
- An independent TESS period (Vavilov & Carry 2025) exists for 38 of the 156. It agrees with us in 20
  and with LCDB in 3.

**Transfer to unknown asteroids.** The matched control is the TEST asteroids absent from all six
catalogues below. Tier A is correct for **185/205 = 90 %** of them.

**Calibration.** Predicted against observed probability on TEST:

| Predicted | 0.16 | 0.39 | 0.60 | 0.78 | 0.95 |
|---|---|---|---|---|---|
| Observed | 0.14 | 0.41 | 0.69 | 0.80 | 0.89 |

The top bin is somewhat overconfident.

## Spin sense

The sense picked by the PAB fit agrees with the hemisphere of published poles. Poles within 20 deg of
the ecliptic and ambiguous pole pairs are excluded.

| Reference | Agreement |
|---|---|
| Durech & Hanus 2023 | 3473/3535 = 98.2 % |
| DAMIT | 3802/3899 = 97.5 % |
| DAMIT, asteroids not in Durech & Hanus | 372/394 = 94.4 % |

Tier A has 3,677 retrograde and 2,561 prograde rotators. Of them, 3,390 have no LCDB period.

The PAB correction also explains why v2 disagreed with sidereal periods. Median |dP/P| against
Durech & Hanus:

| Period range | v2 | v3 |
|---|---|---|
| 2-5 h | 9e-5 | 6e-6 |
| 10-30 h | 3e-4 | 7e-5 |

## Comparison with other catalogues

Tier A, agreement within 3 %:

| Catalogue | Data | Agreement |
|---|---|---|
| Durech & Hanus 2023 | Gaia DR3 | 3548/3564 = 99.6 % |
| Cellino et al. 2024 | Gaia DR3 | 2855/2883 = 99.0 % |
| MacLennan et al. 2026 | Gaia DR3 | 2648/2676 = 99.0 % |
| Vavilov & Carry 2025 | TESS | 691/759 = 91.0 % |
| Erasmus et al. 2020 | ATLAS | 192/280 = 68.6 % |
| McNeill et al. 2023 | TESS | 475/863 = 55.0 % |

The three Gaia rows use the same data, so they show consistency, not accuracy.

On TEST asteroids where the catalogue and LCDB can both be checked:

| Catalogue | n | This work agrees with LCDB | Catalogue agrees with LCDB |
|---|---|---|---|
| Vavilov & Carry | 411 | 373 | 359 |
| Erasmus et al. | 146 | 111 | 116 |
| McNeill et al. | 379 | 352 | 231 |

## The 861 novel periods

942 tier-A asteroids have no period in LCDB V4.0 or in the six catalogues above. 81 of them have a
published rotation period in one of these sources:
- DAMIT;
- about 180 VizieR tables with asteroid rotation periods (5.0 M rows);
- the full text of the Minor Planet Bulletin, vols. 50-53.

VizieR matching uses identifier columns only. Units are taken from the table metadata, and non-rotation
"periods" are skipped, such as the astrometric wobble periods of Liberato et al. 2024.

**Agreement with those published periods.** At tier A, 47 of 61 VizieR values agree within 3 %. The
disagreements were inspected one by one in the wider prob >= 0.70 list (63 of 79 agree), and they are
understood:
- PTF partial-coverage periods (Chang et al. 2016) are half of ours;
- K2 periods differ by 3-6 %;
- 5 objects are fast rotators below 2 h (Erasmus et al. 2019), outside our search range;
- 2 are slow rotators.

**The list.** The remaining **861** periods are listed as novel: 667 at 2-10 h, 131 at 10-30 h and 63 at
30-100 h. Their expected precision is about 90 %, the matched-control value.

**Not checked:** SsODNet/ssoBFT, Behrend's Geneva page, ZTF period papers outside VizieR, and Pál et al.
2020. Until those are checked, read "novel" as "no period found in the sources listed".

## Period errors

The chi2-curvature error alone is too small. Against Durech & Hanus, which is a sidereal solution from
the same data, the median |dP/P| is 3.9e-5. Adding a systematic 5.5e-5 P in quadrature gives a median
|dP|/sigma of about 0.67 on both halves of a split.

This calibration measures agreement between two methods on the same data, not absolute accuracy, and it
excludes aliasing.

## Known limitations

- **Fast rotators.** Periods below 2 h are not searched. A fast rotator can therefore receive a wrong
  longer period, as for the 5 cases above.
- **P versus 2P.** The A1/A2 rule is a heuristic.
- **PAB coefficient for doubled periods.** When the period is doubled after the fit, the PAB coefficient
  should be 2. A variant that also tries coefficient 2 raised TEST tier-A precision only from 89.3 % to
  89.7 %. It is deferred to DR4.
- **Slow rotators and tumblers** are outside the model.
- **Injection-recovery** on real Gaia epochs has not been done yet.
- **Pilot candidates.** Of the 42 in the pilot note:
  - 35 agree with v3;
  - v3 doubles the period of 4 that were flagged "low";
  - for 3 that were flagged "high" (39932, 109412, 13686), v3 prefers a slow solution, and none of them
    is tier A, so these 3 are ambiguous.

## Review history

Two independent referees reviewed the work in two rounds: statistics in both rounds, planetary science in
both rounds.

**Round 1** led to:
- the slow-rotator flag;
- the matched control;
- the null test;
- tiers;
- the novelty re-check;
- the period-error term;
- the PAB correction.

**Round 2** led to:
- the error anatomy (the LCDB daily alias);
- U >= 3- precision;
- the spin-sense checks against D&H and DAMIT;
- the block null;
- tier A at 0.80;
- fixing the novelty units and the wobble-period confusion;
- the coefficient-2 test.

## Reproduce

1. `code/prep_gaia.py`
2. `PIPELINE_PAB=1 code/pipeline.py --workers 10` (about 20 min on 10 cores)
3. `code/calibrate2.py`
4. `compare_lit.py`, `make_new.py`, `tally_novelty.py`, `stats_final.py`, `make_figures.py`

Null tests:
- add `PIPELINE_NULL=1`, plus `PIPELINE_NULL_BLOCK=1.0` for the block version;
- use `PIPELINE_RESULTS=results_null[_block]` and `--only-file <list>`.

## Acknowledgements

ESA Gaia and DPAC; JPL Horizons and SBDB; LCDB (Warner, Harris & Pravec); DAMIT; VizieR (CDS). The
analysis was designed, coded and checked with the help of an AI assistant (Claude, Anthropic) under the
author's direction.
