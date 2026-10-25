# Rotation periods and spin senses of asteroids from Gaia DR3 sparse photometry

Status: **released v1.0.x**, DOI [10.5281/zenodo.23638281](https://doi.org/10.5281/zenodo.23638281) (all versions). Manuscript in preparation for A&A. This is version 3 of the method first piloted in
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

**Physical check: Yarkovsky segregation in families.** The spin senses reproduce the known Yarkovsky
segregation in families (Hanus et al. 2013, 2018): prograde rotators lie outside the parent's semimajor
axis and retrograde rotators inside it.
- 74.8 % of 2,345 family members are on the predicted side. Permuting the senses within each family gives
  52.4 ± 0.9 %, so the excess is z = 24.7.
- The fraction rises from 58 % near the family centre to 82 % for the most drifted members.
- The 912 members with no pole in Durech & Hanus 2023 extend the known samples, at 73.6 %.

**108 disputed LCDB periods** in the 2023 LCDB revision distributed by JPL SBDB.
- 39 are disputed by independent survey data (TESS, ATLAS).
- 69 rest on agreement among Gaia DR3 analyses only.
- Nine more periods flagged by the same test were already revised in that LCDB revision, each to the value
  found here.

**861 candidate new periods (tier A)** in any source we checked:
- expected precision about 90 %;
- noise from the null tests: 3.7-4.5 % of this list (95 % upper limit 5.9 %).

## Contents

| File | Rows | Content |
|---|---|---|
| `data/gaia_dr3_rotation_periods.csv` | 41,842 | every solved asteroid, with tier, probability, spin sense and flags |
| `data/novel_tierA.csv` | 861 | tier-A periods with no published period found in the sources checked |
| `data/lcdb_suspect_periods.csv` | 117 | LCDB V4.0 periods contradicted by this work plus independent support (with current SBDB status) |
| `validation/stats_final.json` | | every number quoted here, computed from the catalogue |
| `validation/report.json`, `lit_report.json` | | calibration report, literature comparison |
| `validation/REVIEW_BRIEF*.md` | | the briefs given to the independent referees (rounds 1 and 2) |
| `paper/` | | draft manuscript (`catalog.tex`, `catalog.pdf`) and figures |
| `code/` | | the full pipeline |

Columns:
- `period_h`, `period_err_h`: the period and its 1-sigma error (see *Period errors*).
- `tier`: `A` = confident. `B` = probable, but B is **not** reliable for asteroids without a known
  period: 18-20 % of signal-free asteroids reach it in the null tests.
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

Both nulls were run on all 32,229 solved asteroids without an LCDB period. The number that pass equals the
projected number of noise periods.

| Threshold | White pass | Block pass | Share of the 861 candidates (95 % upper limit) |
|---|---|---|---|
| 0.384 (TUNE 80 % precision) | 20.0 % | 18.1 % | — |
| 0.70 | 264 | 248 | — |
| 0.75 | 104 | 108 | — |
| **0.80 (tier A)** | **39** | **32** | **3.7-4.5 % (5.9 %)** |
| 0.85 | 12 | 8 | |

The estimate is conservative, because it treats every unknown asteroid as having no detectable rotation.

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

## Injection-recovery

Synthetic double-peaked lightcurves were injected into the real Gaia sampling of 4,000 asteroids without a
known period. Each lightcurve has:
- a period of 2-100 h, log-uniform;
- an amplitude of 0.1-0.6 mag, scaled per season by 0.5-1 to mimic aspect changes;
- a random spin sense, with the phase drifting with the PAB.

Two noise models bracket reality: the object's own residuals permuted (pessimistic, since they still contain
its scrambled real lightcurve) and Gaussian noise at the quoted errors (optimistic).

| | Permuted noise | Gaussian noise |
|---|---|---|
| tier-A precision | **96.5 %** (109/113) | **99.3 %** (567/571) |
| tier-A completeness | 2.7 % | 14 % |
| P/2 or 2P errors in tier A | 0 | 0 |
| spin sense correct (correct tier-A periods) | 96 % | 97 % |
| completeness, amplitude >= 0.45 mag | 7 % | 34 % |
| completeness, amplitude < 0.2 mag | 0 % | 0 % |

The fraction of real unknown asteroids that reach tier A (10.5 %) falls between the two completeness values.

Tier A is a high-precision, low-completeness selection:
- it recovers mostly high-amplitude rotators with many transits;
- it misses almost all low-amplitude ones;
- its precision on injections (96-99 %) is above its precision against LCDB (89 %). This agrees with the
  error anatomy below: part of the LCDB disagreement is error in LCDB.

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

## The Yarkovsky effect in families

Families come from AstDyS (`all_tro.members`, proper elements `all.syn`, June 2024). A family's centre
is the proper semimajor axis of its namesake. A member is counted as Yarkovsky-consistent if it is
prograde and lies outside the centre, or retrograde and lies inside it. Without a Yarkovsky effect,
50 % of members would be consistent.

| Sample | Consistent | p (binomial) |
|---|---|---|
| All tier-A family members | **1753/2345 = 74.8 %** | 9e-133 |
| Centre = median of all members instead | 1671/2345 = 71.3 % | 3e-97 |
| Members without a pole in Durech & Hanus 2023 | 671/912 = 73.6 % | 7e-48 |

| Family | Consistent | Members |
|---|---|---|
| (221) Eos | 86 % | 578 |
| (24) Themis | 81 % | 184 |
| (15) Eunomia | 79 % | 294 |
| (158) Koronis | 78 % | 184 |
| (10) Hygiea | 70 % | 97 |
| (4) Vesta | 67 % | 150 |

Two families have a fraction below 50 %: (93) Minerva and (375) Ursula. Their namesakes are probably
not at the V-shape centre.

See `paper/fig4_yarkovsky.png`.

This segregation is already known from modelled poles (Hanus et al. 2013, 2018; Kryszczynska 2013). Here it
serves as a check: random sense errors can only dilute it, so 74.8 % means that at least 75 % of the senses
are correct, a bound that does not rely on any pole catalogue.

| Robustness check | Result |
|---|---|
| Senses permuted within families (correct null) | 52.4 ± 0.9 % expected; observed 74.8 % (z = 24.7) |
| Odds ratio | 9.1 |
| Members near the centre | 58 % |
| Members far from the centre (\|a - a_c\| D > 2x family median) | 82 % |

Tier A favours high-amplitude rotators, so these fractions describe that subset, not whole families.

## Disputed LCDB periods

`data/lcdb_suspect_periods.csv` lists 117 tier-A asteroids whose LCDB V4.0 period disagrees with ours. In
each case either:
- an independent survey supports our period and none supports LCDB (43 cases: TESS from Vavilov & Carry
  or McNeill et al., or ATLAS from Erasmus et al.); or
- at least two other Gaia DR3 analyses support it (74 cases).

Of these, 32 are exact daily aliases and 14 are factor-2 differences.

Status in today's JPL SBDB (LCDB revision 2023):
- 9 have already been corrected to our value;
- **108 remain and are disputed**: 39 by independent survey data, 69 only by agreement of Gaia DR3
  analyses. LCDB quality of the 108: U = 2: 83, 2+: 9, 2-: 5, 3-: 3, 3: 8.

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
- **Completeness is low and depends on amplitude** (injection-recovery above). The catalogue is not
  suited to population statistics without a selection-function correction.
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

## Reproduce, and the Gaia DR4 run

To rerun the whole pipeline, from bulk files to a validated catalogue:

```bash
RELEASE_PREFIX=Gaia/gdr3/Solar_system/sso_observation/ WORKERS=10 code/run_release.sh
```

The script runs these steps:
1. fetch the bulk files;
2. build the transits;
3. run the PAB period search;
4. run the white and block null tests;
5. choose the tier-A threshold with `choose_threshold.py`. The rule is fixed in advance: noise at most
   5 % of the uncatalogued tier A, on a 0.05 grid;
6. calibrate on TUNE and build the catalogue;
7. compare with the literature and select new candidates;
8. compute the statistics and draw the figures.

A dry run on DR3 that reused the transit file took 21 min on 12 cores. It reproduced the catalogue exactly:
41,842 of 41,842 rows have the same period and tier, and the threshold came out at 0.80.

For DR4, only `RELEASE_PREFIX` should need to change. Check the DR4 file layout and column names first.

`code/run_release.sh` does not run the novelty searches beyond the six catalogues. Run them separately:
`novelty_vizier.py`, `novelty_catalogs.py`, `mpb_check.py`, then `tally_novelty.py`.

## Input data not included here

The scripts read these inputs from `data/`:

| Input | Source |
|---|---|
| Gaia DR3 `sso_observation` bulk files (4.4 GB) | `code/fetch_bulk.py` |
| Osculating elements `ELEMENTS.NUMBR.gz` | JPL SSD |
| Planet vectors | JPL Horizons, fetched by `nbody.py` |
| LCDB V4.0 summary table `lc_summary.csv` | PDS Small Bodies Node |
| Durech & Hanus 2023: periods and poles | VizieR J/A+A/675/A24 |
| Cellino et al. 2024 | VizieR J/A+A/687/A277 |
| MacLennan et al. 2026 | VizieR J/A+A/707/A131 |
| McNeill et al. 2023 | VizieR J/AJ/166/152 |
| Vavilov & Carry 2025 | VizieR J/A+A/693/A66 |
| Erasmus et al. 2020 | VizieR J/ApJS/247/13 |
| DAMIT asteroid and model tables | damit.cuni.cz/projects/damit/exports |
| AstDyS family membership and synthetic proper elements: `all_tro.members`, `all.syn` | AstDyS |

## Acknowledgements

ESA Gaia and DPAC; JPL Horizons and SBDB; LCDB (Warner, Harris & Pravec); DAMIT; VizieR (CDS). The
analysis was designed, coded and checked with the help of an AI assistant (Claude, Anthropic) under the
author's direction.
