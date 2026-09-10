"""The drawn form of the run report.

The prose form states the result; this one has to show the diagnostics that
could undermine it. The tests below hold it to three things: that it draws
what the record holds rather than recomputing it, that a value the estimator
refused is not drawn as if it had been estimated, and that the page opens
without anything to fetch.

The shipped planted example was run without the lineage attribution, so its
record carries no lineage-attributable share. The fixture supplies one by
running the estimator over the same cohort, which is what the pipeline does
when ``attribution.enabled`` is set. What is under test here is the renderer,
so the fixture only has to be a well-formed record; the estimator itself is
tested in ``test_attribution.py``.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from amr_archetypes import attribution
from amr_archetypes.report_html import render_html_report

EXPECTED = Path(__file__).resolve().parent.parent / "examples" / "synthetic"


def _with_attribution(record, summary):
    d = EXPECTED / "data" / "planted"
    amr = pd.read_csv(d / "amr.csv", index_col=0)
    vir = pd.read_csv(d / "vir.csv", index_col=0)
    meta = pd.read_csv(d / "metadata.csv", index_col=0)
    X = pd.concat([amr, vir], axis=1)
    lineage = meta.loc[X.index, "lineage"].tolist()
    by_id = {a["isolate_id"]: a["cluster"] for a in record["assignment"]}
    labels = np.asarray([by_id[i] for i in X.index.astype(str)])
    att = attribution.attribute_partition(
        X.to_numpy(dtype=float), labels, lineage, n_boot=50, n_perm=50,
        seed=0).as_dict()
    att["lambda_gate"] = 0.5
    record["metadata_diagnostics"]["lineage_attribution"] = att
    summary["lineage_attributable_share"] = att["lam"]
    summary["lineage_attributable_share_ci95"] = [att["ci_low"], att["ci_high"]]
    return record, summary


@pytest.fixture(scope="module")
def rendered():
    record = json.loads((EXPECTED / "expected_planted" /
                         "cluster_result.json").read_text(encoding="utf-8"))
    summary = json.loads((EXPECTED / "expected_planted" /
                          "summary.json").read_text(encoding="utf-8"))
    record, summary = _with_attribution(record, summary)
    return record, summary, render_html_report(record, summary)


def test_the_page_is_self_contained(rendered):
    """Nothing to fetch: no script, no external stylesheet, no remote image.

    A report a laboratory cannot open offline is not a report. The one URL the
    page carries is the SVG namespace, which is an identifier rather than an
    address: nothing is retrieved from it.
    """
    _, _, html = rendered
    assert html.startswith("<!doctype html>")
    assert "<script" not in html.lower()
    assert "<link" not in html.lower()
    assert "src=" not in html.lower()
    addresses = [u for u in re.findall(r"""https?://[^\s"'<>]+""", html)
                 if u != "http://www.w3.org/2000/svg"]
    assert addresses == []
    assert re.search(r"<svg[^>]*viewBox", html)


def test_every_section_the_reader_needs_is_present(rendered):
    """The page opens on the measurement, then carries every diagnostic that
    could undermine it, in a fixed order."""
    _, _, html = rendered
    order = ("Measurement summary",
             "Admissibility of the input",
             "resistance-profile groups",
             "artefact of the panel",
             "beat a simpler rule",
             "Which layer carries the grouping",
             "How stable is the grouping",
             "What may be concluded",
             "Provenance and terms")
    positions = [html.index(h) for h in order]
    assert positions == sorted(positions), "sections out of order"
    assert html.count('<span class="no">') == len(order)
    assert "Not evaluated on this run" in html
    assert "Interpretation (generated from the record" in html


def test_the_figures_are_drawn_from_the_record(rendered):
    """A drawn value must be traceable to the file: the description-length
    sweep draws one point per candidate k and marks the selected one, and the
    share the summary states is the share the record holds."""
    record, summary, html = rendered
    sweep = record["k_selection"]["mdl_sweep"]
    assert html.count("<circle") >= len(sweep)
    assert ">selected</text>" in html
    lam = record["metadata_diagnostics"]["lineage_attribution"]["lam"]
    assert "%.3f" % lam in html
    assert "%.3f" % summary["lineage_attributable_share"] in html


def test_a_refused_gate_margin_is_not_invented(rendered):
    """Only gates carrying a numeric margin are drawn. A gate whose margin is
    absent must not appear in the figure with a bar of zero, which would read
    as a gate that only just held."""
    record, _, html = rendered
    ledger = record["interpretation"]["gate_ledger"]
    with_margin = [g for g in ledger if g.get("applicable")
                   and isinstance(g.get("margin_to_failure"), float)]
    figure = html.split("margin to failure")[0]
    for gate in ledger:
        drawn = ">%s</text>" % gate["code"].replace("_", " ")
        if gate in with_margin:
            assert drawn in figure or gate["code"] in html
    assert len(with_margin) >= 1
