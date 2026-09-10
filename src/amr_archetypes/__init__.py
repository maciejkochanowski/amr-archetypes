"""amr-archetypes — recurring resistance profiles in a bacterial collection, and
the diagnostics that decide whether they are real.

A collection of genomes typed for acquired resistance determinants, virulence
loci and capsule or antigen type can be clustered on those layers, and the
groups that come out look like archetypes: combinations of resistance and
virulence that recur. Most of them are not. The largest group is often the
isolates that carry nothing; one layer can dominate the fusion so that the
groups are that layer under another name; tied affinities can make the answer
depend on the order of the rows; and blocks of co-inherited loci can make a
single element count as many independent features. The most common artefact
of all is population structure: closely related genomes share genes, so a
partition of any genotype layer tends to be the lineages relabelled.

The package runs the pipeline and every one of those checks, and closes the run
where a check fails.

**The pipeline.** Per-layer distances, similarity-network fusion, consensus
clustering, and a choice of the number of groups that may return one
(:mod:`~amr_archetypes.core`, :mod:`~amr_archetypes.fusion`), benchmarked
against the rules any such pipeline has to beat
(:mod:`~amr_archetypes.baselines`).

**The diagnostics.** Fusion collapsing onto a single layer
(:mod:`~amr_archetypes.influence`); the trait-absent stratum and tied
affinities (:mod:`~amr_archetypes.stats`, :mod:`~amr_archetypes.fusion`);
co-inherited loci inflating the feature count
and clonal population structure (:mod:`~amr_archetypes.lineage`), the latter
measured as the lineage-attributable share of the partition
(:mod:`~amr_archetypes.attribution`); and whether the groups are discrete rather than a continuum, by
multi-split feature splitting with an exchangeable merging rule
(:mod:`~amr_archetypes.inference`), with a phylogenetic convergence test
for small cohorts, a Monte Carlo null under a fitted two-state Markov chain
with the exact uniform-edge tail beside it (:mod:`~amr_archetypes.archephy`).

**The verdict.** A five-level claim ladder exposes every applicable gate, and a
partition is never promoted to a biological archetype past a gate that fired.
The share each clustering trait carries on its own is reported beside the
partition's.
"""
from __future__ import annotations

from importlib import import_module

__version__ = "1.0.0"

__all__ = [
    "__version__", "Config", "ConfigError", "load_config", "run", "validate",
    "inference", "influence", "lineage", "baselines", "archephy", "tva",
    "fusion", "small_n", "attribution", "stats", "phenotype",
]

_PUBLIC_MODULES = {"inference", "influence", "lineage", "baselines", "archephy",
                   "tva", "fusion", "small_n", "attribution", "stats",
                   "phenotype"}
_CONFIG_EXPORTS = {"Config", "ConfigError", "load_config"}
_CORE_EXPORTS = {"run", "validate"}


def __getattr__(name: str):
    """Load the numerical stack only when a public object is first requested.

    Python imports the package before executing ``python -m
    amr_archetypes.cli``. Eager imports here therefore initialized BLAS
    before the CLI could apply ``--threads``. PEP 562 lazy attributes preserve
    the public API while deferring those imports.
    """
    if name in _PUBLIC_MODULES:
        value = import_module(f".{name}", __name__)
    elif name in _CONFIG_EXPORTS:
        value = getattr(import_module(".config", __name__), name)
    elif name in _CORE_EXPORTS:
        value = getattr(import_module(".core", __name__), name)
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
