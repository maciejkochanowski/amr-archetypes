# amr-archetypes run report

Every number below is read from `cluster_result.json` and `summary.json`, written by the same run; none is recomputed here.

- **Run:** A06124B1
- **Issued:** 2026-09-10T20:31Z
- **Software:** amr-archetypes 1.0.0
- **Isolates:** 677
- **Layers:** ribo, cell
- **Seed:** 42
- **Configuration:** sha256:d52a0f5c7b4c
- **Record digest:** sha256:3fa88a4ef2ed7ba56d1ebc81958be3c8881baf444c3efb1045f7ed94d89ee6fe
- **Stack:** Python 3.11.15, numpy 2.4.6, scipy 1.17.1, pandas 3.0.5, scikit-learn 1.9.0

**Profile-group claim level 4, archetype candidate.** 0 of 8 applicable gates closed on this run.

## 1. Measurement summary

**Question asked.** Whether this collection holds recurring resistance profiles: groups of isolates that recur on traits held out of the clustering, that are separated by gaps rather than cut from a gradient, that are not manufactured by the shape of the panel, and that are not the lineages under another name.

- **Profile groups:** 6
- **Cohort:** 677 isolates, 2 layers
- **Recurrence on held-out traits:** p < 0.001 across all 50 checked split orderings
- **Discrete beyond a gradient:** discrete
- **Share of the grouping explained by lineage:** 0.334; gate at 0.50
- **Claim:** level 4, archetype candidate

*Figure 1 (drawn on the page).* The claim ladder. The run reaches the highest rung its gates allow; a closed gate holds it there and is named. Level 4 is reached only when every applicable gate passes, and is a candidate status, not biological confirmation.

**Gates.** 0 of 8 applicable conditions closed on this run. A closed gate is a result, not an error: it says the collection cannot support the reading. No gate closed does not establish that the groups are biological types.

> **Not evaluated on this run, and why**
>
> Permutation null for the description length: not requested. The held-out test is the evidence for real structure.
>
> Interval on the share of the profile groups explained by lineage: not given, because the groups were re-fitted inside every cross-validation fold and a lineage drawn twice would train a group on rows that are also held out. The spread across repeated cross-validation is 0.008.
>
> Permutation test on layer contribution: skipped above 500 isolates, where it would cost as many network fusions as permutations times layers; the leave-one-layer-out influence in Table 6 was computed.
>

> **Interpretation (generated from the record by fixed rules)**
>
> The 6 groups recur on features held out of the clustering (p < 0.001 across all 50 checked split orderings).
>
> They are separated by gaps rather than cut from a gradient.
>
> Lineage explains 0.334 of the grouping, below the gate: the groups cut across lineages.
>
> These sentences follow from the record by fixed rules and carry no judgement beyond it.
>

## 2. Admissibility of the input

- **Lineage column:** `baps_cluster`
- **Binary layers:** ribo, cell
- **Distance:** jaccard (undefined pairs: identical)
- **Fusion:** similarity-network fusion, K=20, mu=0.5, T=20
- **Resampling:** 30 consensus, 200 bootstrap, 0 permutations

Empty cells in the binary layers: 0. Nothing was filled in.

Lineage groups in the input: 30, of which 3 hold a single isolate. Support 99.6 % against the 90.0 % the estimator needs: accepted.

**Table 1.** Conditions the diagnostics require before any result is reported.

| Condition | Observed | Required | Verdict |
|---|---:|---:|---|
| Lineage support | 99.6 % | ≥ 90.0 % | accepted |
| Lineage groups used | 30 of 30 | reported | accepted |
| Effective layers | 1.8 | > 1.5 | accepted |
| Split design | adequate | adequate | accepted |

## 3. Are there resistance-profile groups?

The selection procedure returned **6** profile groups. Tested on features held out of the clustering, the grouping reproduces at p < 0.001 across all 50 checked split orderings. The structure is separated by gaps rather than shading continuously from one type into the next (discrete).

The labels re-derived inside each split resemble the reported grouping at a median adjusted Rand index of 0.52 (range 0.21 to 0.68 over 25 splits), so the held-out evidence concerns this grouping.

*Figure 2 (drawn on the page).* Description length saved by describing the cohort as k archetypes rather than as one population. The turn in the curve, not a threshold, is what selects k.

**Table 2.** Evidence behind the number of groups.

| Quantity | Value | Reading |
|---|---:|---|
| Groups selected | 6 | by minimum description length |
| Description length saved | 1954 bits | 30.5 % of the null code |
| Permutation null for that gain | not run | a permutation null for the description length is optional and was not requested; the held-out test below is the evidence for real structure |
| Held-out reproducibility | p < 0.001 across all 50 checked split orderings | groups recur on features not used to form them |
| Continuum exceedances | 0 of 99 | upper limit of the exact binomial interval 0.0366 |
| Latent dimension of the null | 3 | chosen by information criterion, not pinned |

## 4. Could the grouping be an artefact of the panel?

A grouping can arise from the shape of the panel rather than from the isolates. Three things are checked per layer: how many isolates carry no informative feature at all, how many independent directions the layer really holds, and whether the nearest-neighbour cut that builds the affinity graph was decided by ties rather than by distance. A tie inflation of 1.00 means the cut was clean; a value above it means more neighbours were kept than asked for, because candidates shared the same affinity.

**Table 3.** Panel geometry, layer by layer.

| Layer | Features used | Effective dimension | Uninformative isolates | Tie inflation at the cut | Empty-stratum agreement |
|---|---:|---:|---:|---:|---:|
| ribo | 8 | 2.93 | 10.0 % | 7.619 | 0.107 |
| cell | 5 | 2.66 | 62.2 % | 14.141 | 0.174 |

The empty-stratum check compares the grouping with the isolates that carry nothing in one layer, and the largest group against the rest with the isolates that carry nothing in any layer. An agreement near one would mean the grouping is reproduced by absence alone. The largest group holds 207 isolates, of which 0.0 % carry no feature of any layer; its agreement with that indicator is -0.064. The largest value on this run is 0.174.

*Figure 3 (drawn on the page).* What each group is made of, by the layers its isolates carry. A group that is mostly the trait-absent stratum is an absence, not a profile; the number above each bar is the group's size.

## 5. Does the grouping beat a simpler rule?

A grouping that a single layer or a plain concatenation reproduces has not earned the fusion that produced it. Every candidate below was run through the same held-out test the reported grouping had to pass: its own pipeline on the discovery half of the feature blocks, scored on the held-out half. That test is the criterion that can rank candidates. The description length is computed in sample and favours a candidate fitted by likelihood on these same bits, so it is shown and decides nothing; agreement with an external labelling is shown as a paired difference from the reported grouping with its interval, so that "not distinguishable" is a possible answer.

**Table 4.** Candidate groupings. Held-out: the feature-split test on the candidate's own pipeline. Description length: in sample, descriptive only.

| Candidate | Groups | Held-out | Description length saved | Agreement with reported |
|---|---:|---:|---:|---:|
| fused snf | 6 | p < 0.001 | 1954 | 1.000 |
| concatenation | 6 | p < 0.001 | 2335 | 0.629 |
| solo ribo | 6 | p < 0.001 | 2035 | 0.725 |
| solo cell | 6 | p < 0.001 | 264 | 0.222 |
| bernoulli mixture | 6 | p < 0.001 | 2541 | 0.675 |

**Table 5.** Agreement with each external labelling, as the difference in adjusted Rand index between the candidate and the reported grouping on the same bootstrap resamples of isolates, with its 95 % interval. * marks a difference whose interval excludes zero; without it the two cannot be told apart by that labelling.

| Candidate | serovar | isolation country | collection year | host name | mlst |
|---|---:|---:|---:|---:|---:|
| concatenation | +0.023 * 0.001 to 0.044 | -0.023 * -0.034 to -0.014 | -0.014 * -0.025 to -0.005 | +0.003 -0.003 to 0.008 | +0.008 -0.023 to 0.036 |
| solo ribo | -0.015 * -0.029 to -0.004 | -0.005 -0.014 to 0.004 | -0.002 -0.012 to 0.007 | +0.005 * 0.000 to 0.011 | -0.040 * -0.056 to -0.023 |
| solo cell | +0.025 -0.005 to 0.046 | -0.020 -0.045 to 0.007 | -0.008 -0.025 to 0.004 | -0.036 * -0.053 to -0.021 | +0.015 -0.026 to 0.051 |
| bernoulli mixture | +0.019 * 0.003 to 0.037 | -0.008 -0.019 to 0.003 | -0.012 * -0.021 to -0.000 | +0.004 -0.003 to 0.010 | -0.005 -0.029 to 0.018 |

5 of 5 tested groupings reproduce on held-out features. The reported grouping is one of several admissible descriptions of this collection; the held-out test does not prefer one of them. The description length in sample is largest for bernoulli mixture, as is expected of a grouping fitted by likelihood on these bits; it does not say which grouping is real. Agreement with an external labelling differs distinguishably from the reported grouping for concatenation (lower on collection year, lower on isolation country, higher on serovar), solo ribo (higher on host name, lower on mlst, lower on serovar), solo cell (lower on host name) and bernoulli mixture (lower on collection year, higher on serovar). Whether higher agreement is a merit depends on the labelling: closer agreement with a lineage label means the groups are closer to being the lineages, which is the confounding the attribution measures, not a gain.

## 6. Which layer carries the grouping?

Layers contribute differently and jointly. The effective number of layers is 1.77 of 2, and the layer that moves the answer most is **ribo**. A layer marked inert can be removed without changing the grouping.

*Figure 4 (drawn on the page).* Weight each layer carries in the fused network. A layer drawn in the warning colour is inert: the grouping does not change when it is removed.

**Table 6.** What each layer contributes.

| Layer | Weight | Loss when removed | Agreement alone with the fused grouping | Inert |
|---|---:|---:|---:|---|
| ribo | 0.743 | 0.778 | 0.725 | no |
| cell | 0.257 | 0.269 | 0.222 | no |

Mean disagreement between layers, taken over layer pairs only, is 0.679.

## 7. How stable is the grouping?

**Table 7.** Behaviour under resampling and under removal.

| Quantity | Value | Reading |
|---|---:|---|
| Proportion of ambiguous pairs | 0.170 | share of pairs that neither always nor never co-cluster across consensus draws; zero is a clean split |
| Area under the consensus distribution | 0.785 | a flat consensus matrix drives this towards one |
| Largest isolate fragility | 0.846 | how far one isolate can move the grouping |
| Largest feature fragility | 0.490 | how far one feature can move the grouping |
| Label recovery from half the features | 0.650 | recovery of the pipeline's own labels from half the features; internal coherence, not external predictive validity |

## 8. What may be concluded, and what may not

The highest claim the profile-group diagnostics carry is **level 4**, archetype candidate. That level attests reproducible structure in the reported grouping; it does not say that the reported grouping is the best of the candidates in Table 4, which is a separate question answered there. Every gate was evaluated; the margin is the distance the run had left before the gate would have closed.

*Figure 5 (drawn on the page).* Distance to failure for each gate that carries a numeric margin. A short bar is a result that only just holds.

**Table 8.** Gate ledger. Every gate is listed, including those that did not fire.

| Gate | Applicable | Closed | Observed | Threshold |
|---|---|---|---|---|
| k selection | yes | no | selected k 6; top of sweep 10 | optimum inside the swept range |
| fusion collapse | yes | no | 1.768 | 1.500 |
| empty stratum | yes | no | 0.174 | 0.500 |
| post clustering inference | yes | no | ok | status is ok |
| split design | yes | no | yes | adequate is true |
| lineage support | yes | no | 0.996 | 0.900 |
| lineage confounding | yes | no | lineage attributable share 0.334; ci95 not computed (+7 more in the record) | lineage attributable share below 0.500 |
| phenotype superiority | no | no | rules beating partition none; worst ci95 low minus partition not computed | no tested simple rule has bootstrap CI95 low > 0 |
| continuum discreteness | yes | no | status ok; p value 0.010 (+1 more in the record) | status is ok and p value < 0.05 |

## 9. Provenance and terms

- **Software:** amr-archetypes 1.0.0, record schema 1.0
- **Seed:** 42
- **Configuration:** `sha256:d52a0f5c7b4c`
- **Record:** `sha256:3fa88a4ef2ed7ba56d1ebc81958be3c8881baf444c3efb1045f7ed94d89ee6fe`

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

amr-archetypes 1.0.0 · record schema 1.0 · seed 42 · configuration sha256:d52a0f5c7b4c
Cite this run as: “amr-archetypes 1.0.0, run A06124B1, 2026-09-10T20:31Z.”
This report supersedes any earlier report bearing the same run identifier. It is regenerated from the record and holds no value that the record does not. The symbols carry the same wording in every run of this software; no symbol against a value means only that none of the listed conditions fired. Intervals are printed as computed, without clipping to the natural bounds of the quantity; clipping would leave their coverage unchanged and is left to the reader so that widths stay comparable across runs.
