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
