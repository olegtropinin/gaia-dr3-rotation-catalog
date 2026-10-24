"""Compare catalog.csv with published period catalogues: agreement by catalogue and period band.

Only confident results are compared. 'agree' = within 3%; 'half'/'double' = factor 2 aliases.
Durech & Hanus 2023, Cellino 2024 and MacLennan 2026 use the same Gaia DR3 data (method check);
McNeill 2023 and Vavilov & Carry 2025 (TESS) and Erasmus 2020 (ATLAS) are independent data.
"""
import csv, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data")


def num(x):
    x = (x or "").strip().strip("()")
    return int(x) if x.isdigit() else None


def load(path, ncol, pcol):
    out = {}
    for r in csv.DictReader(open(path)):
        n = num(r.get(ncol))
        try:
            p = abs(float(r[pcol]))
        except (TypeError, ValueError):
            continue
        if n and p > 0:
            out.setdefault(n, p)
    return out


def main():
    cats = {
        "Durech & Hanus 2023 (Gaia DR3)": {int(l.split("\t")[0]): float(l.split("\t")[1]) for l in open(os.path.join(D, "durech2023.tsv"))},
        "Cellino 2024 (Gaia DR3)": load(os.path.join(D, "lit", "cellino2024.csv"), "Name", "Prot"),
        "MacLennan 2026 (Gaia DR3)": load(os.path.join(D, "lit", "maclennan2026.csv"), "Number", "Prot"),
        "McNeill 2023 (TESS)": load(os.path.join(D, "lit", "mcneill2023_tess.csv"), "Object", "Prot"),
        "Vavilov & Carry 2025 (TESS)": load(os.path.join(D, "lit", "vavilov2025_tess.csv"), "MPC", "Per"),
        "Erasmus 2020 (ATLAS)": load(os.path.join(D, "lit", "erasmus2020_atlas.csv"), "Planet", "Prot"),
    }
    rows = [r for r in csv.DictReader(open(os.path.join(HERE, "catalog.csv"))) if r["confident"] == "1"]
    report = {}
    for name, ref in cats.items():
        stat = {"n": 0, "agree": 0, "half": 0, "double": 0, "other": 0, "bands": {}}
        for r in rows:
            n = int(r["number"])
            if n not in ref:
                continue
            p, q = float(r["period_h"]), ref[n]
            rel = "agree" if abs(p - q) / q < 0.03 else "half" if abs(2 * p - q) / q < 0.03 else "double" if abs(p - 2 * q) / (2 * q) < 0.03 else "other"
            stat["n"] += 1; stat[rel] += 1
            band = "2-10h" if p < 10 else "10-30h" if p < 30 else "30-100h" if p < 100 else "100-1000h"
            b = stat["bands"].setdefault(band, [0, 0]); b[0] += 1; b[1] += rel == "agree"
        stat["agree_rate"] = round(stat["agree"] / stat["n"], 3) if stat["n"] else None
        report[name] = stat
    known_any = set().union(*[set(c) for c in cats.values()])
    lcdb_known = {int(r["number"]) for r in csv.DictReader(open(os.path.join(HERE, "catalog.csv"))) if r["lcdb_period_h"]}
    new = [r for r in rows if int(r["number"]) not in known_any and int(r["number"]) not in lcdb_known]
    report["confident_total"] = len(rows)
    report["confident_not_in_any_catalogue"] = len(new)
    json.dump(report, open(os.path.join(HERE, "lit_report.json"), "w"), indent=1)
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
