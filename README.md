# amr-archetypes

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)

**Release status:** public product version `1.0.0`.

**Are the resistance profiles in this collection a set of recurring types, or
the lineages relabelled?** Give it one or more wide binary matrices per isolate
(acquired AMR determinants, virulence loci, capsule type, plasmid replicons)
and a lineage label, and it fuses the layers into a similarity network,
clusters it, profiles the result, and then answers the questions that decide
whether the partition means anything. A dozen other tools do the first part.
The reason to use this one is the second:

- **Is the largest cluster just the isolates with no detected features?**
  Jaccard is undefined for two all-zero rows and the usual convention calls them
  identical. On real accessory-genome data that block is often the majority of
  the cohort. Reported as `empty_stratum_ari`, with a gate.
- **Would a different row order in the CSV give a different answer?** With
  binary data the *K*-nearest-neighbour graph is cut in the middle of a huge tie
  block unless neighbour selection is made order-invariant, which it is here,
  and `tie_inflation` tells you how close to degenerate the graph is.
- **Did the fusion actually fuse, or did one layer win?** Leave-one-layer-out
  influence, an effective number of contributing layers, and a `regime` label
  (`complementary` / `collapsed` / `redundant` / `unstructured` / `uninformative`),
  because `n_eff` alone gives the same answer to three concordant layers and to
  three noise layers.
- **Are these clusters just clones?** Same-lineage pair concordance against a
  permutation null says whether there is any lineage signal, and on a real
  cohort there always is. What carries the gate is how much: the
  lineage-attributable share of the partition, an out-of-sample variance
  decomposition from [`amr-clonalshare`](https://github.com/maciejkochanowski/amr-clonalshare),
  which this package depends on and grew out of.
- **Is the structure real, and is it *discrete*?** Two different questions,
  answered by two different tests, because a valid post-clustering p-value
  rejects on a smooth gradient just as readily as on genuine archetypes. The
  discreteness null is a *q*-factor latent trait with *q* chosen by BIC; pinned
  at one factor it calls any two-dimensional gradient discrete 100 % of the time.
  The default fits dimensions 1--3, conditionally extends to 4 when the
  provisional optimum is on the boundary, and returns a third, non-estimable
  state if the optimum remains on the final boundary.
- **Does the partition beat one column of the input?** If you can supply measured
  phenotype, that is the only criterion here that is not a function of what was
  clustered. On the shipped *Klebsiella* cohort the answer is no, and the CLI
  exits non-zero saying so.

If any of these trips, the CLI says so on stderr and exits non-zero.

## What the controls and real cohorts show

Two independently seeded planted controls provide positive examples that do
not end in refusal. In each, the pipeline recovers all three planted groups
(ARI 1.000), detects held-out structure, rejects the fitted two-factor
continuum (0/99 exceedances; corrected `p = 0.01`; exact tail-probability 95%
CI 0-0.0366), validates 60 defining features, finds no lineage confounding,
reaches claim level 4 (`archetype_candidate`), and exits 0.

On the shipped *Klebsiella* cohort a discrete signal is detected beyond the
BIC-selected three-factor continuum (`p = 0.01`); with the BIC sweep run to
four factors, `q = 3` is an interior optimum. This statistical result
does not establish biological archetypes: the two-group partition correlates
with the all-zero virulence stratum, is inferior to a one-dimensional
resistance score for measured susceptibility (mean balanced accuracy 0.790
versus 0.695; bootstrap difference +0.090, 95 % CI [+0.048, +0.125]), and
lineage explains 0.474 of it, just under the gate of 0.5. The CLI therefore
exits 3 while preserving the positive discreteness result. The *S. suis*
example detects a discrete signal beyond a three-factor continuum
(`p = 0.01`), lineage explains 0.411 of its five-group partition, and no gate
closes: it reaches level 4. These are independent biological interpretation
gates, not refusals by the continuum test.

## Install

From PyPI, or from an unpacked source tree:

```bash
python -m pip install amr-archetypes       # released version from PyPI
python -m pip install .                     # core, from source
python -m pip install ".[phylo]"            # + the phylogenetic convergence test
python -m pip install -e ".[dev]"           # editable source + test suite
```

NumPy, pandas, SciPy, scikit-learn, PyYAML and pandera. `dendropy` is optional
and only needed for `amr_archetypes.archephy`.

## Quickstart

Run the controls first. They are the reason the real-cohort diagnostics are
interpretable.

```bash
python examples/synthetic/make_data.py

# positive control: 3 planted archetypes
amr-archetypes --config examples/synthetic/planted.yaml --results-dir out/planted

# independent positive confirmation: a different random seed, same design
amr-archetypes --config examples/synthetic/planted_confirmation.yaml --results-dir out/planted-confirmation

# negative control: no clusters at all -> selected_k = 1
amr-archetypes --config examples/synthetic/null.yaml    --results-dir out/null

# adversarial control: all structure is clonal -> flagged as lineage-confounded
amr-archetypes --config examples/synthetic/clonal.yaml  --results-dir out/clonal

# the case study: 1500 Klebsiella pneumoniae genomes
amr-archetypes --config examples/klebsiella/config.yaml --results-dir out/kp

# a second cohort: 677 Streptococcus suis isolates, the susceptibility panel
# split into two layers and the population cluster as the lineage
amr-archetypes --config examples/ssuis/config.yaml      --results-dir out/ssuis
```

Each run writes `summary.json` (headline numbers, claim level and active gates),
`cluster_result.json` (everything), `archetype_profiles.tsv` (per-cluster effect
sizes) and `assignment.tsv` (one row per isolate, joined to every metadata
column, which is the table you actually want to open). It also writes the run
report in two forms, `report.md` and `report.html`, rendered from one
structure: the same sections in the same order, the same numbers, the second
with the diagnostics drawn, so that a panel of intervals that all cross zero
is seen rather than counted. The first page is the measurement summary: the
gates, one row per trait, what was not evaluated on this run and why, and an
interpretation drawn from that table by fixed rules; the pages after it defend
the first. Both forms read every
value from `cluster_result.json` and recompute nothing, both carry the
record's SHA-256, and `report.html` is a single file with no script and
nothing to fetch, so it opens offline.

## Reading the output

`summary.json` is designed to be read top to bottom before anything else:

```json
{
  "selected_k": 2,
  "p_value_structure_report": "p < 1e-100 across all checked split orderings",
  "diagnostic_p_value_structure_exact": 1.3978130041463598e-193,
  "structure_detected": true,
  "discrete_beyond_a_gradient": true,
  "discreteness_status": "ok",
  "discreteness_verdict": "discrete",
  "discreteness_p_value": 0.01,
  "continuum_bootstrap_exceedances": 0,
  "continuum_tail_probability_ci95": {"low": 0.0, "high": 0.03657574498347893},
  "continuum_decision_resolved_at_alpha_0_05": true,
  "continuum_latent_dimension": 3,
  "continuum_null_under_dimensioned": false,
  "n_defining_validated": 17,
  "fusion_n_eff_layers": 1.7893160074349297,
  "fusion_collapse": false,
  "max_empty_stratum_ari": 0.6328112682300324,
  "lineage_concordance_z": 14.0029718182725,
  "lineage_attributable_share": 0.47405282667776627,
  "lineage_confounded": false,
  "claim_level": 3,
  "claim_status": "statistically_discrete_partition",
  "active_gate_codes": ["empty_stratum", "phenotype_superiority"],
  "mdl_gain_fraction_of_null_code": 0.14891050144447857
}
```

The thresholded `p_value_structure_report` is the publication-facing result;
the exact floating-point value is retained only as a diagnostic. Reporting the
decision over checked split orderings avoids presenting a seed/order-dependent
tail value as a stable measurement.

The claim ladder is deliberately monotone: 0 `no_structure`, 1
`descriptive_partition`, 2 `validated_structure`, 3
`statistically_discrete_partition`, and 4 `archetype_candidate`. The complete
result stores every applicable gate with its trigger, threshold, value and
signed margin. Level 4 means the applicable diagnostics passed; it is not
causal, clinical or cross-cohort biological confirmation.

`structure_detected` alone is **not** a claim that archetypes exist. The
feature-split test rejects whenever the held-out features depend on the
discovery labels, which a single continuous gradient also produces.
`discrete_beyond_a_gradient` is the one that distinguishes them, via a
parametric bootstrap from a latent-trait model whose dimension is chosen by BIC.
Here BIC selects `q = 3`; the adaptive `q = 4` fit turns upward, so the optimum
is interior. Zero of 99 null replicates exceed the observed statistic, and the
exact 95% interval for the underlying tail probability is 0-0.0366: enough to
resolve alpha 0.05, but not a claim that the floor `p = 0.01` is precisely
estimated. If a future
dataset instead selects the largest permitted dimension, the software returns
`discreteness_status = "withheld_under_dimensioned"`, a null verdict and no
bootstrap p-value. It never converts an under-dimensioned null into either a
positive or a negative decision.
`mdl_gain_fraction_of_null_code` puts the description-length gain on an
interpretable scale: 0.47 on the planted control, 0.15 on the *Klebsiella*
cohort, -0.00001 on the null control. (The block above is the *Klebsiella*
`summary.json`, the fields that decide the reading: it detects reproducible,
statistically discrete structure and independently trips the artefact and
phenotype gates, with the lineage gate just held. That separation is the case
the diagnostics exist for.)

Exit codes: `0` clean, `1` `--validate` failed its threshold, `2` config or
input error (a refused file, an empty cell under the default policy, a value
that is not 0 or 1), `3` the analysis ran but a diagnostic gate tripped.

## How much of this is the clone?

Ask whether a partition of resistance profiles is really a lineage relabelling
and the honest answer in bacteria is "partly, always". The usual instrument is
a permutation test on same-lineage pair co-assignment, computed over the O(n²)
pairs of the cohort, so its null narrows as the cohort grows while the
structure it measures does not. On the shipped *S. suis* example, with the
partition and the lineage variable held fixed and the cohort subsampled, the
statistic reads

| isolates | attributable share `λ` | concordance `z` |
|---|---|---|
| 67 | 0.268 | 3.4 |
| 135 | 0.310 | 7.4 |
| 270 | 0.340 | 12.2 |
| 473 | 0.358 | 18.0 |
| 677 | 0.349 | 21.1 |

mean of five draws at each size, the partition held fixed and never refitted
(`benchmarks/subsample_series.py`, which writes
`benchmarks/results/ssuis_subsample_series.json`). Under the sequence type, on
the 458 typed isolates, `z` runs from 2.5 to 10.4 while `λ` reads 0.24 to
0.36. A threshold on `z` is a threshold on cohort size wearing a biological
name. The package keeps the `z` as a descriptor and gates on the magnitude
instead; the shipped run, which rebuilds the partition inside every fold,
reads a share of 0.411 against a `z` of 22.2.

```python
from amr_clonalshare.attribution import attribute_partition

a = attribute_partition(trait_matrix, cluster_labels, sequence_types)
a.lam, a.shapley_lineage, a.shapley_partition
```

`attribute_partition` splits the explanatory power of a partition against the
lineage label by commonality analysis and by the two-player Shapley value of
the variance-explained game. `lam` is the
lineage-attributable share and carries the gate; the default threshold is 0.5
and is set in `attribution.lambda_gate`. A run whose point estimate is below
the threshold but whose interval crosses it is reported as unresolved rather
than cleared.

A singleton lineage cannot be predicted out of sample, so `support`, the share
of isolates in a lineage with at least two members, is reported and
`estimable` is withheld below 0.90, a threshold read off the coverage curve in
the calibration benchmark of `amr-clonalshare` rather than chosen. The *K. pneumoniae*
sequence types sit at 0.687 and the whole-cohort estimate is withheld.

The run computes this itself when `dataset.lineage_column` is set, and
reports beside it the share each clustering feature carries on its own, so
that a partition of lineage-locked traits is read as one. The estimators, their
intervals and their calibration are documented in `amr-clonalshare`, which
treats the share as the question rather than as a gate.

## Input format

Each layer is a wide CSV: a strain-ID column plus one 0/1 column per feature.
The config declares the layers, what kind each is, and every choice that changes
the answer:

```yaml
dataset:
  name: my_cohort
  strain_id_column: isolate
  data_dir: data
  metadata: metadata.csv        # optional; not used for clustering
  lineage_column: ST            # enables the population-structure diagnostics
  external_columns: [published_score]

files:
  amr: { path: amr.csv, kind: wide_binary, protected: [Bla_Carb, Col] }
  vir:
    path: vir.csv
    kind: wide_binary
    groups:                     # co-inherited loci, collapsed before distances
      ybt: [ybtS, ybtX, irp1, irp2, fyuA]
      iuc: [iucA, iucB, iucC, iucD, iutA]
  kloc: { path: kloc.csv, kind: one_hot }   # categorical, validated at load

distance:
  metric: jaccard
  undefined_pair: identical     # what two all-zero rows mean. State it.

trait_cluster:
  layers: [amr, vir]
  k_range: [2, 3, 4, 5]         # k = 1 is always added
  collapse_feature_groups: true
```

`kind: one_hot` is not cosmetic: such a layer gets a matching coefficient rather
than Jaccard, is validated to have at most one positive per row, is excluded
from count aggregation, and counts as one hypothesis rather than one per level.

### Empty cells, and what the run does with them

A 0/1 layer has no state for "not measured". An empty field in the CSV, or an
isolate that one layer holds and another does not under
`strain_alignment_policy: union`, is therefore never written as 0, because a 0
reads as absence of the trait. `dataset.missing_policy` decides what happens
instead: `refuse` (default) stops before any estimate and names the rows and
columns; `drop_rows` removes the affected isolates from every layer;
`drop_columns` removes the affected features. Any value other than 0 or 1 is
refused. The choice and its consequences are written to `input_qc.json`.

### Checking the input before the run

```bash
amr-archetypes --config config.yaml --results-dir out --check-input
```

loads the data, applies the policy above, and writes `input_qc.json` and a
plain-language `input_qc.md`, then stops. The same two files are written at
the start of every full run. They record, per layer, the count of isolates of
the rarer outcome for each trait against the project's reporting threshold of
20, and, when `lineage_column` is set, the size of every lineage group, the
number of single-isolate lineages, the resulting support, and whether the
lineage-share estimator will accept the cohort at that typing resolution. There
is no single minimum sample size: what binds is the number of lineages with at
least two isolates and the count of the rarer outcome, and the check reports
both so the verdict is visible before the estimate is made.

## What is in the box

| module | what it is for |
|---|---|
| `qc` | the input check: empty cells and the policy applied, per-trait counts, per-lineage group sizes and the estimator's verdict |
| `core` | the pipeline: gating, distances, fusion, k selection, consensus, profiles |
| `fusion` | Wang et al. (2014) affinity and cross-diffusion, order-invariant; both published update rules |
| `inference` | feature splitting, p-value merging, count splitting, the continuum null |
| `influence` | leave-one-layer-out influence, effective number of layers |
| `lineage` | same-lineage pair concordance, cluster composition, de-replication, co-inherited blocks |
| `baselines` | concatenation, single layers, Bernoulli mixture, each under the same held-out test; paired external agreement |
| `archephy` | exact phylogenetic convergence test for small cohorts (needs dendropy) |
| `small_n` | gap statistic with a matched observed/reference clusterer |

## Methods and calibration

`docs/methodology.md` states every statistic, threshold and assumption with its
citation. `benchmarks/calibration_study.py` regenerates every type-I and power
number the paper quotes:

```bash
python benchmarks/calibration_study.py --quick        # ~2 min smoke run
python benchmarks/calibration_study.py                # the full study
```

Binary distances with an explicit empty-union policy, the permutation
p-value and Benjamini-Hochberg control are taken from `amr_clonalshare.stats`,
so that both packages score a pair of rows the same way.

The article and its supplement are not part of this repository.

## Tests

```bash
pytest -m "not slow"      # a few minutes
pytest                    # + the Monte-Carlo calibration tests
```

## Citing

See `CITATION.cff`. The *Klebsiella* data in `examples/klebsiella/data/` is
**not** covered by this repository's MIT licence. It derives from Lam et al.
(2021) and is redistributed under CC BY 4.0. See
`examples/klebsiella/DATA_PROVENANCE.md`, which also lists the reproducibility
gaps we could not close. The *S. suis* panel in `examples/ssuis/data/` derives
from Hadjirin et al. (2021); see `examples/ssuis/DATA_PROVENANCE.md`.

The lineage-share estimators this package gates on are
[`amr-clonalshare`](https://github.com/maciejkochanowski/amr-clonalshare),
installed as a dependency; cite it when the share itself is the result.

## License

MIT for the code; see [`LICENSE`](LICENSE).
