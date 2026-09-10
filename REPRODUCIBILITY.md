# Reproducing the reported numbers

Three files carry three different claims and they are deliberately not merged.

`pyproject.toml` states the versions the package supports. It uses ranges,
because a user installing the tool should not be forced onto one stack.

`requirements-lock.txt` states the versions that produced the shipped records
and the numbers in the article: an exact pin list read from the installed
distribution metadata of the environment that ran them (Python 3.11.15). `uv.lock`
is the resolver lock for developers who use the uv toolchain; it pins a
consistent development environment across the supported range and is not the
record of what produced the numbers.

`Dockerfile` builds that environment from the pin list on a pinned Python base
image. A difference between a rerun inside the image and a number in the paper
is therefore a difference in the work rather than in the stack.

## The two stacks the results were computed on

The shipped records and the cross-stack pairs were produced on one of two
environments. Every `cluster_result.json` names its own in a `provenance`
block (software version, interpreter and library versions, and the SHA-256 of
each input file); the older benchmark artefacts under `benchmarks/` carry an
`environment` field of their own.

| | interpreter | numpy | scipy | pandas |
|---|---|---|---|---|
| stack A, pinned by `requirements-lock.txt` and the `Dockerfile` | 3.11.15 | 2.4.6 | 1.17.1 | 3.0.5 |
| stack B | 3.12.13 | 2.5.3 | 1.18.1 | 3.0.5 |

Running the same analysis on two stacks is not redundancy. A failure that
appears on one and not on the other is an artefact of the machine, and
reporting such an artefact as a defect of the work is the most damaging error
available in an audit.

## Seeds

Every stochastic component is seeded and the seed is written into the
artefact. The master seed of a run is `--seed`, 42 by default, and every
stage draws from its own generator spawned off it, so adding a diagnostic
cannot perturb the clustering. The shipped expected records under
`examples/*/expected*` were produced at seed 42 on stack A. The same six
configurations run on stack B returned the same number of groups, the same
group for every isolate, the same claim level and the same closed gates on
every run; the records are not byte-identical, because floating-point sums
differ in their last digits between library versions and the seeded Monte
Carlo stages then diverge slightly (λ on the *Klebsiella* cohort reads 0.457
on stack B against 0.456 on stack A). The paired records are deposited with
the article's evidence.

## Building and running

    docker build -t amr-archetypes:1.0.0 .
    docker run --rm amr-archetypes:1.0.0

    # or, without a container
    python -m venv .venv && . .venv/bin/activate
    pip install -r requirements-lock.txt
    pip install --no-deps .

## Which artefact is the code of this release

Three things carry the version 1.0.0 and one of them is authoritative. The git
tag `v1.0.0` is the source of the release; the Zenodo record archives the tag
as it stands and is the record to cite for a reproduction; the wheel
published on PyPI is built from the tag and is byte-identical to it module
for module.
