# amr-archetypes run report

Every number below is read from `cluster_result.json` and `summary.json`, written by the same run; none is recomputed here.

- **Run:** A1DDF6F2
- **Issued:** 2026-09-10T00:27Z
- **Software:** amr-archetypes 1.0.0
- **Isolates:** 1500
- **Layers:** amr, vir
- **Seed:** 42
- **Configuration:** sha256:f828f63c8977
- **Record digest:** sha256:5cf1eaa69729a2888e03be7566b974bcb5252676fd97340ae01316b5f23836b7

**Profile-group claim level 3, statistically discrete partition.** 2 of 7 applicable gates closed on this run.

## 1. Measurement summary

**Question asked.** Whether this collection holds recurring resistance profiles: groups of isolates that recur on traits held out of the clustering, that are separated by gaps rather than cut from a gradient, that are not manufactured by the shape of the panel, and that are not the lineages under another name.

- **Profile groups:** 2
- **Cohort:** 1500 isolates, 2 layers
- **Recurrence on held-out traits:** p < 1e-100 across all checked split orderings
- **Discrete beyond a gradient:** discrete
- **Share of the grouping explained by lineage:** 0.474; gate at 0.50
- **Claim:** level 3, statistically discrete partition

**Gates.** 2 of 7 applicable conditions closed on this run. A closed gate is a result, not an error: it says the collection cannot support the reading. No gate closed does not establish that the groups are biological types.

> **Not evaluated on this run, and why**
>
> Permutation null for the description length: not requested. The held-out test is the evidence for real structure.
>
> Interval on the share of the profile groups explained by lineage: not given, because the groups were re-fitted inside every cross-validation fold and a lineage drawn twice would train a group on rows that are also held out. The spread across repeated cross-validation is 0.026.
>
> Permutation test on layer contribution: skipped above 500 isolates, where it would cost as many network fusions as permutations times layers; the leave-one-layer-out influence in Table 6 was computed.
>

> **Interpretation (generated from the record by fixed rules)**
>
> The 2 groups recur on features held out of the clustering (p < 1e-100 across all checked split orderings).
>
> They are separated by gaps rather than cut from a gradient.
>
> Lineage explains 0.474 of the grouping, below the gate: the groups cut across lineages.
>
> The largest group is the isolates that carry none of the traits of a layer; it is an absence, not a profile.
>
> A one-dimensional resistance score predicts the measured phenotype better than the grouping does.
>
> These sentences follow from the record by fixed rules and carry no judgement beyond it.
>

## 2. Admissibility of the input

- **Lineage column:** `ST`
- **Binary layers:** amr, vir
- **Distance:** jaccard (undefined pairs: identical)
- **Fusion:** similarity-network fusion, K=30, mu=0.5, T=20
- **Resampling:** 30 consensus, 200 bootstrap, 0 permutations

Empty cells in the binary layers: 0. Nothing was filled in.

Lineage groups in the input: 768, of which 469 hold a single isolate. Support 68.7 % against the 90.0 % the estimator needs: not accepted at this typing resolution.

**Table 1.** Conditions the diagnostics require before any result is reported.

| Condition | Observed | Required | Verdict |
|---|---:|---:|---|
| Lineage support | 68.7 % | ≥ 90.0 % | refused |
| Lineage groups used | 768 of 768 | reported | accepted |
| Effective layers | 1.8 | > 1.5 | accepted |
| Split design | adequate | adequate | accepted |

## 3. Are there resistance-profile groups?

The selection procedure returned **2** profile groups. Tested on features held out of the clustering, the grouping reproduces at p < 1e-100 across all checked split orderings. The structure is separated by gaps rather than shading continuously from one type into the next (discrete).

The labels re-derived inside each split resemble the reported grouping at a median adjusted Rand index of 0.54 (range 0.02 to 0.77 over 15 splits), so the held-out evidence concerns this grouping.

*Figure 1 (drawn on the page).* Description length saved by describing the cohort as k archetypes rather than as one population. The turn in the curve, not a threshold, is what selects k.

**Table 2.** Evidence behind the number of groups.

| Quantity | Value | Reading |
|---|---:|---|
| Groups selected | 2 | by minimum description length |
| Description length saved | 2660 bits | 14.9 % of the null code |
| Permutation null for that gain | not run | a permutation null for the description length is optional and was not requested; the held-out test below is the evidence for real structure |
| Held-out reproducibility | p < 1e-100 across all checked split orderings | groups recur on features not used to form them |
| Continuum exceedances | 0 of 99 | upper limit of the exact binomial interval 0.0366 |
| Latent dimension of the null | 3 | chosen by information criterion, not pinned |

## 4. Could the grouping be an artefact of the panel?

A grouping can arise from the shape of the panel rather than from the isolates. Three things are checked per layer: how many isolates carry no informative feature at all, how many independent directions the layer really holds, and whether the nearest-neighbour cut that builds the affinity graph was decided by ties rather than by distance. A tie inflation of 1.00 means the cut was clean; a value above it means more neighbours were kept than asked for, because candidates shared the same affinity.

**Table 3.** Panel geometry, layer by layer.

| Layer | Features used | Effective dimension | Uninformative isolates | Tie inflation at the cut | Empty-stratum agreement |
|---|---:|---:|---:|---:|---:|
| amr | 14 | 5.18 | 41.1 % | 9.157 | 0.633 |
| vir | 5 | 2.45 | 66.9 % | 24.534 | -0.005 |

The empty-stratum check re-runs the grouping on isolates that carry nothing in one layer. Where it returns a value, an agreement near one would mean the grouping is reproduced by absence alone. The largest value on this run is 0.633.

## 5. Does the grouping beat a simpler rule?

A grouping that a single layer or a plain concatenation reproduces has not earned the fusion that produced it. Every candidate below was run through the same held-out test the reported grouping had to pass: its own pipeline on the discovery half of the feature blocks, scored on the held-out half. That test is the criterion that can rank candidates. The description length is computed in sample and favours a candidate fitted by likelihood on these same bits, so it is shown and decides nothing; agreement with an external labelling is shown as a paired difference from the reported grouping with its interval, so that "not distinguishable" is a possible answer.

**Table 4.** Candidate groupings. Held-out: the feature-split test on the candidate's own pipeline. Description length: in sample, descriptive only.

| Candidate | Groups | Held-out | Description length saved | Agreement with reported |
|---|---:|---:|---:|---:|
| fused snf | 2 | p < 0.001 | 2660 | 1.000 |
| concatenation | 2 | p < 0.001 | 1921 | 0.587 |
| solo amr | 2 | p < 0.001 | 3881 | 0.633 |
| solo vir | 2 | p < 0.001 | 281 | -0.005 |
| bernoulli mixture | 2 | p < 0.001 | 4675 | 0.467 |

**Table 5.** Agreement with each external labelling, as the difference in adjusted Rand index between the candidate and the reported grouping on the same bootstrap resamples of isolates, with its 95 % interval. * marks a difference whose interval excludes zero; without it the two cannot be told apart by that labelling.

| Candidate | virulence score | resistance score | K locus | Convergence event |
|---|---:|---:|---:|---:|
| concatenation | -0.114 * -0.133 to -0.096 | -0.128 * -0.159 to -0.105 | -0.000 -0.002 to 0.001 | -0.033 * -0.133 to -0.043 |
| solo amr | -0.028 * -0.043 to -0.015 | +0.136 * 0.107 to 0.167 | -0.001 -0.002 to 0.000 | -0.033 * -0.139 to -0.044 |
| solo vir | +0.838 * 0.803 to 0.869 | -0.105 * -0.143 to -0.072 | +0.000 -0.001 to 0.002 | -0.033 * -0.146 to -0.044 |
| bernoulli mixture | -0.035 * -0.047 to -0.023 | +0.243 * 0.203 to 0.282 | +0.000 -0.001 to 0.001 | -0.008 -0.055 to 0.007 |

5 of 5 tested groupings reproduce on held-out features. The reported grouping is one of several admissible descriptions of this collection; the held-out test does not prefer one of them. The description length in sample is largest for bernoulli mixture, as is expected of a grouping fitted by likelihood on these bits; it does not say which grouping is real. Agreement with an external labelling differs distinguishably from the reported grouping for concatenation (lower on Convergence event, lower on resistance score, lower on virulence score), solo amr (lower on Convergence event, higher on resistance score, lower on virulence score), solo vir (lower on Convergence event, lower on resistance score, higher on virulence score) and bernoulli mixture (higher on resistance score, lower on virulence score). Whether higher agreement is a merit depends on the labelling: closer agreement with a lineage label means the groups are closer to being the lineages, which is the confounding the attribution measures, not a gain.

## 6. Which layer carries the grouping?

Layers contribute differently and jointly. The effective number of layers is 1.79 of 2, and the layer that moves the answer most is **amr**. A layer marked inert can be removed without changing the grouping.

*Figure 2 (drawn on the page).* Weight each layer carries in the fused network. A layer drawn in the warning colour is inert: the grouping does not change when it is removed.

**Table 6.** What each layer contributes.

| Layer | Weight | Loss when removed | Agreement alone with the fused grouping | Inert |
|---|---:|---:|---:|---|
| amr | 0.731 | 1.000 | 0.633 | no |
| vir | 0.269 | 0.367 | -0.005 | no |

Mean disagreement between layers, taken over layer pairs only, is 0.535.

## 7. How stable is the grouping?

**Table 7.** Behaviour under resampling and under removal.

| Quantity | Value | Reading |
|---|---:|---|
| Proportion of ambiguous pairs | 0.152 | share of pairs that neither always nor never co-cluster across consensus draws; zero is a clean split |
| Area under the consensus distribution | 0.481 | a flat consensus matrix drives this towards one |
| Largest isolate fragility | 0.684 | how far one isolate can move the grouping |
| Largest feature fragility | 0.067 | how far one feature can move the grouping |
| Label recovery from half the features | 0.950 | recovery of the pipeline's own labels from half the features; internal coherence, not external predictive validity |

## 8. What may be concluded, and what may not

The highest claim the profile-group diagnostics carry is **level 3**, statistically discrete partition. That level attests reproducible structure in the reported grouping; it does not say that the reported grouping is the best of the candidates in Table 4, which is a separate question answered there. Every gate was evaluated; the margin is the distance the run had left before the gate would have closed.

*Figure 3 (drawn on the page).* Distance to failure for each gate that carries a numeric margin. A short bar is a result that only just holds.

**Diagnostic failure:** the partition largely reproduces the 'carries no feature of layer 'amr'' indicator (ARI 0.63); this is an artefact of the empty-union distance convention, not trait structure

**Diagnostic failure:** the partition is significantly beaten on measured phenotype by the single rule 'external_resistance_score_above_median': mean balanced accuracy 0.695 against 0.790 over the 19 antibiotics with enough tested isolates (permutation floor 0.554), difference +0.090 with bootstrap 95 % CI [+0.048, +0.125]. Whatever the fusion found, a laboratory could have got it from one column

**Table 8.** Gate ledger. Every gate is listed, including those that did not fire.

| Gate | Applicable | Closed | Observed | Threshold |
|---|---|---|---|---|
| fusion collapse | yes | no | 1.789 | 1.500 |
| empty stratum | yes | yes | 0.633 | 0.500 |
| post clustering inference | yes | no | ok | status is ok |
| split design | yes | no | yes | adequate is true |
| lineage confounding | yes | no | lineage attributable share 0.474; ci95 not computed (+7 more in the record) | lineage attributable share below 0.500 |
| phenotype superiority | yes | yes | rules beating partition [external_resistance_score_above_median]; worst ci95 low minus partition 0.048 | no tested simple rule has bootstrap CI95 low > 0 |
| continuum discreteness | yes | no | status ok; p value 0.010 (+1 more in the record) | status is ok and p value < 0.05 |

## 9. Provenance and terms

- **Software:** amr-archetypes 1.0.0, record schema 1.0
- **Seed:** 42
- **Configuration:** `sha256:f828f63c8977`
- **Record:** `sha256:5cf1eaa69729a2888e03be7566b974bcb5252676fd97340ae01316b5f23836b7`

> **Terms used in this report**
>
> **Profile group.** A set of isolates the fused layers place together. It is a description of this collection until the diagnostics say more.
>
> **Held-out recurrence.** Whether the groups formed on one half of the traits are found again on the other half, which the same data cannot manufacture.
>
> **Share of the grouping explained by lineage.** How much of what the groups explain the lineage label already explains. Near 1: the groups are the lineages under another name. Near 0: they cut across lineages.
>
> **Control.** The same calculation on shuffled lineage labels, which should return roughly zero; a share is read against it.
>
> **Support.** The share of isolates sitting in lineages large enough to inform the lineage share; below 0.90 the software withholds it.
>
> **Gate.** A condition fixed before the run. If it does not hold, the software withholds the reading and names the condition that failed.
>

## Notes on reading this report

- § Derived arithmetically from a quantity recorded elsewhere in the record rather than estimated in this run.

amr-archetypes 1.0.0 · record schema 1.0 · seed 42 · configuration sha256:f828f63c8977
Cite this run as: “amr-archetypes 1.0.0, run A1DDF6F2, 2026-09-10T00:27Z.”
This report supersedes any earlier report bearing the same run identifier. It is regenerated from the record and holds no value that the record does not. The symbols carry the same wording in every run of this software; no symbol against a value means only that none of the listed conditions fired. Intervals are printed as computed, without clipping to the natural bounds of the quantity; clipping would leave their coverage unchanged and is left to the reader so that widths stay comparable across runs.
