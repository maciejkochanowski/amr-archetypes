"""Every shipped record renders a report that asserts nothing the record lacks.

The report was written beside one cohort. Rendering it against every record
the package ships, and against the branches those records do not reach, is
what catches a sentence that prints a placeholder where a value should be,
a count of zero out of zero, or an instruction meant for the developer. The
forbidden strings below are the ones that have appeared in a rendered report
at some point and should not again.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from amr_archetypes.cli import _summary
from amr_archetypes.report import render_report
from amr_archetypes.report_html import render_html_report

ROOT = Path(__file__).resolve().parents[1]
RECORDS = sorted(ROOT.glob("examples/*/expected*/cluster_result.json"))
if (ROOT / "out_ssuis" / "cluster_result.json").is_file():
    RECORDS.append(ROOT / "out_ssuis" / "cluster_result.json")

FORBIDDEN = (
    r"\bNone\b", r"\bnan\b", r"\bNaN\b", r"\[\]", r"\b0 of the 0\b",
    r"\b0 of 0\b", r"result\[", r"run\(\.\.\.", r"n_perm=", r"\bO\(n",
    r"ari_vs_fused", r"external_agreement", r"mdl_gain",
    r"metadata_diagnostics\.", r"not computed to not computed",
)


@pytest.mark.parametrize("path", RECORDS, ids=[p.parent.name for p in RECORDS])
def test_the_report_never_prints_a_placeholder_or_developer_text(path):
    record = json.loads(path.read_text(encoding="utf-8"))
    summary = _summary(record)
    md = render_report(record, summary, record_bytes=path.read_bytes())
    html = render_html_report(record, summary, record_bytes=path.read_bytes())
    text = re.sub(r"<[^>]+>", " ", html)
    for form, body in (("markdown", md), ("html", text)):
        for pat in FORBIDDEN:
            hits = [m.group(0) for m in re.finditer(pat, body)]
            assert not hits, f"{form} report of {path.parent.name}: {pat} -> {hits[:3]}"


def test_the_empty_record_renders_without_asserting_anything():
    record = {"layers": [], "n_isolates": 0, "seed": 0, "selected_k": 1}
    summary = _summary(record)
    for body in (render_report(record, summary),
                 re.sub(r"<[^>]+>", " ", render_html_report(record, summary))):
        assert "no lineage column" in body
        for pat in FORBIDDEN:
            assert not re.search(pat, body), pat
