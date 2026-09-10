# 3. Check the input

Before any estimate, run the input check alone:

```bash
amr-archetypes --config config.yaml --results-dir out --check-input
```

It loads every layer, applies the missing-value policy, refuses anything that
is not 0 or 1, joins the metadata, and prints a plain-language summary. The
same summary is written to `out/input_qc.md`, with the full record in
`out/input_qc.json`. The full run performs the same step first, so nothing
here is skipped by going straight to the run; the flag only lets you read the
verdict before spending compute.

![The input check on the planted control](../img/03_check_input.png)

## What it reports

**Empty cells.** How many, in which rows and columns, and what the policy did
with them. Nothing is ever filled in.

**Values other than 0 and 1.** Listed with their counts. The run refuses them.

**Per trait: the count of the rarer outcome.** A trait present in 3 isolates of
500, or absent in 3, has three observations that can inform the question. The
tool reports how many traits reach the project's threshold of 20. Below it the
estimate is still computed, and its interval will show how little it rests on.

**Per lineage: the group sizes and the estimator's verdict.** A lineage with a
single isolate carries one outcome and cannot show how much the trait varies
inside it. The share of isolates in lineages of at least two members is the
*support*, and the lineage share that the lineage gate rests on is withheld
below 0.90, a threshold read off its measured coverage curve rather than
chosen. The check tells you before the run whether your lineage definition
clears it, and if not, that a coarser definition would.

## Is my collection large enough?

There is no single minimum. Two things bind, and the check reports both:

1. **the number of lineages with at least two isolates**, because they alone
   inform the within-lineage variation; and
2. **the count of the rarer outcome per trait**, because a trait nobody carries
   cannot inform a distance.

The held-out test that decides whether the groups are real needs traits it
can split into a training and a test half; a panel of a handful of traits is
refused for that test and the groups are reported as descriptive only.

## Exit codes of this step

`0` the input loaded and the summary was printed; `2` a file, a key, an empty
cell under the default policy or a non-binary value was refused, with one
sentence on standard error naming what and where.
