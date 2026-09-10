#!/usr/bin/env python3
"""The same-lineage concordance z and the lineage-attributable share lambda on
the shipped S. suis cohort as it is subsampled.

Two arms. In the first the shipped partition and the lineage labels are held
fixed and nothing is re-clustered: at each cohort size the two statistics are
computed on the same random subsets, several draws each, so that the shape of
the two series across n is read on identical data. In the second the share is
the one the gate reads: the partition is rebuilt inside every cross-validation
fold on the subsample, with the shipped configuration, k held at the value the
whole cohort selected and the held-out isolates placed against the training
groups by the run's own assignment rule. The point of the series is that z
grows with n at fixed structure while neither share does.

    python benchmarks/subsample_series.py [out.json] [--draws 5] [--refit-draws 3]
"""
import argparse, hashlib, json, pathlib
import numpy as np, pandas as pd
from amr_archetypes import core
from amr_archetypes.config import load_config
from amr_archetypes.core import spectral_from_similarity
from amr_archetypes.fusion import snf_kernel, snf_fuse
from amr_archetypes.lineage import lineage_concordance
from amr_archetypes.attribution import attribute_partition

ROOT = pathlib.Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("out", nargs="?", default=str(ROOT / "benchmarks" / "results" / "ssuis_subsample_series.json"))
ap.add_argument("--draws", type=int, default=5)
ap.add_argument("--refit-draws", type=int, default=3)
ap.add_argument("--refit-repeats", type=int, default=10)
a = ap.parse_args()
OUT = pathlib.Path(a.out)
ex = ROOT / "examples" / "ssuis"
cfg = load_config(ex / "config.yaml", check_files_exist=False)
assign = pd.read_csv(ex / "expected" / "assignment.tsv", sep="\t").set_index("isolate_id")
layer_names = list(cfg.trait_cluster.layers)
frames = {"ribo": pd.read_csv(ex / "data" / "ribo.csv").set_index("genome_id"),
          "cell": pd.read_csv(ex / "data" / "cell.csv").set_index("genome_id")}
layer_mats_all = [frames[r].reindex(assign.index).to_numpy(dtype=float) for r in layer_names]
X = np.concatenate(layer_mats_all, axis=1)
assert not np.isnan(X).any()
labels = assign["cluster"].to_numpy()
k = int(labels.max()) + 1
K = cfg.snf.K if cfg.snf.K is not None else core.default_K(len(labels))
sizes = [67, 135, 270, 473, 677]


def refit_factory(rows):
    """The run's own fold-internal refit, restricted to the subsample rows."""
    mats = [M[rows] for M in layer_mats_all]

    def fuse(Ws):
        return snf_fuse(Ws, K=K, T=cfg.snf.T, alpha=cfg.snf.alpha,
                        tie_policy=cfg.snf.tie_policy, update=cfg.snf.update)

    def refit(train, held_out, labels=None):
        if labels is None:
            Ws = [snf_kernel(core._layer_distance(cfg, r, M[train]), mu=cfg.snf.mu, K=K)
                  for r, M in zip(layer_names, mats)]
            labels_train = spectral_from_similarity(fuse(Ws), k)
        else:
            labels_train = np.asarray(labels)[train]
        return core._assign_to_training_clusters(cfg, layer_names, mats, train, held_out,
                                                 labels_train, K)
    return refit


res = {"source": {f: hashlib.sha256((ex / p).read_bytes()).hexdigest()
                  for f, p in (("assignment", "expected/assignment.tsv"), ("ribo", "data/ribo.csv"),
                               ("cell", "data/cell.csv"), ("config", "config.yaml"))},
       "design": {"sizes": sizes, "draws_per_size": a.draws, "seed": 20260909,
                  "fixed_partition": {"folds": 5, "repeats": 20, "n_boot": 0, "n_perm": 60, "refit": False},
                  "refit": {"folds": 5, "repeats": a.refit_repeats, "n_boot": 0, "n_perm": 60,
                            "draws_per_size": a.refit_draws, "k": k, "K": K},
                  "concordance": {"n_perm": 500}},
       "lambda_gate": float(cfg.attribution.lambda_gate),
       "series": {}}
for col in ("baps_cluster", "mlst"):
    lin_all = assign[col]
    idx_all = np.flatnonzero(lin_all.notna().to_numpy())
    rows_out = []
    for n in sizes:
        n_eff = min(n, len(idx_all))
        if any(r["n"] == n_eff for r in rows_out):
            continue
        lam, z, r2l, r2p, lam_refit, r2p_refit = [], [], [], [], [], []
        for d in range(a.draws):
            rng = np.random.default_rng([20260909, n, d])
            idx = np.sort(rng.choice(idx_all, size=n_eff, replace=False))
            lab, lin, Xi = labels[idx], lin_all.to_numpy()[idx], X[idx]
            c = lineage_concordance(lab, lin, n_perm=500, rng=np.random.default_rng([1, n, d]))
            att = attribute_partition(Xi, lab, lin, folds=5, repeats=20, n_boot=0, n_perm=60,
                                      seed=np.random.default_rng([2, n, d]))
            lam.append(att.lam); z.append(c["z"]); r2l.append(att.r2_lineage); r2p.append(att.r2_partition)
            if d < a.refit_draws:
                att_r = attribute_partition(Xi, lab, lin, folds=5, repeats=a.refit_repeats, n_boot=0,
                                            n_perm=60, refit=refit_factory(idx),
                                            seed=np.random.default_rng([3, n, d]))
                lam_refit.append(att_r.lam); r2p_refit.append(att_r.r2_partition)
        row = {"n": n_eff, "lambda_mean": float(np.mean(lam)), "lambda_sd": float(np.std(lam, ddof=1)),
               "z_mean": float(np.mean(z)), "z_sd": float(np.std(z, ddof=1)),
               "r2_lineage_mean": float(np.mean(r2l)), "r2_partition_mean": float(np.mean(r2p)),
               "lambda_draws": [float(v) for v in lam], "z_draws": [float(v) for v in z],
               "lambda_refit_mean": float(np.mean(lam_refit)) if lam_refit else None,
               "lambda_refit_sd": float(np.std(lam_refit, ddof=1)) if len(lam_refit) > 1 else None,
               "lambda_refit_draws": [float(v) for v in lam_refit],
               "r2_partition_refit_mean": float(np.mean(r2p_refit)) if r2p_refit else None}
        rows_out.append(row)
        print(col, n_eff, "lam %.3f z %.1f lam_refit %s" % (row["lambda_mean"], row["z_mean"],
              "%.3f" % row["lambda_refit_mean"] if row["lambda_refit_mean"] is not None else "-"), flush=True)
    res["series"][col] = {"n_labelled": int(len(idx_all)), "rows": rows_out}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(res, indent=1))
print("wrote", OUT)
