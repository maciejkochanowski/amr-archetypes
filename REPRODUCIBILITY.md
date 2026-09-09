# Reproducing the reported numbers

Three files carry three different claims and they are deliberately not merged.

`pyproject.toml` states the versions the package supports. It uses ranges,
because a user installing the tool should not be forced onto one stack.

`uv.lock` and `requirements-lock.txt` state the versions that produced the
numbers in the article. `requirements-lock.txt` is an exact pin list read
from the installed distribution metadata of the environment that ran them, for
readers who do not use the uv toolchain.

`Dockerfile` builds that environment from the pin list on a pinned Python base
image. A difference between a rerun inside the image and a number in the paper
is therefore a difference in the work rather than in the stack.

## The two stacks the results were computed on

Every result was produced on one of two environments and each artefact records
which, in its own provenance block.

| | interpreter | numpy | scipy | pandas |
|---|---|---|---|---|
| workstation | 3.12.13 | 2.5.2 | 1.18.1 | 3.0.5 |
| cluster | 3.11.16 | 2.4.6 | 1.17.1 | 3.0.5 |

Running the same analysis on two stacks is not redundancy. A failure that
appears on one and not on the other is an artefact of the machine, and
reporting such an artefact as a defect of the work is the most damaging error
available in an audit.

## Seeds

Every stochastic component is seeded and the seed is written into the
artefact. The master seed of a run is `--seed`, 42 by default, and every
stage draws from its own generator spawned off it, so adding a diagnostic
cannot perturb the clustering. The shipped expected records under
`examples/*/expected*` were produced at seed 42 on the workstation stack.

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
