# API reference

The public surface is the modules listed in `amr_archetypes.__all__`,
each loaded on first use. Everything below is read from the docstrings in the
source, so the reference and the code cannot disagree. Names that begin with
an underscore are internal and are not documented here.

## Partition diagnostics

The lineage-attributable share of a partition, and the share each trait
carries on its own, are computed by `amr_archetypes.attribution` and reported
in the record under `lineage_attribution` and `clonal_share`.

::: amr_archetypes.attribution
    options:
      members:
        - attribute_partition
        - concordance_z
        - clonal_share
        - layer_clonal_share
        - AttributionResult
        - ShareResult


### inference

::: amr_archetypes.inference
    options:
      members:
        - feature_split_test
        - merge_pvalues
        - merge_order_sensitivity
        - correlation_blocks
        - continuum_null_test
        - select_latent_dimension
        - poisson_thin
        - nb_thin
        - binomial_thin
        - thinning_dependence

### influence

::: amr_archetypes.influence

### lineage

::: amr_archetypes.lineage

### tva

::: amr_archetypes.tva

### archephy

::: amr_archetypes.archephy
    options:
      members:
        - load_tree
        - fitch_change_edges
        - fitch_asr
        - joint_homoplasy_pvalue
        - archephy_cs_test

### baselines

::: amr_archetypes.baselines

## Running a configuration

::: amr_archetypes.core
    options:
      members:
        - run
        - validate

::: amr_archetypes.config
    options:
      members:
        - load_config
        - Config
        - ConfigError
