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

## 5. Novelty of the 861 candidates: SsODNet, current JPL SBDB, Durech et al. 2022 (checked 2026-10-26, revised after a statistics review)

The submitted text says "SsODNet, Behrend's Geneva page and ZTF period papers outside VizieR were not
searched". SsODNet itself (ssp.imcce.fr: ssoCard, dataCloud, ssoBFT) still answered 502 on 2026-10-26, so
the check used a third-party snapshot that merges JPL SBDB with the SsODNet best-estimate table ssoBFT
(AsteroidCatalog release data-2026-10-21b, checksum verified; per its changelog the ssoBFT file is that of
2026-09-22). The snapshot keeps JPL's period first and only the best-ranked SsODNet solution; it carries
no references. Controls: all 4,806 Durech & Hanus 2023 periods that JPL lacks are found with identical
values (their numbers span most of the candidates' range); of 1,325 Durech et al. 2022 periods that JPL
lacks, 1,220 are found, so the snapshot misses about 8 % of a catalogue SsODNet holds.

| source of the prior period | n | match | ours = 2x | daily alias | 2/3 | differ |
|---|---|---|---|---|---|---|
| SsODNet value identical to Durech et al. 2022 (ATLAS; not in VizieR) | 45 | 35 | 6 | 4 | 0 | 0 |
| SsODNet, source not identified (ssoCard needed) | 17 | 10 | 0 | 2 | 2 | 3 |
| JPL SBDB (LCDB rev. 2023-Oct) | 9 | 4 | 1 | 0 | 0 | 4 |
| **total** | **71 of 861 (8.2 %)** | 49 | 7 | 6 | 2 | 7 |

Of the 22 non-matches, 18 are against U >= 2 or survey periods and 4 against LCDB periods with U = 1 or
only a lower limit. **790 candidates remain** (617 at 2-10 h, 116 at 10-30 h, 57 at 30-100 h).
New files: `data/novel_tierA_v2.csv` (790); `data/novel_tierA_prior_periods.csv` (the 71, with source,
relation, status and a flag for the 9 whose SsODNet value is hidden behind a JPL value).
`data/novel_tierA.csv` is left as submitted.

Changes for the revision:
- Text: "942 tier-A asteroids ... For 81 of them (8.6 %) ..." -> 152 of 942 (16.1 %) have a period in
  the sources now searched; 790 remain. Call them "no period found in the sources searched", and give the
  measured miss rate of the SsODNet snapshot (about 8 %).
- Definition: five candidates have an LCDB period with U = 1 or only a lower limit (11874, 25719, 27270,
  61303, 133862). The submitted definition did not count these as known. Removing them is a change of
  definition (to be conservative); say so explicitly.
- Reliability of the 790, two numbers, both to be quoted:
  - noise from the null tests: 32-39 of 861; removal does not depend on whether the period matched, so
    proportionally 29-36 of 790, the same 3.7-4.5 %. (A random period pair matches within 3 % in about 3 %
    of cases and falls in some non-"differ" class in about 21 %, so noise periods are not protected from
    matching.)
  - agreement where a prior period exists: 49/71 = 69 % (95 % interval 58-79 %); 48/60 = 80 % (68-88 %)
    after removing U = 1 periods and the 6 Durech et al. 2022 halvings; rest of tier A 93.9 %. Like for
    like against Durech et al. 2022: candidates 35/46 = 76 %, other tier A 1,053/1,130 = 93.2 %. Error
    among the candidates is dominated by aliases and harmonics of real signals, not noise. Replace the
    "expected precision of about 90 %" with this range, or state both and explain the difference
    (candidates have fewer transits and lower calibrated probability).
- Independent-survey check to add next to the TESS arbitration (item 3): tier A vs Durech et al. 2022
  (ATLAS): 1,088/1,176 = 92.5 % (TEST 551/591 = 93.2 %). The main disagreement, ours = 2 x theirs (72), is
  not decided: for the 36 with an LCDB period LCDB sides with ours 31 times, which favours ours on average
  but is not proof for any single object.
- Spin sense against an ATLAS-only source, Durech et al. (2020, A&A 643, A59; |beta| >= 20 deg, both
  poles in one hemisphere): 374/388 = 96.4 %; not in Durech & Hanus 2023 130/137 = 94.9 %; TEST half
  209/217 = 96.3 %. Useful for item 1.
- Do not quote the 571/590 agreement with SsODNet-only periods as a check: their sources are unknown and
  may share the Gaia data.
- Bib entries to add: Berthier et al. 2023 (A&A 671, A151, SsODNet); Durech et al. 2020 (A&A 643, A59);
  Durech et al. 2022 (Front. Astron. Space Sci. 9, 809771).
- Still open: SsODNet references for the 17 unidentified values and for the 9 masked ones; Behrend's page
  (unreachable 2026-10-26); ZTF papers outside VizieR; anything after 2026-09-22. Re-run `ssodnet_check.py`
  when ssp.imcce.fr is back.

RNAAS AAS82759 (35 candidates): 11857 (1988 RK9) has 19.7181 h in Durech et al. 2022, ours 19.710 h.
It is published, so 34 remain new. NEA list (20): 162882 has 8.7 h in SsODNet (source unknown), ours
17.76 h (2x); 19 remain.
