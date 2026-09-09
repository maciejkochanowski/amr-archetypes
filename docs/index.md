# amr-archetypes

A command-line tool that answers one question about a collection of bacterial
isolates typed for resistance determinants, virulence loci and other binary
traits: **are the recurring resistance profiles in it real types, or an
artefact, or the lineages under another name?**

The answer is a partition with a claim level, and around it the diagnostics
that decide what the partition may be called: whether the groups recur on
traits held out of the clustering, whether they are separated by gaps rather
than cut from a gradient, whether the largest group is the isolates that carry
nothing, whether one layer won the fusion, whether a different row order would
give a different answer, and how much of the grouping the lineage label
already explains. A gate that fails closes the run and says why.

## Who it is for

Laboratories and genomic-epidemiology groups that hold a typed collection with
one or more binary trait panels and want to know whether the profiles they see
recur for a reason the data can support. No statistics beyond reading an
interval is needed to use it; the run writes a report in plain language.

## Where to start

1. [Install](manual/01-install.md) with `pip` or run the container.
2. [Prepare the input](manual/02-input.md): one CSV per layer, one row per
   isolate, one column per trait, 0 or 1 in every cell, plus a metadata table
   with the lineage.
3. [Check the input](manual/03-check-input.md) before spending compute.
4. [Run](manual/04-run.md) and [read the results](manual/05-results.md).

## What the shipped controls show

The package ships a positive control (three planted archetypes), an independent
confirmation with a second seed, a negative control with no structure, and an
adversarial control where every difference is clonal. The first recovers the
planted truth, the second recovers it again, the third returns one group, the
fourth is flagged as lineage-confounded. These four runs are the first thing to
reproduce on a new machine; the [container page](manual/06-container.md) does
exactly that.
