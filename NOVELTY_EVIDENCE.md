# Novelty evidence

This file supports the priority words used in the article and in the source
docstrings. Each claim names the evidence behind it. The two claims below
concern the gate a partition of resistance profiles is held to; they were
first recorded, with the literature search behind them, in the evidence file
of `amr-clonalshare`, which implements the estimator the gate rests on, and
they are carried here because the gate is this package's.

## Claim 1

> A pass-or-fail gate built on a same-lineage pair co-assignment permutation
> test cannot fail on a cohort large enough to be worth analysing, because the
> statistic is computed over O(n^2) pairs while the structure it measures is
> not a function of n.

**Evidence, and the part of the claim that was withdrawn.** The sample
dependence of pairwise co-assignment statistics is documented, and an earlier
draft of the article that called it unnamed was wrong. Pinto, Melo-Cristino and
Ramirez (PLoS ONE 2008;3:e3696) state the sample dependence of the Wallace
coefficient and propose a confidence interval and an independence baseline;
Severiano, Pinto, Ramirez and Carrico (J Clin Microbiol 2011;49:3997) add the
adjusted coefficient with intervals; Kelly and colleagues (Bioinformatics
2015;31:2461) build a power and sample-size framework for permutation tests on
pairwise distances. Harmon and Glor (Evolution 2010;64:2173) and Guillot and
Rousset (Methods Ecol Evol 2013;4:336) make the general point for
distance-matrix permutation tests.

What no located paper does is apply the critique to such a test used as a
**gate** on a candidate trait partition, or state the O(n^2) pair-count framing
in these terms. The article claims that and nothing more, and quotes the
subsampling series that measures it on the shipped cohort (`benchmarks/subsample_series.py`): z = 3.4, 7.4, 12.2, 18.0, 21.1 at n = 67, 135, 270, 473, 677, against an attributable share of 0.268, 0.310, 0.340, 0.358, 0.349 on the same partition and the same labels, the partition held fixed.

## Claim 2

> The two-player Shapley decomposition of the variance-explained game against a
> lineage label has not been applied in bacterial population genomics.

**Evidence, and the part of the claim that was withdrawn.** Dividing bacterial
phenotype variance between lineage and other effects is established and an
earlier draft that implied otherwise was wrong. Lees and colleagues (eLife
2017;6:e26255) partition pneumococcal carriage duration into genomic variation,
serotype, drug resistance and other locus effects with numbers attached, and
MacFadden and colleagues (J Clin Microbiol 2019;57:e01780-18) compare
sequence-type-only against resistance-locus prediction. What was not located is
the Shapley form of that split, which is what the article claims, together with
its application to a routine susceptibility panel and its use as a magnitude
where a significance test stood.

A terminology collision is pre-empted on first use rather than left to a
reader: the Shapley value already names a diversity index on phylogenies
equivalent to Fair Proportion (Haake, Kashiwada and Su, J Math Biol
2008;56:479). The game decomposed here is the variance explained, not the tree.
These are also not SHAP attributions, which are Shapley values of a prediction
with respect to input features.

## What is not claimed

The article does not claim novelty for similarity network fusion, consensus
clustering, post-clustering selective inference, latent-trait modelling, or
any component of the diagnostic pipeline, all of which are cited to their
sources. The contribution claimed is the gate: that a partition of resistance
profiles is held to a magnitude that does not grow with the cohort, and that
the magnitude is the two-player Shapley split of the variance-explained game
against the lineage label.
