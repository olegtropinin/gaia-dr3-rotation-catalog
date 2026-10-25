# Notes for the revision of ICARUS-D-26-00681

Prepared before referee reports arrive, from an external read of the submitted version (2026-10-25).

## 1. The "at least 75 % of senses correct" bound (Sect. on Yarkovsky segregation) — REWORD

The sentence "the observed 74.8 % therefore implies that at least 75 % of the senses are correct" holds only
if (a) the true consistent fraction is at least 50 % and (b) sense errors are independent of the side of
the family. Checked directly on 1,530 tier-A family members with published poles (Durech & Hanus 2023 and
DAMIT, |beta| >= 20 deg, unambiguous hemisphere):

| | |
|---|---|
| sense correct, members truly on the predicted side | 1143/1159 = 98.6 % |
| sense correct, members truly on the other side | 360/371 = 97.0 % |
| overall sense accuracy | 98.2 % |
| true consistent fraction (published poles) | 75.8 % |
| consistent fraction with our senses, same members | 75.4 % |

So errors are nearly independent of side (assumption b holds), and 74.8 % is essentially the true degree
of segregation in these families, not a bound on accuracy. Replace the sentence with: "For the 1,530
members with published poles, our senses are correct for 98.2 % and give a consistent fraction of 75.4 %,
against 75.8 % from the published poles; the 74.8 % therefore measures the segregation itself." Note that
most published poles come from the same Gaia data; quote the DAMIT-only subset separately.

## 2. Disputed LCDB periods

Already split 39 (independent survey) / 69 (Gaia-only) in text and abstract. In the revision, present the
two groups as separate tables or columns, and call only the first group "contradicted by independent data".

## 3. Accuracy against an imperfect truth set

Keep the three-way evidence together in one paragraph: 89.3 % against all LCDB, 95.4 % against U >= 3-,
96-99 % on injected lightcurves, and the TESS arbitration of disagreements (20 vs 3).

## 4. Candidate new periods are not a population sample

State in the conclusions that the 861 are a target list biased to high amplitude and P > 2 h, not a
population sample (already in limitations; repeat where the list is introduced).

Script for item 1: `code/yarkovsky_families.py` + the check in this note (to be added as a function).

## 5. Novelty of the 861 candidates: SsODNet, current JPL SBDB, Durech et al. 2022 (checked 2026-10-26)

The submitted text says "SsODNet, Behrend's Geneva page and ZTF period papers outside VizieR were not
searched". SsODNet itself (ssp.imcce.fr: ssoCard, dataCloud, ssoBFT) still answered 502 on 2026-10-26, so
the check used a third-party snapshot of the SsODNet best-estimate table (ssoBFT) merged with JPL SBDB
(AsteroidCatalog release data-2026-10-21b, checksum verified). Controls: four LCDB periods (665, 433, 4,
216) found and matching; all 4,806 Durech & Hanus 2023 periods without a JPL period found in the
SsODNet column with identical values. Bibliographic references of the SsODNet values are not in the
snapshot; they were recovered by matching values against Durech et al. (2022, Front. Astron. Space Sci.
9, 809771; ATLAS, 5,126 periods, not in VizieR), which the original search had missed.

| | count |
|---|---|
| candidates with a period somewhere | **71 of 861 (8.2 %)** |
| — SsODNet value identical to Durech et al. 2022 | 45 |
| — SsODNet, source not identified (ssoCard needed) | 17 |
| — JPL SBDB (LCDB rev. 2023-Oct; entries after LCDB V4.0 or with U = 1) | 9 |
| agree within 3 % | 49 (1 of them an LCDB U = 1 period) |
| ours = 2 x theirs | 7 |
| daily alias (lightcurve frequency 2/P differs by 1-2 c/d) | 6 |
| 2/3 ratio | 2 |
| other | 7 (3 of them against LCDB U = 1 or lower-limit periods) |
| **remaining candidate new periods** | **790** (617 at 2-10 h, 116 at 10-30 h, 57 at 30-100 h) |

New file `data/novel_tierA_v2.csv` (790); `data/novel_tierA_prior_periods.csv` (the 71, with source,
relation and status). `data/novel_tierA.csv` is left as submitted.

Changes for the revision:
- Text: "942 tier-A asteroids ... For 81 of them (8.6 %) ..." -> add SsODNet, current JPL SBDB and
  Durech et al. (2022): 152 of 942 (16.1 %) have a period somewhere; 790 remain.
- Noise: 32-39 noise periods are now 4.1-4.9 % of 790 (95 % upper limits 43 and 51 = 5.4 % and 6.5 %).
  The point estimates still meet the 5 % rule fixed in advance; the upper limits do not. Say so.
- The novelty definition is "no LCDB V4.0 period with U >= 2-". Five candidates have an LCDB period with U = 1 or
  only a lower limit; say explicitly that such periods were not counted as known, and list them.
- Disagreements with Durech et al. 2022 are mostly theirs halving: over all tier A, 1,176 overlap,
  1,088 agree (92.5 %; TEST half 551/591 = 93.2 %), 72 are ours = 2 x theirs, and where LCDB also has a
  period for those 72, LCDB agrees with ours in 31 of 36. Where ours and LCDB disagree (62), Durech et
  al. 2022 sides with ours 52 times and with LCDB 6 times. This is an independent-survey check (ATLAS)
  to add next to the TESS arbitration in item 3.
- Spin sense against an ATLAS-only source, Durech et al. (2020, A&A 643, A59; |beta| >= 20 deg, both
  poles in one hemisphere): 374/388 = 96.4 %; for asteroids not in Durech & Hanus 2023 130/137 = 94.9 %;
  TEST half 209/217 = 96.3 %. Useful for item 1 (it does not depend on Gaia photometry).
- Bib entries to add: Berthier et al. 2023 (A&A 671, A151, SsODNet); Durech et al. 2020 (A&A 643, A59);
  Durech et al. 2022 (Front. Astron. Space Sci. 9, 809771).
- Still not searched: SsODNet bibrefs for the 17 unidentified values; Behrend's page (unreachable
  2026-10-26); ZTF papers outside VizieR. Re-run `ssodnet_check.py` when ssp.imcce.fr is back.

RNAAS AAS82759 (35 candidates): 11857 (1988 RK9) has 19.7181 h in Durech et al. 2022, ours 19.710 h.
It is published, so 34 remain new. NEA list (20): 162882 has 8.7 h in SsODNet (source unknown), ours
17.76 h (2x); 19 remain.
