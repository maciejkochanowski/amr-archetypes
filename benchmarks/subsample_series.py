#!/usr/bin/env python3
"""The same-lineage concordance z and the lineage-attributable share lambda on
the shipped S. suis partition, held fixed, as the cohort is subsampled.

The partition and the lineage labels are those of the shipped record; nothing
is re-clustered. At each cohort size the two statistics are computed on the
same random subsets, several draws each, so that the shape of the two series
across n is read on identical data. The point of the series is that z grows
with n at fixed structure while lambda does not.
"""
import json, sys, hashlib, pathlib
import numpy as np, pandas as pd
from amr_archetypes.lineage import lineage_concordance
from amr_clonalshare.attribution import attribute_partition

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "benchmarks" / "results" / "ssuis_subsample_series.json"
ex = ROOT / "examples" / "ssuis"
assign = pd.read_csv(ex / "expected" / "assignment.tsv", sep="\t").set_index("isolate_id")
ribo = pd.read_csv(ex / "data" / "ribo.csv").set_index("genome_id")
cell = pd.read_csv(ex / "data" / "cell.csv").set_index("genome_id")
X = pd.concat([ribo, cell], axis=1).reindex(assign.index)
assert not X.isna().any().any()
labels = assign["cluster"].to_numpy()
sizes = [67, 135, 270, 473, 677]
draws = 5
res = {"source": {"assignment": hashlib.sha256((ex / "expected" / "assignment.tsv").read_bytes()).hexdigest(),
                  "ribo": hashlib.sha256((ex / "data" / "ribo.csv").read_bytes()).hexdigest(),
                  "cell": hashlib.sha256((ex / "data" / "cell.csv").read_bytes()).hexdigest()},
       "design": {"sizes": sizes, "draws_per_size": draws, "seed": 20260909,
                  "attribution": {"folds": 5, "repeats": 20, "n_boot": 0, "n_perm": 60, "refit": False},
                  "concordance": {"n_perm": 500}},
       "series": {}}
for col in ("baps_cluster", "mlst"):
    lin_all = assign[col]
    keep = lin_all.notna().to_numpy()
    idx_all = np.flatnonzero(keep)
    rows = []
    for n in sizes:
        n_eff = min(n, len(idx_all))
        if any(r["n"] == n_eff for r in rows):
            continue          # the labelled subset is smaller than this size
        lam, z, r2l, r2p = [], [], [], []
        for d in range(draws):
            rng = np.random.default_rng([20260909, n, d])
            idx = np.sort(rng.choice(idx_all, size=n_eff, replace=False))
            lab, lin, Xi = labels[idx], lin_all.to_numpy()[idx], X.to_numpy(dtype=float)[idx]
            c = lineage_concordance(lab, lin, n_perm=500, rng=np.random.default_rng([1, n, d]))
            a = attribute_partition(Xi, lab, lin, folds=5, repeats=20, n_boot=0, n_perm=60,
                                    seed=np.random.default_rng([2, n, d]))
            lam.append(a.lam); z.append(c["z"]); r2l.append(a.r2_lineage); r2p.append(a.r2_partition)
        rows.append({"n": n_eff, "lambda_mean": float(np.mean(lam)), "lambda_sd": float(np.std(lam, ddof=1)),
                     "z_mean": float(np.mean(z)), "z_sd": float(np.std(z, ddof=1)),
                     "r2_lineage_mean": float(np.mean(r2l)), "r2_partition_mean": float(np.mean(r2p)),
                     "lambda_draws": [float(v) for v in lam], "z_draws": [float(v) for v in z]})
        print(col, rows[-1]["n"], round(rows[-1]["lambda_mean"], 3), round(rows[-1]["z_mean"], 1), flush=True)
    res["series"][col] = {"n_labelled": int(len(idx_all)), "rows": rows}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(res, indent=1))
print("wrote", OUT)
