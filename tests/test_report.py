"""The run report is rendered from the record, in a fixed order, with nothing invented.

The shipped *S. suis* record is the real case; synthetic records exercise the
branches the shipped run does not reach (no structure, withheld inference,
no lineage column, gates tripped). Both forms of the report are built from
one structure, so what is asserted of the prose form here holds of the page.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from amr_archetypes.cli import _gates, _summary
from amr_archetypes.report import render_report
from amr_archetypes.report_html import render_html_report

ROOT = Path(__file__).resolve().parents[1]
SSUIS = ROOT / "examples" / "ssuis" / "expected" / "cluster_result.json"


@pytest.fixture(scope="module")
def ssuis():
    if not SSUIS.is_file():
        pytest.skip("shipped S. suis record not present")
    return json.loads(SSUIS.read_text(encoding="utf-8"))


def _sections(text):
    return [line[3:] for line in text.splitlines() if line.startswith("## ")]


def test_every_number_in_the_ssuis_report_is_read_from_the_record(ssuis):
    text = render_report(ssuis, _summary(ssuis))
    heads = _sections(text)
    assert heads[0].endswith("Measurement summary")
    assert heads[1].endswith("Admissibility of the input")
    assert "What may be concluded" in heads[-3] and heads[-2].endswith("Provenance and terms")
    assert f"**Isolates:** {ssuis['n_isolates']}" in text
    assert f"returned **{ssuis['selected_k']}** profile groups" in text
    lam = ssuis["metadata_diagnostics"]["lineage_attribution"]["lam"]
    assert f"{lam:.3f}" in text


def test_the_no_structure_branch_and_the_absent_lineage_branch():
    result = {"layers": ["amr"], "n_isolates": 12, "seed": 1, "selected_k": 1,
              "k_selection": {"no_structure": True}}
    text = render_report(result, _summary(result))
    assert "This is a result, not a failure" in text
    assert "no lineage column was given" in text
    assert "No gate applied on this run" in text
    assert "No input check was attached" in text
    import re
    assert not re.search(r"\bNone\b|\bnan\b", text)


def test_the_withheld_and_confounded_branches_with_an_input_record():
    result = {"layers": ["amr", "vir"], "n_isolates": 50, "seed": 2, "selected_k": 3,
              "provenance": {"version": "1.0.0"},
              "post_clustering_inference": {"status": "withheld_inadequate_split_design"},
              "metadata_diagnostics": {
                  "lineage_attribution": {"lam": 0.8, "ci_low": 0.4, "ci_high": 0.9,
                                          "lambda_gate": 0.5},
                  "clonal_share": {f"t{i}": {"kappa_adj": i / 20, "ci_low": 0.0,
                                             "ci_high": 1.0, "support": 0.95,
                                             "estimable": True}
                                   for i in range(15)}},
              "interpretation": {"claim_level": "descriptive",
                                 "active_gate_codes": ["G1"]}}
    qc = {"missing": {"policy": "drop_rows", "layers": {"amr": {"cells": 3}}},
          "lineage": {"n_groups": 4, "n_singletons": 1, "support": 0.5,
                      "support_threshold": 0.9, "estimable": False}}
    text = render_report(result, _summary(result), input_qc=qc,
                         problems=["fusion collapsed"])
    assert "could not be tested" in text
    assert "at or above the gate" in text
    assert "Empty cells in the binary layers: 3, handled by the policy `drop_rows`" in text
    assert "not accepted at this typing resolution" in text
    assert "Diagnostic failure:** fusion collapsed" in text


def test_the_reproducible_and_discrete_branch():
    result = {"layers": ["amr"], "n_isolates": 80, "seed": 3, "selected_k": 2,
              "post_clustering_inference": {"status": "ok", "structure_detected": True,
                                            "p_value_structure": 0.0001,
                                            "discreteness": {"verdict": "discrete",
                                                             "discrete_beyond_a_gradient": True}},
              "metadata_diagnostics": {
                  "lineage_attribution": {"lam": 0.2, "ci_low": 0.1, "ci_high": 0.3,
                                          "lambda_gate": 0.5},
                  "clonal_share_by_layer": {"all_clustering_features": {"kappa_adj": 0.31}}}}
    text = render_report(result, _summary(result))
    assert "reproduces at p < 0.001" in text
    assert "separated by gaps" in text
    assert "0.200 (95 % interval 0.100 to 0.300); gate at 0.50" in text
    assert "the groups cut across lineages" in text
    # the gradient branch
    result["post_clustering_inference"]["discreteness"]["verdict"] = None
    result["post_clustering_inference"]["discreteness"]["discrete_beyond_a_gradient"] = False
    assert "sit on a gradient" in render_report(result, _summary(result))


def test_a_refit_partition_explains_its_missing_interval_and_gates_survive_null():
    result = {"layers": ["amr"], "n_isolates": 200, "seed": 4, "selected_k": 3,
              "metadata_diagnostics": {
                  "lineage_attribution": {"lam": 0.99, "ci_low": None, "ci_high": None,
                                          "lambda_gate": 0.5, "partition_refit": True,
                                          "lam_cv_sd": 0.0006}}}
    problems = _gates(result)  # a JSON round-trip leaves null where NaN was
    assert problems and "nan to nan" in problems[0]
    text = render_report(result, _summary(result), problems=problems)
    assert "not computed to not computed" not in text
    assert "re-fitted inside every cross-validation fold" in text and "0.001" in text


def test_formatting_never_invents_a_number():
    from amr_archetypes.report import _f, _pct
    from amr_archetypes.report_model import interval
    assert _f(None) == "not computed" and _f(float("nan")) == "not computed"
    assert _f("withheld") == "withheld" and _f(0.12345) == "0.123"
    assert _pct(None) == "not computed" and _pct(0.5) == "50.0 %"
    assert interval(None, 0.2) == "not computed"


def test_both_forms_are_built_from_one_structure():
    """A number in one form is in the other, and both carry the record digest."""
    result = {"layers": ["amr"], "n_isolates": 80, "seed": 3, "selected_k": 2,
              "metadata_diagnostics": {
                  "lineage_attribution": {"lam": 0.31, "ci_low": 0.2, "ci_high": 0.4,
                                          "lambda_gate": 0.5}}}
    raw = json.dumps(result).encode()
    md = render_report(result, _summary(result), record_bytes=raw)
    html = render_html_report(result, _summary(result), record_bytes=raw)
    import hashlib
    digest = hashlib.sha256(raw).hexdigest()
    assert digest in md and digest in html
    assert "0.310" in md and "0.310" in html
    assert "0.200 to 0.400" in md and "0.200 to 0.400" in html


def test_the_split_labels_are_compared_with_the_reported_grouping(ssuis):
    """The held-out p-value is about the reported grouping only when the labels
    re-derived inside each split resemble it; the record carries the median
    ARI and the verdict, and the page must print both beside the p-value."""
    pci = ssuis["post_clustering_inference"]
    ari = pci["ari_discovery_vs_reported"]
    text = render_report(ssuis, _summary(ssuis))
    assert f"median adjusted Rand index of {ari['median']:.2f}" in text
    if pci["concerns_reported_partition"]:
        assert "concerns this grouping" in text
    else:
        assert "one description of it rather than the one the test confirmed" in text
    # the continuum denominator is the bootstrap count of the continuum test,
    # not the consensus bootstrap of the run
    disc = pci["discreteness"]
    assert f"{disc['bootstrap_exceedances']} of {disc['n_boot']}" in text
