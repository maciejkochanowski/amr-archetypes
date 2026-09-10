# 5. Read the results

Start with `report.md`. It has the same nine sections on every run, in the
same order, and the first page is meant to be read on its own: the question
asked, the grouping the run returned with the tests it passed, the share of it
that lineage explains, the gates that fired, what was not evaluated on this
run and why, and an interpretation generated from the record by fixed rules.
Everything after the first page defends it. Both forms of the report,
`report.md` and `report.html`, are rendered from one
structure, read every value from `cluster_result.json` and `summary.json`, and
recompute nothing; the page carries the record's SHA-256 so a report can be
matched to the record it came from. Then open `summary.json` for the
machine-readable digest, and `cluster_result.json` only when a specific number
has to be traced.

![The run report on the planted control](../img/05_report.png)

## The sections of the report

**1. Measurement summary.** The question asked, the number of groups, whether
they recur on held-out traits and are discrete, the share of the grouping that
lineage explains against its gate, the claim level, the gates that fired, what
was not evaluated on this run with the reason, and the interpretation the
fixed rules draw from the record. This is the page a reader stops at.

**2. Admissibility of the input.** The lineage column and its resolution, the
layers, the settings that shape the grouping, the input check, and the
conditions the diagnostics require before a result is reported, each with its
observed value, its threshold and a verdict.

**3. Are there resistance-profile groups?** The number of groups selected, the
description-length curve, and whether the groups reproduce on traits held out
of the clustering and are separated by gaps or sit on a gradient. One group is
a result, not a failure, and the report says so.

**4. Could the grouping be an artefact of the panel?** Effective dimension per
layer, tie inflation, the empty-stratum check.

**5. Does the grouping beat a simpler rule?** Every candidate partition
(concatenation, each layer alone, a Bernoulli mixture) put through the same
held-out test as the reported grouping, its in-sample description length, and
its agreement with the reported grouping; then, where external labels exist,
the paired difference in agreement against each label with a bootstrap
interval. Higher agreement with a lineage label is confounding, not merit, so
the section reports the differences and does not rank.

**6. Which layer carries the grouping?** Weights in the fused network and
the loss when each layer is removed.

**7. How stable is the grouping?** Ambiguous pairs, fragility, label
recovery from half the features.

**8. What may be concluded, and what may not.** The highest claim the
diagnostics support, the distance of each gate from its threshold, the
diagnostic failures if any, and the gate ledger. A gate is not an error; it
marks a reading the data cannot support, and the record keeps the numbers
behind it.

**9. Provenance and terms.** Software, seed, configuration and record
digests, and the terms used, defined once.

## summary.json

The digest a script reads. The fields that decide the reading:

| field | meaning |
|---|---|
| `selected_k`, `k_at_sweep_boundary` | number of profile groups; `1` with `no_structure: true` is the null result; `k_at_sweep_boundary: true` means the description length was still rising at the top of `k_range`, the number is not identified and the `k_selection` gate closes |
| `inference_status` | `ok`, or `withheld_inadequate_split_design` when the panel cannot be split into training and test halves |
| `structure_detected`, `p_value_structure_report` | whether the groups reproduce on held-out traits |
| `discreteness_verdict`, `discrete_beyond_a_gradient` | gaps between groups, or a gradient |
| `lineage_attributable_share`, `..._ci95` | share of the grouping explained by lineage, with interval |
| `lineage_attribution_support`, `lineage_attribution_estimable` | share of isolates in lineages of at least two members; below 0.90 the share is reported without a verdict and the `lineage_support` gate closes |
| `lineage_confounded` | `true` when that share reaches the gate: read the groups as lineages; `null` when the share is not estimable |
| `clonal_share_all_features` | out-of-sample lineage share of the clustering traits taken together |
| `claim_level`, `active_gate_codes` | the claim ladder and the gates that limit it |

## cluster_result.json

The full record: the configuration as run, every diagnostic with its inputs,
the lineage attribution of the partition
(`metadata_diagnostics.lineage_attribution`), the lineage share of every
clustering trait (`metadata_diagnostics.clonal_share`), and the provenance.
It is strict JSON: no `NaN`, no `Infinity`, so any parser reads it.

## assignment.tsv and archetype_profiles.tsv

The group of each isolate with its assignment confidence and stability label,
and the trait profile of each group with the traits that define it after
false-discovery control.
