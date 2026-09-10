"""Properties the arithmetic must satisfy for every input, not for the inputs
someone thought of.

Each test states an identity or an order relation and lets Hypothesis search
for a counterexample. Where the property is an equation, the right-hand side
is computed in exact rational arithmetic with :mod:`fractions`, so the test is
an oracle rather than a second copy of the floating-point code. Where the
property is a bound or a monotonicity, the check is exact by construction.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from math import comb

from hypothesis import given, settings
from hypothesis import strategies as st

from amr_archetypes.archephy import _exact_upper_tail
from amr_archetypes.inference import merge_pvalues

_pfamily = st.lists(st.integers(0, 1000).map(lambda k: Fraction(k, 1000)),
                    min_size=1, max_size=40)


# --------------------------------------------------------------------------- #
# Merging exchangeable p-values
# --------------------------------------------------------------------------- #

@given(st.lists(st.floats(0.0, 1.0), min_size=1, max_size=25),
       st.sampled_from(["ruger", "twice_mean", "mmb"]))
def test_symmetric_merges_are_probabilities_and_ignore_the_order(ps, how):
    merged = merge_pvalues(ps, how=how)
    assert 0.0 <= merged <= 1.0
    # Reversing the order changes the order of a floating-point sum, so the
    # comparison allows the rounding that a sum in another order carries.
    assert abs(merge_pvalues(list(reversed(ps)), how=how) - merged) < 1e-12


@given(st.lists(st.floats(0.0, 1.0), min_size=1, max_size=25))
def test_exchangeable_ruger_never_exceeds_the_plain_ruger_merge(ps):
    """The exchangeable rule takes the best prefix of the given order and the
    full family is one of those prefixes, so it can only come out at or below
    the plain rule. It is order-dependent on purpose, which is why the package
    reports its order sensitivity separately rather than hiding it."""
    merged = merge_pvalues(ps, how="exchangeable_ruger")
    assert 0.0 <= merged <= merge_pvalues(ps, how="ruger") + 1e-12


@given(st.lists(st.integers(0, 1000).map(lambda k: Fraction(k, 1000)),
                min_size=1, max_size=25))
def test_twice_the_mean_is_twice_the_mean(ps):
    merged = merge_pvalues([float(p) for p in ps], how="twice_mean")
    exact = min(Fraction(1), 2 * sum(ps) / len(ps))
    assert abs(merged - float(exact)) < 1e-12


# --------------------------------------------------------------------------- #
# Joint homoplasy tail: inclusion-exclusion against brute-force enumeration
# --------------------------------------------------------------------------- #

def _tail_by_enumeration(E, c, m):
    """P(M >= m) where trait t places c_t changes on distinct edges chosen
    uniformly among the E, independently across traits, and M counts the
    edges every trait hit. Every placement is enumerated, so the answer is
    an exact rational."""
    edges = range(E)
    hits = Fraction(0)
    total = 1
    for ct in c:
        total *= comb(E, ct)

    def rec(t, common):
        nonlocal hits
        if t == len(c):
            if len(common) >= m:
                hits += 1
            return
        for s in combinations(edges, c[t]):
            rec(t + 1, common & set(s))
    rec(0, set(edges))
    return hits / total


@given(st.integers(1, 5).flatmap(
    lambda E: st.tuples(st.just(E),
                        st.lists(st.integers(0, E), min_size=2, max_size=3),
                        st.integers(1, E))))
@settings(max_examples=60, deadline=None)
def test_exact_upper_tail_agrees_with_enumeration(Ecm):
    E, c, m = Ecm
    expected = _tail_by_enumeration(E, c, m)
    assert abs(_exact_upper_tail(E, c, m) - float(expected)) < 1e-12


@given(st.integers(1, 30).flatmap(
    lambda E: st.tuples(st.just(E), st.lists(st.integers(0, E),
                                             min_size=2, max_size=4))))
def test_exact_upper_tail_is_a_survival_function(Ec):
    E, c = Ec
    assert _exact_upper_tail(E, c, 0) == 1.0
    prev = 1.0
    for m in range(1, E + 2):
        cur = _exact_upper_tail(E, c, m)
        assert 0.0 <= cur <= prev
        prev = cur
