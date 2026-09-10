#!/usr/bin/env python3
"""The description-length curve of the two shipped cohorts swept far past the
configured range, so that a selection at the top of the shipped sweep can be
read against where the curve goes next.

Reproduces the run's own chain (gated layers, per-layer distances, kernels,
fusion, one spectral cut per k) with the shipped configuration, and records
the bits saved at every k from 1 to --k-max. Nothing else of the run is
repeated. Writes benchmarks/results/mdl_sweep_extended.json.
"""
import argparse, hashlib, json, pathlib
import pandas as pd
from amr_archetypes.config import load_config
from amr_archetypes.io import load_dataset
from amr_archetypes.fusion import snf_kernel, snf_fuse, default_K
from amr_archetypes.core import spectral_from_similarity, mdl_archetype, _layer_distance, _load_gated_layers

ROOT = pathlib.Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--k-max", type=int, default=25)
ap.add_argument("out", nargs="?", default=str(ROOT / "benchmarks" / "results" / "mdl_sweep_extended.json"))
a = ap.parse_args()
res = {"k_max": a.k_max, "cohorts": {}}
for name in ("klebsiella", "ssuis"):
    cfg_path = ROOT / "examples" / name / "config.yaml"
    cfg = load_config(cfg_path)
    ds = load_dataset(cfg)
    names, frames, ids, _ = _load_gated_layers(cfg, ds)
    X = pd.concat(frames, axis=1).values.astype(int)
    mats = [f.values.astype(int) for f in frames]
    K = cfg.snf.K if cfg.snf.K is not None else default_K(len(ids))
    Ws = [snf_kernel(_layer_distance(cfg, r, M), mu=cfg.snf.mu, K=K) for r, M in zip(names, mats)]
    W = snf_fuse(Ws, K=K, T=cfg.snf.T, alpha=cfg.snf.alpha, tie_policy=cfg.snf.tie_policy, update=cfg.snf.update)
    sweep = []
    for k in range(1, a.k_max + 1):
        info = mdl_archetype(X, spectral_from_similarity(W, k), complexity="rissanen")
        sweep.append({"k": k, "gain": float(info["gain"])})
    best = max(sweep, key=lambda r: r["gain"])
    res["cohorts"][name] = {"config_sha256": hashlib.sha256(cfg_path.read_bytes()).hexdigest(),
                            "n_isolates": int(X.shape[0]), "n_features": int(X.shape[1]),
                            "shipped_k_range_max": int(max(cfg.trait_cluster.k_range)),
                            "sweep": sweep, "best_k": int(best["k"]), "best_gain": float(best["gain"])}
    print(name, [(r["k"], round(r["gain"])) for r in sweep])
pathlib.Path(a.out).write_text(json.dumps(res, indent=1))
print("wrote", a.out)
