# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/);
versioning: [SemVer](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-10

First public release. Everything below is what the package contains, not a
record of how it was built.

### Added

**Partition diagnostics.** Multi-view consensus clustering over binary trait
layers with similarity network fusion, order-invariant neighbour selection and
a description-length criterion whose sweep includes `k = 1`, so a cohort with
no structure can be reported as having none. The absence-stratum check
compares each layer's all-zero indicator with the whole partition and, because
that index is diluted at large `k`, also compares the largest group against
the rest with the indicator "carries no retained feature of any layer"; the
larger agreement carries the gate. An ordered sequence of artefact,
layer, held-out-feature and adaptively dimensioned continuum diagnostics runs
before any partition is released, and each is tied to a status code rather than
to prose.

**The number of groups is a finding only inside the sweep.** The
description-length sweep runs from one to ten groups on every shipped
configuration; a best value at the top of the range is flagged and closes the
`k_selection` gate, because a curve that has not turned identifies nothing.
`benchmarks/mdl_sweep_extended.py` sweeps the two shipped cohorts to
twenty-five groups so that a flagged selection can be read against where the
curve goes next.

**The lineage gate is a magnitude.** Same-lineage pair concordance against a
permutation null says whether the partition carries any lineage signal, and on
a real cohort it always does, more so the larger the cohort. What carries the
gate is the lineage-attributable share of the partition, estimated out of
sample by `amr_archetypes.attribution.attribute_partition` with the partition
rebuilt inside every fold, split against the lineage label by commonality
analysis and by the two-player Shapley value. Where fewer than 90 % of
isolates sit in lineages of at least two members the share is reported
without a verdict and a `lineage_support` gate closes instead, because a
singleton lineage cannot be predicted out of sample. The threshold is
`attribution.lambda_gate`, 0.5 by default, decided by the point estimate; where
an interval is computed and crosses it the reading is marked unresolved. The share
each clustering trait carries on its own is reported beside it.

**Baselines under one criterion.** Every candidate partition (concatenation,
each layer alone, a Bernoulli mixture) is put through the same feature-split
held-out test as the reported partition, and against each external label the
record holds the paired bootstrap difference in adjusted Rand index between
the candidate and the reported partition with its interval
(`baselines.candidates[*].held_out`, `external_agreement_vs_reported`,
`mdl_gain_scope`).

**Input check.** Every run starts by loading the layers, applying the stated
policy to cells that hold no value (refuse, drop the isolate, or drop the
feature; never fill in a 0), refusing any value other than 0 and 1, and writing
`input_qc.json` with a plain-language `input_qc.md`: per trait the count of the
rarer outcome, and per lineage the group sizes, the share of isolates in
lineages of at least two, and whether the lineage share will be estimable at
that typing resolution. `--check-input` runs this step alone. A refused input
leaves with exit code 2 and a sentence naming the position, not a traceback.

**Run report, written and drawn.** `report.md` and `report.html` beside
`cluster_result.json`, both rendered from one structure in a fixed order of
nine sections. The first page is the measurement summary: the question asked,
the number of groups, whether they recur on held-out traits and are discrete,
the share of the grouping that lineage explains against its gate, the claim
level, the gates that fired, what was not evaluated on this run and why, and
an interpretation generated from the record by fixed rules. The pages after it
defend the first: the admissibility conditions with observed value, threshold
and verdict, the profile groups and their checks, and the gate ledger; beside the
held-out p-value the page states how closely the labels re-derived inside each
split resemble the reported grouping, and says, below a median adjusted Rand
index of 0.5, that the evidence attests structure in the layers and not this
grouping in particular. Every value on either page is read from the record and
none is recomputed; both carry the SHA-256 of the record; the drawn page is one
file with no script and nothing to fetch.

**Contract and reproducibility.** A strict YAML configuration that refuses an
unknown key rather than silently disabling the analysis it names; eight output
files (the record under output schema 1.0, its summary, the profile and
assignment tables, the input check in JSON and in prose, and the report in
Markdown and HTML); exit codes 0, 1, 2 and 3 separating success, a failed
planted-truth validation, a configuration error and an informative refusal; a
master seed spawning every stochastic stage; and a `provenance` block in every
record naming the software and library versions and the SHA-256 of each input
file.

**Property tests.** `tests/test_properties.py` states the identities the
arithmetic must satisfy for every input and lets Hypothesis search for a
counterexample: the merged p-value of exchangeable splits is a probability
that ignores their order and never exceeds the plain merge, and the exact
homoplasy tail agrees with brute-force enumeration.

**The subsampling series.** `benchmarks/subsample_series.py` holds the shipped
*S. suis* partition and its lineage labels fixed and subsamples the cohort,
computing the same-lineage concordance z and the lineage-attributable share
on identical draws at each size, under the population cluster and under the
sequence type; the series behind the README table is written to
`benchmarks/results/ssuis_subsample_series.json`.

**Experiment G with common random numbers.** `benchmarks/block_threshold_crn.py`
applies every blocking threshold to the same cohort with the same split draws,
so that a difference between two thresholds is a difference between two rules
on identical data, with paired contrasts read from the discordant pairs. The
design is registered in `benchmarks/prereg_block_threshold_crn.json` before
the run.

**Engineering gates.** `ruff` and `mypy` run in CI and both pass over the
package; the coverage gate is per module (`scripts/check_coverage_floors.py`);
the documentation builds strictly in CI and carries an API reference generated
from the docstrings; releases are published from GitHub releases through PyPI
Trusted Publishing with PEP 740 attestations and no stored token; actions are
pinned to commit digests; mutation testing is configured for the fusion and
inference modules and run by hand, as `CONTRIBUTING.md` describes.

**Supported stack.** Python 3.11 or later, NumPy 2.0, pandas 2.2, SciPy 1.13
and scikit-learn 1.5 or later, following the scientific-Python support window;
CI runs 3.11 to 3.13. Every reported number was produced inside these floors.

**Examples.** Two real cohorts, 1,500 *Klebsiella pneumoniae* genomes with
acquired resistance determinants and virulence loci as two layers, the
sequence type as the lineage and a measured susceptibility panel as the
external criterion, and 677 *Streptococcus suis* isolates with thirteen
antimicrobials in two layers and a hierBAPS population cluster for every
isolate; four synthetic controls, two planted, one null and one clonal; and a
holdout arm.

### Known limits

- Level 4 of the claim ladder attests that every applicable diagnostic
  passed; it is not causal, clinical or cross-cohort biological confirmation.
- Byte-identity of the spectral step across BLAS builds is not claimed; what
  is claimed and tested is invariance to row order, stability of the selected
  k, and reproducibility within one environment at a fixed seed.
- The examples are not a cross-species validation study, and no superiority
  over all multi-view methods is claimed.
