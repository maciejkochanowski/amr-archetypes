# Methodology

Every statistic the package computes, its definition, the choice it embodies and
the citation behind it. Where a default is consequential the reasoning is given
here rather than in a docstring.

---

## 1. Inputs and gating

**Layers.** One or more wide binary matrices, strains × features, declared in
the config with a `kind`:

* `wide_binary`: independent 0/1 presence calls. Jaccard-family distance.
* `one_hot`: a categorical variable expanded to indicators (capsule K locus, O
  antigen, MLST). Validated at load time to have at most one positive per row,
  given a matching coefficient rather than Jaccard, excluded from count
  aggregation, and counted as **one** hypothesis in the FDR set rather than one
  per level. Jaccard over a one-hot block takes only a handful of distinct
  values and is not a usable similarity.

**Feature groups.** `files.<layer>.groups` names co-inherited blocks (operons,
mobile elements). With `collapse_feature_groups: true` each group becomes a
single presence call *before* distances are computed. This matters twice: an
uncollapsed encoding weights a biological unit by its gene count, and it also
breaks the post-clustering inference (§4.2).

**Prevalence gate.** Keep features with `lo < prevalence < hi` and at least
`min_count` carriers. The default `lo = 0.0, min_count = 2` deliberately keeps
rare determinants: a 2 % floor removes exactly the emergent colistin,
tigecycline and carbapenemase columns that AMR surveillance exists to detect.
`files.<layer>.protected` exempts named features from the gate. A feature
present in **zero** isolates is always removed, because it cannot inform a
distance, cannot be tested, and would occupy a slot in the FDR denominator, and
is
reported with that reason. Everything removed appears in
`layer_reports[].gated_out`.

---

## 2. Distances

| metric | definition |
|---|---|
| `jaccard` | `1 - a/(a+b+c)` |
| `dice` | `1 - 2a/(2a+b+c)` |
| `simple_matching` / `hamming` | `(b+c)/p`, counts shared absence |

with `a` the shared presences and `b`, `c` the exclusive counts.

**The empty-union convention is a declared choice, not a default.**
Jaccard is undefined when two isolates carry none of a layer's features. The
textbook convention sets the similarity to 1, on the reading that two genomes
sharing no detected
determinant are declared maximally similar. On accessory-genome data this is
consequential: absence is the default state, it is confounded with assembly
quality, and trait-absent isolates are usually the majority. In the *Klebsiella*
cohort 1004 of 1500 isolates had an all-zero virulence row; under the classical
convention they formed one clique of 503 506 pairs at distance zero, and the
all-zero indicator alone reproduced the resulting single-layer partition at ARI 0.83
in that audit. On the shipped two-layer record, which sweeps to ten groups and
selects ten, the per-layer indices read 0.260 and 0.216, but the largest group
is exactly the 409 isolates that carry nothing in either layer, and the
largest-group check below closes the gate.

`distance.undefined_pair` takes `identical` (D = 0, classical), `distinct`
(D = 1) or `nan`. Whichever is chosen is echoed into the result, and
`artifact_diagnostics.per_layer[].empty_stratum_ari` reports the ARI between the
whole partition and each layer's all-zero indicator, and
`artifact_diagnostics.largest_group` compares the largest group against the rest
with the indicator "carries no retained feature of any layer", because the
per-layer index is diluted once k is large: on the shipped *Klebsiella* record
the per-layer values are 0.260 and 0.216 at ten groups while the largest group,
409 isolates, is exactly the all-empty set (ARI 1.000). The larger of the two
is `max_empty_stratum_ari`; at or above 0.5 the gate closes.

---

## 3. Fusion

Similarity network fusion, Wang et al. (2014), *Nat Methods* 11:333-337,
[10.1038/nmeth.2810](https://doi.org/10.1038/nmeth.2810).

**Kernel.** `W(i,j) = exp(-d²/(mu·eps_ij))` with

```
eps_ij = ( mean_{k in N_i} d(i,k) + mean_{k in N_j} d(j,k) + d(i,j) ) / 3
```

where `N_i` is `i`'s **K nearest neighbours**, self excluded. Using the global
mean distance instead, as an earlier draft of this code did, removes the local
scaling the kernel exists to provide. Both reference implementations (SNFtool's
`affinityMatrix.R`, snfpy's `make_affinity`) use the K-nearest-neighbour mean.
Note that those implementations use a Gaussian *density* rather than the
exponential form above; the two differ by a scale factor absorbed into `mu`.

**Cross-diffusion.** `P_v <- normalise( S_v · mean(P_{u != v}) · S_vᵀ )` for `T`
iterations, with each view's transition matrix re-symmetrised **inside** every
iteration (SNFtool does this; symmetrising only the final average lets asymmetry
accumulate over `T` steps).

**Sparsification and ties.** `S_v` keeps each row's `K` largest affinities.
`argsort(-W[i])[:K]` is ill-defined when more than `K` candidates tie at the
cut, and binary trait data produces exactly that: on the *Klebsiella* virulence
layer the median row had ~1000 candidates tied at `K = 30`. Which of them was
kept depended on the input file's row order, so the partition was not
equivariant under relabelling of samples (ARI 0.59-0.98 against the unpermuted
run). `tie_policy: inclusive` keeps **every** neighbour tied with the `K`-th
largest, which is order-invariant by construction. The test suite asserts
ARI = 1.0000 across row permutations, and the run reports
`layer_reports[].knn_ties.tie_inflation` = mean degree / `K`. A value far above
1 means the affinity has too few distinct values for a KNN graph to be
meaningful.

`snf.K`, `snf.mu`, `snf.T`, `snf.alpha` and `snf.tie_policy` are all config
keys. A single-layer fusion is legal and returns that layer's normalised
transition matrix.

---

## 4. Post-clustering inference

### 4.1 The problem, and why data thinning does not solve it here

Testing which features distinguish clusters estimated from those same features
is double dipping: Gao, Bien & Witten (2024), *JASA* 119:332-342,
[10.1080/01621459.2022.2116331](https://doi.org/10.1080/01621459.2022.2116331);
Chen & Witten (2023), *JMLR* 24(152).

Data thinning, Neufeld, Dharamshi, Gao and Witten (2024), *JMLR* 25(57):1-35,
splits an observation into independent parts from the same family. Its Remark 8
states that infinite divisibility "prevents us from thinning the Bernoulli or
categorical distributions". Coarse-graining to counts and thinning those fails
twice on real panels: the aggregates are often rescaled indicators rather than
counts (a yersiniabactin tally taking only {0, 8}; one-hot capsule "counts"
in {0,1} with an exact linear dependence among them), and the negative-binomial
recipe needs the size parameter **known**. Proposition 11 of the same paper
gives the damage when it is not:

```
cov(X1, X2) = (1 - eps) · r · ((1-p)/p)² · (1 - (r+1)/(r~+1))
```

negative when `r~ < r`, positive when `r~ > r`. With a pooled estimate
`r̂ = 0.43` the realised within-column correlation on the *Klebsiella* aggregates
was −0.174, against +0.003 for a genuine NB matrix with `r` known. Hivert et al.
(2024, [arXiv:2405.13591](https://arxiv.org/abs/2405.13591)) reach the same
conclusion empirically.

Where a count model *is* defensible the machinery is retained and **checked**:
per-feature dispersion, `screen_thinnable` refusing under-dispersed,
near-binary and exactly collinear columns with a stated reason, and the realised
`corr(X1, X2)` reported and gated. `binomial_thin` implements the hypergeometric
split for bounded row-sums over `m` known members, where nothing is estimated.

### 4.2 Feature splitting, and the block requirement

For binary panels the split is over **features**: cluster on a random half,
test the held-out half, repeat. The group contrast within a split is the largest
*discovery-block* cluster against the rest, so no grouping or direction is ever
chosen from the values being tested.

**The split must respect the dependence structure of the features.** The null
actually tested is

> H0: the held-out features are independent of the labels learned from the
> discovery features

which is implied by "features are mutually independent", **not** by "there are
no clusters". Measured on a no-cluster null with features in correlated blocks
of five, a per-feature split has family-wise error **1.000** at nominal 0.05,
because a block straddling the two halves makes the discovery labels predict the
held-out features for reasons unrelated to clustering. Passing `groups`, which
`core.run` does automatically from the config's declared feature groups, with
each `one_hot` layer as a single unit, assigns whole blocks to one side and
restores validity: on the 4,000-replicate calibration
(`benchmarks/results_n4000_2026-08-14/B_feature_splitting_n4000.json`) the
per-feature split rejects the blocked null 99.98 % of the time and the
block-aware split 1.95 %, against 2.4 % and 2.5 % when the features are
independent.

Each split re-runs the *same* procedure the reported partition came from
(per-layer distances with each layer's declared kind, cross-diffusion fusion,
spectral clustering) on the discovery features, and
`ari_discovery_vs_reported` records whether the per-split labels resemble the
reported partition. If they do not, the p-value is about detectable structure in
general and not about this partition, and `concerns_reported_partition` says so.

### 4.3 Merging the splits

One split gives one p-value, and that p-value is random even with the data
fixed: forty draws of a single-split implementation returned p between
3.8 × 10⁻⁶³ and 0.97. Repeated splits of one fixed dataset are **exchangeable**
but arbitrarily dependent, so Fisher and Stouffer combination are invalid and
the minimum is catastrophically so. A multiplicative constant is unavoidable.

| `tva.merge` | rule | reference |
|---|---|---|
| `exchangeable_ruger` (default) | `(K/k)·min_{l≤K} p^(l)_(⌈lk/K⌉)` | Gasparin, Wang & Ramdas (2025), *PNAS* 122:e2410849122, Thm 4.1 |
| `ruger` | `(K/k)·p_(k)` | Rüger; see Vovk & Wang (2020) §2 |
| `twice_mean` | `2·mean(p)` | Vovk & Wang (2020), *Biometrika* 107:791-808 |

`amr_archetypes.inference.mmb_merge` implements the Meinshausen, Meier &
Bühlmann (2009, *JASA* 104:1671-1681, Eq. 2.3) quantile rule as a library
function for comparison; it is not selectable from the configuration.

All three hold their level on an equicorrelated Gaussian-copula exchangeable null
at ρ ∈ {0, 0.5, 0.9}; the exchangeable Rüger rule is the least conservative,
which is why it is the default.

### 4.4 Structure is not the same as discreteness

The split test rejects on a single continuous gradient as readily as on discrete
groups. Comparing a `k`-component Bernoulli mixture with one component by BIC
does not settle it either: two components fit a gradient better than one.

`inference.continuum_null_test` fits a *q*-factor logistic latent-trait model.
It evaluates `q = 1..3` first and, only when `q = 3` is the provisional boundary
optimum, extends to the supported `q = 4`; the default maximum is therefore 4.
It then simulates from the selected model and compares the
observed `BIC(q-factor) − BIC(k-component mixture)` against what the continuum
itself produces. The null therefore preserves the feature dependence that
breaks the naive tests. On planted discrete data it rejects; on data simulated
from a sufficiently dimensioned continuum it does not. If BIC is still falling
at `q_max`, the function stops before bootstrap and returns
`withheld_under_dimensioned`, `p_value = null` and a null discreteness verdict:
rejection against a known-under-dimensioned continuum is not evidence of
archetypes. With an estimable interior optimum the verdict is explicitly
`discrete` or `continuum_compatible`. The p-value is Phipson-Smyth corrected, so
its floor is `1/(n_boot+1)`, reported alongside; at least 20 bootstrap draws are
required so a test at alpha 0.05 is attainable.

### 4.5 Small cohorts: phylogenetic convergence

Splitting throws away information and has no power at *n* of order 100.
`amr_archetypes.archephy` asks a different question: did a candidate
archetype's `k` traits arise *repeatedly and independently* across a
phylogeny?

Fitch parsimony (Fitch 1971, *Syst Zool* 20:406-416) gives per trait the set
`S_t` of change edges, `c_t = |S_t|`, on a tree with `E` non-root edges. The
`k`-way joint homoplasy count is `m = |S_1 ∩ … ∩ S_k|`. Under independent
evolution with exchangeable edges the binomial moments are
`E[C(M,j)] = C(E,j)·∏_t C(c_t,j)/C(E,j)`, so

```
P(M >= m) = sum_{j>=m} (-1)^(j-m) · C(j-1, m-1) · E[C(M,j)]
```

evaluated in exact rational arithmetic. At `k = 2` this equals the
hypergeometric survival function (verified in the test suite); at `k = 3` it
agrees with brute-force enumeration. The arithmetic is exact but the null is
not the biological one: real change edges concentrate on short and terminal
branches, so two traits that evolved independently share change edges more
often than uniform subsets of edges do. On birth-death trees with traits
evolved under independent two-state Markov chains
(`benchmarks/results/archephy_size.json`) the exact null rejects at 0.072 to
0.078 against a nominal 0.05 under a strict clock and at 0.14 under a relaxed
one. The default is therefore `method="ctmc"`, a Monte Carlo null that
simulates each trait down the actual tree conditioned on its observed number
of changes, at or below nominal in every strict-clock cell (0.017 to 0.033);
the exact tail is reported beside it as `p_value_exact_uniform_null`. A
Poisson approximation (`method="poisson"`, the first moment of the exact
null) is kept for comparison, and `method="weighted"`, which samples edges in
proportion to branch length, is the one null that stays below nominal under
the relaxed clock (0.033).

`m >= 2` is required for a positive call: one joint change edge is a single
clonal co-origin, the confounder the test exists to reject.

---

## 5. Choosing k, including k = 1

Every criterion sweeps `[1] + k_range`. A criterion whose sweep starts at 2
cannot report "there are no clusters", and on noise it will not: measured, such
a sweep returns k = 2 in 100 % of replicates where a sweep including 1 returns
k = 1 in 100 %.

| `k_select_primary` | rule |
|---|---|
| `mdl` | largest description-length gain; **k = 1 unless some k has positive gain**; a best k at the top of `k_range` is flagged (`mdl_optimum_at_k_range_boundary`) and closes the `k_selection` gate, because the curve has not been seen to turn |
| `prediction_strength` | largest k with mean PS ≥ threshold, else 1 (Tibshirani & Walther 2005) |
| `gap` | 1-SE rule over a sweep including k = 1 (Tibshirani, Walther & Hastie 2001) |
| `bic_mixture` | BIC over Bernoulli-mixture fits including k = 1 |

**MDL.** `gain = L_null − (L_assign + L_profiles + L_residuals)` with
`L_assign = n log₂ k`, residuals coded under the per-cluster Krichevsky-Trofimov
estimate, and parametric complexity `(d/2) log₂ n` charged to **both** models
(Rissanen 1983; Grünwald 2007). Charging the clustered model twice that rate and the
null model nothing, which is the obvious shortcut, is not a code-length
comparison. `mdl_gain_fraction` puts the gain on
an interpretable scale: 0.47 on the planted control, 0.16 on the *Klebsiella*
cohort and -0.00001 on the null control, because a large bit count can still be a small fraction.

**Gap statistic.** Observed and reference samples are clustered by the **same**
procedure, so estimator bias cancels; `null_labeler` is a required argument.
Clustering the two with different algorithms accounts for 92-105 % of the
reported Gap on null data. The reference is
independent Bernoulli matched to each feature's prevalence, a stated deviation
from the paper's uniform reference, which is not defined for binary data.

**Permutation calibration.** `mdl_null_calibration` re-runs the whole
distance → fusion → spectral chain on column-permuted data. It costs
O(n_perm·T·m·n³) and is therefore **opt-in** (`run(..., n_perm=199)`). The
p-value uses the Phipson & Smyth (2010) `(b+1)/(B+1)` correction and reports its
minimum attainable value; a permutation p-value can never legitimately be 0.

---

## 6. Diagnostics

**Layer influence** (`influence.layer_influence`). `delta_loo[l] = clip(1 −
ARI(fuse(all), fuse(all \ l)), 0, 1)`, which is interventional rather than
merely descriptive.
Normalised to weights whose Hill number of order 1 (Hill 1973, *Ecology*
54:427-432) is the **effective number of contributing layers**. `n_eff` alone
cannot separate "every layer agrees, so removing one changes nothing" from "no
layer matters": both give `delta_loo ≈ 0`. The `regime` field uses the solo
agreements to resolve it: `complementary`, `redundant` (every layer alone
reproduces the fused partition), `collapsed` (`n_eff` below
`collapse_threshold`, 1.5 by default: one layer drives the result),
`unstructured` (removing any layer changes the partition and none reproduces
it alone) and `uninformative` (no layer reproduces it and removing any
changes nothing). The gate closes on `collapsed`, `unstructured` and
`uninformative`; `redundant` is reported and does not close it, because a
fusion that agrees with every single layer has lost nothing. An optional permutation
test (row-permute one layer, re-fuse) gives each layer a p-value.

**Population structure** (`lineage.lineage_concordance`). The fraction of
same-lineage pairs that are also same-cluster, against a permutation null of the
cluster labels. AMI is the wrong instrument: with hundreds of singleton lineages
the chance correction dominates, and on the shipped *Klebsiella* record
AMI(cluster, ST) = 0.076 while the pair concordance is 0.396 against a null of
0.174 (z = 23.7). `cluster_composition` reports the maximum single-lineage share per
cluster; `dereplicate_index` supports the one-isolate-per-lineage sensitivity
run.

The concordance answers whether there is any lineage signal, and on a real
cohort there always is, more emphatically the larger the cohort: the
statistic is computed over the O(n²) pairs, so its null narrows with n while
the structure it measures does not. The gate is therefore carried by a
magnitude, the lineage-attributable share of the partition, `lam`, from
`amr_archetypes.attribution.attribute_partition`: the explanatory power of
the partition on the trait matrix, estimated out of sample with the
partition rebuilt inside every fold, split against the lineage label by
commonality analysis and by the two-player Shapley value of the
variance-explained game. The threshold is `attribution.lambda_gate`, 0.5 by
default, decided by the point estimate; where an interval is computed and
crosses it the reading is marked unresolved rather than cleared. Both `lam`
and the trait-level clonal share reported beside it are held to the support
rule of the estimator: when fewer than 90 % of isolates sit in lineages of at
least two members, the support below which the estimator's coverage was
measured to fail, the values are reported without a verdict and the
`lineage_support` gate closes; on the *Klebsiella* cohort the support is
0.687 and the lineage verdict is withheld at sequence-type resolution. The
estimator is `amr_archetypes.attribution.attribute_partition`; its intervals
and its calibration study are documented with the companion package
`amr-clonalshare`, which carries the same estimator.

**Baselines** (`baselines`). Every candidate partition, meaning the fusion, the
naive concatenation, each single layer and a Bernoulli-mixture latent class
model, is put through the same feature-split held-out test as the reported
partition (`held_out`), so each candidate is attested or not on the same
criterion, and is scored on MDL gain and on the same external criteria. The
MDL gain is an in-sample quantity and favours the candidate fitted by
likelihood on the same bits, so it is reported with that scope and does not
decide. Agreement with the fused partition cannot rank candidates, because it
measures agreement with the tool's own answer. Against each external label the
record holds the paired difference in adjusted Rand index between the candidate
and the reported partition with a bootstrap interval over isolates
(`external_agreement_vs_reported`); a difference whose interval excludes zero
is distinguishable, and its direction is stated without a verdict, since a
higher agreement with a lineage label is the confounding the attribution
measures, not merit. If a single layer or a domain rule reproduces where the
fusion does not, that is the result.

**Collinearity.** `amr_archetypes.stats.effective_dimension` is the participation ratio of a
layer's correlation eigenspectrum: how many mutually uncorrelated columns the
block is worth. A set of `p` perfectly collinear columns has effective dimension
1 however large `p` is.

---

## 7. Descriptive profiles, labelled as such

`archetype_profiles.tsv` gives per (cluster, feature): Δp with a bootstrap
interval, Cohen's *h*, a Haldane-corrected log-odds-ratio, a Fisher exact
p-value with Benjamini-Hochberg FDR, and `is_defining_descriptive`
(|h| ≥ 0.5, BH reject, support ≥ 3; all three configurable).

These are **effect sizes, not inference**. The partition was estimated from the
same matrix, so the p-values do not have their nominal meaning under the null.
They rank features; §4 tests them. The output keys carry the `descriptive_`
prefix for that reason.

`label_recoverability` reports how well a partial feature vector recovers the
label the pipeline itself assigned. It has no external target and no null; a
value near 1.0 is the expected, uninformative result. It is reported with that
caveat attached rather than as predictive validation.

---

## 8. Reproducibility

Every stochastic stage draws from its own generator spawned off `--seed` via
`numpy.random.SeedSequence`, so adding a diagnostic cannot perturb the
clustering. `spectral_from_similarity` takes an explicit `random_state`.

Byte-identity of a floating-point spectral pipeline is not achievable across
BLAS and scikit-learn builds and is not claimed. What is claimed, and tested, is
invariance to input row order, stability of the selected k, and reproducibility
of the whole result within one environment at a fixed seed. `cluster_result.json`
is serialised with `allow_nan=False` and an explicit numpy encoder, so it is
valid RFC 8259 JSON that a non-Python parser can read.
