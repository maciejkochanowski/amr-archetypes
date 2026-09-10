"""The run report as a structure, before it is a page.

WHY ONE MODEL. The package writes the report twice, as prose that diffs
cleanly between runs and as a page with the diagnostics drawn. Two writers
reading the same record drift apart: one grew an input-check section the other
never had. Building the report once, as sections of typed blocks, and rendering
that structure into each form means the two cannot disagree about what a run
found.

WHAT THE STRUCTURE IS SHAPED BY. A measurement report, not a pipeline log. The
first section states the question asked, the grouping the run returned with
the tests it passed and failed, the conditions the diagnostics required and
whether they held, and what the run did not evaluate. Everything after it is
the evidence, in the order a reader asks for it: is the input admissible, are
there groups and are they discrete, could they be an artefact of the panel, do
they beat a simpler rule, which layer carries them, how stable are they; then
the gates; then provenance.

WHAT IS NEVER DONE HERE. Nothing is estimated. Every value is read from the
record or from the summary the command line derived from it, and every rule
this module applies to those values is stated in the text it produces.
Interpretation is a separate block, labelled as such, generated from fixed
conditions on quantities the record already holds; it never introduces a
threshold the record does not carry.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

from . import __version__

__all__ = ["Report", "Section", "Block", "build_report"]

#: Short reader-facing names for the gate codes, used on the claim-ladder figure.
_GATE_LABEL = {
    "k_selection": "the number of groups",
    "fusion_collapse": "layer collapse",
    "empty_stratum": "the absence stratum",
    "post_clustering_inference": "the held-out test",
    "split_design": "the split design",
    "lineage_support": "lineage support",
    "lineage_confounding": "lineage relabelling",
    "phenotype_superiority": "a one-column rule",
    "continuum_discreteness": "the continuum test",
}


# ----------------------------------------------------------------- structure
@dataclass
class Block:
    """One unit of a section.

    ``kind`` is one of ``p`` (a paragraph; ``text``), ``kv`` (label and value
    pairs; ``rows``), ``table`` (``caption``, ``headers`` as (label, align)
    pairs with align in {lab, num, flag}, ``rows``), ``figure`` (``figure`` is
    a name the renderer knows, ``data`` its input, ``caption``), ``callout``
    (``title`` and ``lines``). Text carries two inline marks only:
    ``**bold**`` and ```code```.
    """
    kind: str
    text: str = ""
    title: str = ""
    caption: str = ""
    headers: List[Tuple[str, str]] = field(default_factory=list)
    rows: List[Sequence[Any]] = field(default_factory=list)
    figure: str = ""
    data: Any = None
    lines: List[str] = field(default_factory=list)
    label: str = ""


@dataclass
class Section:
    key: str
    title: str
    blocks: List[Block] = field(default_factory=list)
    part: str = ""

    def p(self, text: str) -> None:
        self.blocks.append(Block("p", text=text))

    def kv(self, rows) -> None:
        self.blocks.append(Block("kv", rows=list(rows)))

    def table(self, label, caption, headers, rows) -> None:
        self.blocks.append(Block("table", label=label, caption=caption,
                                 headers=list(headers), rows=list(rows)))

    def figure(self, label, name, data, caption) -> None:
        self.blocks.append(Block("figure", label=label, figure=name, data=data,
                                 caption=caption))

    def callout(self, title, lines) -> None:
        self.blocks.append(Block("callout", title=title, lines=list(lines)))


@dataclass
class Report:
    ident: Dict[str, str]
    status: Dict[str, Any]
    sections: List[Section]
    symbols: List[Tuple[str, str]]
    colophon: List[str]
    version: str = __version__


# ------------------------------------------------------------------ helpers

def _stack_line(prov: Dict[str, Any]) -> str:
    """One line naming the interpreter and libraries that produced the record,
    read from its ``provenance`` block; empty when the record has none."""
    if not prov.get("python"):
        return ""
    return ("Python %s, numpy %s, scipy %s, pandas %s, scikit-learn %s"
            % (prov.get("python"), prov.get("numpy"), prov.get("scipy"),
               prov.get("pandas"), prov.get("scikit_learn")))

def finite(x) -> bool:
    return (isinstance(x, (int, float)) and not isinstance(x, bool)
            and math.isfinite(float(x)))


def num(x, nd: int = 3) -> str:
    if isinstance(x, bool):
        return "yes" if x else "no"
    if not finite(x):
        return "not computed"
    return ("%%.%df" % nd) % float(x)


def pct(x, nd: int = 1) -> str:
    return "not computed" if not finite(x) else ("%%.%df %%%%" % nd) % (100.0 * float(x))


def pval(x, floor=None) -> str:
    if not finite(x):
        return "not computed"
    x = float(x)
    if finite(floor) and x <= float(floor) + 1e-12:
        # Every permutation fell below the observed share; the number is the
        # smallest the permutation count allows, not an estimate.
        n_perm = int(round(1.0 / float(floor))) - 1
        return "p at the floor of %d permutations, %.3f" % (n_perm, x)
    if x < 0.001:
        return "p < 0.001"
    return "p = %.3f" % x


_SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def interval(lo, hi, nd: int = 3) -> str:
    if not (finite(lo) and finite(hi)):
        return "not computed"
    return "%s to %s" % (num(lo, nd), num(hi, nd))


def _inner(w) -> str:
    """One value inside a gate-ledger entry, with nulls named rather than shown."""
    if w is None:
        return "not computed"
    if isinstance(w, bool):
        return "yes" if w else "no"
    if isinstance(w, float):
        return num(w)
    if isinstance(w, (list, tuple)):
        if not w:
            return "none"
        if all(x is None for x in w):
            return "not computed"
        return "[%s]" % ", ".join(_inner(x) for x in w)
    return str(w)


def pretty(v) -> str:
    if isinstance(v, str):
        return v.replace(" == ", " is ").replace("_", " ")
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        return num(v)
    if isinstance(v, dict):
        bits = ["%s %s" % (k.replace("_", " "), _inner(w))
                for k, w in list(v.items())[:2]]
        s = "; ".join(bits)
        if len(v) > 2:
            s += " (+%d more in the record)" % (len(v) - 2)
        return s
    return "not computed" if v is None else str(v)


def _join(items: Sequence[str]) -> str:
    items = [i for i in items if i]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


# ------------------------------------------------------------------- build
def build_report(record: dict, summary: dict, *,
                 input_qc: Optional[dict] = None,
                 problems: Optional[List[str]] = None,
                 record_bytes: Optional[bytes] = None) -> Report:
    """Assemble the report from a record and the summary derived from it.

    ``input_qc`` is the input check the command line writes beside the record;
    ``problems`` are the release-gate failures it raised. ``record_bytes`` is
    the serialised record the report describes; when given its SHA-256 is
    printed in the identification band so that a report and a record can be
    matched without trusting either.
    """
    problems = list(problems or [])
    md = record.get("metadata_diagnostics") or {}
    interp = record.get("interpretation") or {}
    cfg = record.get("config") or {}
    disc = (record.get("post_clustering_inference") or {}).get("discreteness") or {}
    ledger = interp.get("gate_ledger") or []
    tripped = [g for g in ledger if g.get("triggered")]
    n_gates = sum(1 for g in ledger if g.get("applicable"))
    conc = md.get("lineage_concordance") or {}

    digest = hashlib.sha256(
        json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:12]
    run_id = hashlib.sha256(
        (digest + str(record.get("seed")) + str(record.get("n_isolates")))
        .encode()).hexdigest()[:8].upper()
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    record_sha = (hashlib.sha256(record_bytes).hexdigest()
                  if record_bytes is not None else None)

    ident = {
        "run": run_id, "issued": stamp,
        "software": "amr-archetypes %s" % __version__,
        "record": "cluster_result.json",
        "isolates": str(record.get("n_isolates")),
        "layers": ", ".join(record.get("layers") or []),
        "seed": str(record.get("seed")),
        "configuration": "sha256:%s" % digest,
        "record_sha256": record_sha or "",
        "stack": _stack_line(record.get("provenance") or {}),
    }
    status = {
        "tripped": len(tripped), "applicable": n_gates,
        "gates_line": ("%d of %d applicable gates closed on this run."
                       % (len(tripped), n_gates))
                      if n_gates else "No gate applied on this run.",
        "claim_level": (str(interp.get("claim_level"))
                        if interp.get("claim_level") is not None
                        else "not recorded"),
        "claim_status": (str(interp.get("claim_status")).replace("_", " ")
                         if interp.get("claim_status") else "no status"),
        "flag": bool(tripped),
    }

    S: List[Section] = []

    # ------------------------------------------------ 0 measurement summary
    s = Section("summary", "Measurement summary")
    s.p("**Question asked.** Whether this collection holds recurring "
        "resistance profiles: groups of isolates that recur on traits held "
        "out of the clustering, that are separated by gaps rather than cut "
        "from a gradient, that are not manufactured by the shape of the "
        "panel, and that are not the lineages under another name.")
    att = md.get("lineage_attribution") or {}
    lam = summary.get("lineage_attributable_share")
    lam_ci = summary.get("lineage_attributable_share_ci95") or [None, None]
    if finite(lam) and att.get("estimable") is False:
        lam_text = ("%s, reported without a verdict: support %s against the "
                    "%s the estimator needs" % (
                        num(lam), pct(att.get("support")),
                        pct(att.get("support_threshold", 0.9), 0)))
    elif finite(lam):
        lam_text = "%s%s; gate at %s" % (
            num(lam),
            (" (95 %% interval %s)" % interval(lam_ci[0], lam_ci[1]))
            if finite(lam_ci[0]) and finite(lam_ci[1]) else "",
            num(att.get("lambda_gate"), 2))
    elif not md.get("lineage_column"):
        lam_text = "not estimated: no lineage column was given"
    else:
        lam_text = "withheld; the condition that failed is named in Table 1"
    s.kv([
        ("Profile groups", str(record.get("selected_k"))
         + (", at the top of the swept range: the number is not identified"
            if summary.get("k_at_sweep_boundary") else "")),
        ("Cohort", "%s isolates, %s layer%s" % (
            record.get("n_isolates"), len(record.get("layers") or []),
            "" if len(record.get("layers") or []) == 1 else "s")),
        ("Recurrence on held-out traits",
         str(summary.get("p_value_structure_report") or "not run")),
        ("Discrete beyond a gradient",
         str(summary.get("discreteness_verdict") or "not run")),
        ("Share of the grouping explained by lineage", lam_text),
        ("Claim", "level %s, %s" % (status["claim_level"],
                                     status["claim_status"])),
    ])
    if interp.get("claim_level") is not None:
        s.figure("Figure 1", "ladder",
                 {"level": interp.get("claim_level"),
                  "gates": [_GATE_LABEL.get(g["code"], g["code"])
                            for g in tripped]},
                 "The claim ladder. The run reaches the highest rung its gates "
                 "allow; a closed gate holds it there and is named. Level 4 is "
                 "reached only when every applicable gate passes, and is a "
                 "candidate status, not biological confirmation.")
    if n_gates:
        s.p("**Gates.** %d of %d applicable conditions closed on this run. A "
            "closed gate is a result, not an error: it says the collection "
            "cannot support the reading. No gate closed does not establish "
            "that the groups are biological types." % (len(tripped), n_gates))
    else:
        s.p("**Gates.** No gate applied on this run: the record carries no "
            "gate ledger.")
    not_done = _not_evaluated(record)
    if not_done:
        s.callout("Not evaluated on this run, and why", not_done)
    inter = _interpretation(record, summary)
    if inter:
        s.callout("Interpretation (generated from the record by fixed rules)",
                  inter)
    S.append(s)

    # --------------------------------------------- 1 admissibility of input
    s = Section("admissibility", "Admissibility of the input")
    prov = []
    if md.get("lineage_column"):
        prov.append(("Lineage column", "`%s`" % md["lineage_column"]))
    prov.append(("Binary layers", ", ".join(record.get("layers") or []) or
                 "none"))
    snf = cfg.get("snf") or {}
    dist = cfg.get("distance") or {}
    mc = cfg.get("monte_carlo") or {}
    if dist:
        prov.append(("Distance", "%s (undefined pairs: %s)"
                     % (dist.get("metric"), dist.get("undefined_pair"))))
    if snf:
        prov.append(("Fusion", "similarity-network fusion, K=%s, mu=%s, T=%s"
                     % (snf.get("K"), snf.get("mu"), snf.get("T"))))
    if mc:
        prov.append(("Resampling", "%s consensus, %s bootstrap, %s permutations"
                     % (mc.get("consensus_B"), mc.get("n_boot"), mc.get("n_perm"))))
    if not cfg:
        prov.append(("Settings", "no configuration is recorded in this record"))
    s.kv(prov)
    if input_qc:
        m = input_qc.get("missing") or {}
        total = sum(v.get("cells", 0) for v in (m.get("layers") or {}).values())
        lin = input_qc.get("lineage") or {}
        s.p("Empty cells in the binary layers: %d%s. Nothing was filled in."
            % (total, (", handled by the policy `%s`" % m.get("policy"))
               if total else ""))
        if lin:
            s.p("Lineage groups in the input: %s, of which %s hold a single "
                "isolate. Support %s against the %s the estimator needs: %s"
                % (lin.get("n_groups"), lin.get("n_singletons"),
                   pct(lin.get("support")), pct(lin.get("support_threshold")),
                   "accepted." if lin.get("estimable")
                   else "not accepted at this typing resolution."))
    else:
        s.p("No input check was attached to this record.")
    shares = [v for v in (md.get("clonal_share") or {}).values()
              if finite(v.get("support"))]
    support = min((v["support"] for v in shares), default=None)
    groups_used = max((v.get("n_groups") for v in shares
                       if isinstance(v.get("n_groups"), int)), default=None)
    s.table("Table 1", "Conditions the diagnostics require before any result "
            "is reported.",
            [("Condition", "lab"), ("Observed", "num"), ("Required", "num"),
             ("Verdict", "lab")],
            [("Lineage support",
              pct(support) if support is not None else "not recorded",
              "≥ 90.0 %",
              "accepted" if support is not None and finite(support)
              and support >= 0.9
              else "refused" if support is not None else "not evaluated"),
             ("Lineage groups used",
              "%s of %s" % (groups_used, conc.get("n_lineages"))
              if groups_used is not None and conc.get("n_lineages") is not None
              else "not recorded", "reported",
              "accepted" if groups_used is not None else "not evaluated"),
             ("Effective layers", num(summary.get("fusion_n_eff_layers"), 1),
              "> 1.5",
              "refused" if summary.get("fusion_collapse") else "accepted"),
             ("Split design",
              "adequate" if summary.get("split_design_adequate")
              else "inadequate", "adequate",
              "accepted" if summary.get("split_design_adequate")
              else "refused")])
    S.append(s)

    # ================================================= part II: the groups
    ks = record.get("k_selection") or {}
    s = Section("groups", "Are there resistance-profile groups?")
    held_out = summary.get("p_value_structure_report")
    verdict = summary.get("discreteness_verdict")
    gradient = summary.get("discrete_beyond_a_gradient")
    if held_out is None:
        s.p("The selection procedure returned **%s** profile group. No "
            "structure was detected, so the held-out reproduction test and "
            "the reading of gaps against a gradient were not run: with one "
            "group there is nothing for them to separate. This is a result, "
            "not a failure." % record.get("selected_k"))
    elif summary.get("inference_status") == "withheld_inadequate_split_design":
        s.p("The selection procedure returned **%s** profile groups. Whether "
            "they are real rather than an artefact of the clustering could "
            "not be tested: the panel does not hold enough independent "
            "features to split into a training and a test half. The groups "
            "are descriptive only." % record.get("selected_k"))
    else:
        if verdict:
            shape = (" The structure is separated by gaps rather than shading "
                     "continuously from one type into the next (%s)." % verdict)
        elif gradient is False:
            shape = (" The isolates shade continuously from one type into the "
                     "next: the groups sit on a gradient rather than being "
                     "separated by gaps.")
        else:
            shape = ""
        s.p("The selection procedure returned **%s** profile groups. Tested "
            "on features held out of the clustering, the grouping reproduces "
            "at %s.%s" % (record.get("selected_k"), held_out, shape))
        # Each split re-derives its own labels from the discovery half of the
        # features. How closely those labels resemble the reported grouping
        # decides whether the held-out result is about this grouping or about
        # structure in the layers in general, and the record carries the
        # answer; a page that reports the p-value has to report this beside it.
        pci = record.get("post_clustering_inference") or {}
        ari = pci.get("ari_discovery_vs_reported") or {}
        if finite(ari.get("median")) and pci.get("concerns_reported_partition") is not None:
            if pci.get("concerns_reported_partition"):
                s.p("The labels re-derived inside each split resemble the "
                    "reported grouping at a median adjusted Rand index of %s "
                    "(range %s to %s over %s splits), so the held-out evidence "
                    "concerns this grouping."
                    % (num(ari.get("median"), 2), num(ari.get("min"), 2),
                       num(ari.get("max"), 2), ari.get("n")))
            else:
                s.p("The labels re-derived inside each split resemble the "
                    "reported grouping at a median adjusted Rand index of %s "
                    "(range %s to %s over %s splits), below 0.5: the held-out "
                    "evidence attests structure in the layers, and the "
                    "reported grouping is one description of it rather than "
                    "the one the test confirmed."
                    % (num(ari.get("median"), 2), num(ari.get("min"), 2),
                       num(ari.get("max"), 2), ari.get("n")))
    s.figure("Figure 2", "mdl", {"sweep": ks.get("mdl_sweep") or [],
                                 "selected": record.get("selected_k")},
             "Description length saved by describing the cohort as k "
             "archetypes rather than as one population. The turn in the "
             "curve, not a threshold, is what selects k.")
    ci = summary.get("continuum_tail_probability_ci95") or {}
    mdl_note = (record.get("mdl_calibration") or {}).get("note", "")
    s.table("Table 2", "Evidence behind the number of groups.",
            [("Quantity", "lab"), ("Value", "num"), ("Reading", "lab")],
            [("Groups selected", str(record.get("selected_k")),
              "by minimum description length"),
             ("Description length saved", "%s bits" % num(ks.get("mdl_best_gain"), 0),
              "%s of the null code" % pct(ks.get("mdl_gain_fraction"))),
             ("Permutation null for that gain",
              num(ks.get("mdl_p_value")) if finite(ks.get("mdl_p_value"))
              else "not run",
              "a permutation null for the description length is optional "
              "and was not requested; the held-out test below is the "
              "evidence for real structure" if "not run" in mdl_note
              else mdl_note),
             ("Held-out reproducibility", str(held_out or "not run"),
              "groups recur on features not used to form them"),
             ("Continuum exceedances",
              "%s of %s" % (summary.get("continuum_bootstrap_exceedances"),
                            disc.get("n_boot"))
              if summary.get("continuum_bootstrap_exceedances") is not None
              and disc.get("n_boot") is not None else "not run",
              "upper limit of the exact binomial interval %s" % num(ci.get("high"), 4)
              if finite(ci.get("high")) else "the continuum test was not run"),
             ("Latent dimension of the null",
              str(summary.get("continuum_latent_dimension"))
              if summary.get("continuum_latent_dimension") is not None
              else "not run",
              "chosen by information criterion, not pinned")])
    S.append(s)

    s = Section("artefact", "Could the grouping be an artefact of the panel?")
    art = record.get("artifact_diagnostics") or {}
    per_layer = art.get("per_layer") or []
    s.p("A grouping can arise from the shape of the panel rather than from "
        "the isolates. Three things are checked per layer: how many isolates "
        "carry no informative feature at all, how many independent directions "
        "the layer really holds, and whether the nearest-neighbour cut that "
        "builds the affinity graph was decided by ties rather than by "
        "distance. A tie inflation of 1.00 means the cut was clean; a value "
        "above it means more neighbours were kept than asked for, because "
        "candidates shared the same affinity.")
    s.table("Table 3", "Panel geometry, layer by layer.",
            [("Layer", "lab"), ("Features used", "num"),
             ("Effective dimension", "num"), ("Uninformative isolates", "num"),
             ("Tie inflation at the cut", "num"), ("Empty-stratum agreement", "num")],
            [(p.get("layer"), str(p.get("n_features_used")),
              num(p.get("effective_dimension"), 2),
              pct(p.get("frac_uninformative_rows")),
              num(p.get("knn_tie_inflation"), 3), num(p.get("empty_stratum_ari")))
             for p in per_layer])
    lg = art.get("largest_group") or {}
    s.p("The empty-stratum check compares the grouping with the isolates that "
        "carry nothing in one layer, and the largest group against the rest "
        "with the isolates that carry nothing in any layer. An agreement near "
        "one would mean the grouping is reproduced by absence alone. The "
        "largest group holds %s isolates, of which %s carry no feature of any "
        "layer; its agreement with that indicator is %s. The largest value on "
        "this run is %s."
        % (lg.get("size", "n/a"), pct(lg.get("frac_positive_in_no_layer")),
           num(lg.get("ari_largest_vs_rest_against_all_empty_indicator")),
           num(summary.get("max_empty_stratum_ari"))))
    layers = record.get("layers") or []
    pattern = art.get("layer_positivity_pattern_per_cluster") or {}
    sizes = record.get("cluster_sizes") or {}
    if pattern and len(layers) == 2:
        cats = [("none", "carries nothing"),
                (layers[0], "%s only" % layers[0]),
                (layers[1], "%s only" % layers[1]),
                ("+".join(layers), "both layers")]
        order = sorted(pattern, key=lambda c: -int((sizes or {}).get(c, 0)))
        groups = [("group %s" % c, int((sizes or {}).get(c, sum(pattern[c].values()))),
                   pattern[c]) for c in order]
        s.figure("Figure 3", "stack",
                 {"groups": groups, "cats": cats},
                 "What each group is made of, by the layers its isolates "
                 "carry. A group that is mostly the trait-absent stratum is an "
                 "absence, not a profile; the number above each bar is the "
                 "group's size.")
    S.append(s)

    s = Section("baselines", "Does the grouping beat a simpler rule?")
    base = record.get("baselines") or {}
    cands = base.get("candidates") or []
    cmp_ = summary.get("baseline_comparison") or {}
    s.p("A grouping that a single layer or a plain concatenation reproduces "
        "has not earned the fusion that produced it. Every candidate below was "
        "run through the same held-out test the reported grouping had to pass: "
        "its own pipeline on the discovery half of the feature blocks, scored "
        "on the held-out half. That test is the criterion that can rank "
        "candidates. The description length is computed in sample and favours "
        "a candidate fitted by likelihood on these same bits, so it is shown "
        "and decides nothing; agreement with an external labelling is shown as "
        "a paired difference from the reported grouping with its interval, so "
        "that \"not distinguishable\" is a possible answer.")
    ext_names = []
    for c in cands:
        for key in (c.get("external_agreement_vs_reported") or {}):
            if key not in ext_names:
                ext_names.append(key)
    brow = []
    for c in cands:
        ho = c.get("held_out") or {}
        brow.append((str(c.get("partition")).replace("_", " "),
                     str(c.get("n_clusters")),
                     pval(ho.get("p_value_structure")) if ho.get("status") == "ok"
                     else "not run",
                     num(c.get("mdl_gain"), 0),
                     num(c.get("ari_vs_fused"))))
    s.table("Table 4", "Candidate groupings. Held-out: the feature-split test "
            "on the candidate's own pipeline. Description length: in sample, "
            "descriptive only.",
            [("Candidate", "lab"), ("Groups", "num"), ("Held-out", "num"),
             ("Description length saved", "num"),
             ("Agreement with reported", "num")], brow)
    if ext_names:
        erow = []
        for c in cands:
            if c.get("partition") == "fused_snf":
                continue
            vs = c.get("external_agreement_vs_reported") or {}
            cells = [str(c.get("partition")).replace("_", " ")]
            for key in ext_names:
                d = vs.get(key)
                cells.append("%+.3f%s\n%s to %s" % (
                    d.get("ari_difference"),
                    " *" if d.get("distinguishable") else "",
                    num(d.get("ci95_low"), 3), num(d.get("ci95_high"), 3))
                    if d and finite(d.get("ari_difference")) else "not computed")
            erow.append(tuple(cells))
        s.table("Table 5", "Agreement with each external labelling, as the "
                "difference in adjusted Rand index between the candidate and "
                "the reported grouping on the same bootstrap resamples of "
                "isolates, with its 95 % interval. * marks a difference whose "
                "interval excludes zero; without it the two cannot be told "
                "apart by that labelling.",
                [("Candidate", "lab")] + [(k.replace("_", " "), "num")
                                          for k in ext_names], erow)
    s.p(_baseline_verdict(cmp_))
    S.append(s)

    s = Section("layers", "Which layer carries the grouping?")
    infl = record.get("layer_influence") or {}
    agree = record.get("layer_agreement") or {}
    lead = (str(infl.get("regime_note", "")).capitalize() + ". "
            if infl.get("regime_note") else "")
    if infl.get("per_layer"):
        s.p("%sThe effective number of layers is %s of %s, and the layer that "
            "moves the answer most is **%s**. A layer marked inert can be "
            "removed without changing the grouping."
            % (lead, num(infl.get("n_eff"), 2), infl.get("n_layers"),
               infl.get("dominant_layer") or "not recorded"))
    else:
        s.p("No layer-influence diagnostics are recorded on this run.")
    bars = [(str(p.get("layer")), float(p.get("weight") or 0.0), bool(p.get("inert")))
            for p in (infl.get("per_layer") or [])]
    s.figure("Figure 4", "bars", {"rows": bars,
                                  "label": "weight in the fused network",
                                  "note": "Weight carried by each layer"},
             "Weight each layer carries in the fused network. A layer drawn in "
             "the warning colour is inert: the grouping does not change when "
             "it is removed.")
    s.table("Table 6", "What each layer contributes.",
            [("Layer", "lab"), ("Weight", "num"), ("Loss when removed", "num"),
             ("Agreement alone with the fused grouping", "num"), ("Inert", "lab")],
            [(p.get("layer"), num(p.get("weight")), num(p.get("delta_loo")),
              num(p.get("ari_solo_vs_fused")), "yes" if p.get("inert") else "no")
             for p in (infl.get("per_layer") or [])])
    conflict = agree.get("conflict_mean_layer_pairs_only")
    if finite(conflict):
        s.p("Mean disagreement between layers, taken over layer pairs only, "
            "is %s." % num(conflict))
    S.append(s)

    s = Section("stability", "How stable is the grouping?")
    frag = record.get("fragility") or {}
    fi = [x for x in (frag.get("F_isolate") or []) if finite(x)]
    ff = [x for x in (frag.get("F_feature") or []) if finite(x)]
    lr = record.get("label_recoverability") or {}
    s.table("Table 7", "Behaviour under resampling and under removal.",
            [("Quantity", "lab"), ("Value", "num"), ("Reading", "lab")],
            [("Proportion of ambiguous pairs", num(record.get("pac")),
              "share of pairs that neither always nor never co-cluster across "
              "consensus draws; zero is a clean split"),
             ("Area under the consensus distribution", num(record.get("cdf_area")),
              "a flat consensus matrix drives this towards one"),
             ("Largest isolate fragility", num(max(fi) if fi else None),
              "how far one isolate can move the grouping"),
             ("Largest feature fragility", num(max(ff) if ff else None),
              "how far one feature can move the grouping"),
             ("Label recovery from half the features",
              num(lr.get("internal_label_recoverability")),
              str(lr.get("note", "")))])
    S.append(s)

    # ----------------------------------------------------- gates and scope
    s = Section("gates", "What may be concluded, and what may not")
    level = interp.get("claim_level")
    s.p("The highest claim the profile-group diagnostics carry is **%s**%s. "
        "That level attests reproducible structure in the reported "
        "grouping; it does not say that the reported grouping is the best of "
        "the candidates in Table 4, which is a separate question answered "
        "there. Every gate was evaluated; the margin is the distance the run "
        "had left before the gate would have closed."
        % ("level %s" % level if level is not None else "no level recorded",
           (", %s" % str(interp.get("claim_status")).replace("_", " "))
           if interp.get("claim_status") else ""))
    margins = [(str(g["code"]).replace("_", " "), float(g["margin_to_failure"]),
                bool(g.get("triggered")))
               for g in ledger
               if g.get("applicable") and finite(g.get("margin_to_failure"))]
    s.figure("Figure 5", "bars", {"rows": margins,
                                  "label": "margin to failure (the gate closes at zero)",
                                  "note": "Distance to failure for each gate"},
             "Distance to failure for each gate that carries a numeric margin. "
             "A short bar is a result that only just holds.")
    for prob in problems:
        s.p("**Diagnostic failure:** %s" % prob)
    s.table("Table 8", "Gate ledger. Every gate is listed, including those "
            "that did not fire.",
            [("Gate", "lab"), ("Applicable", "lab"), ("Closed", "lab"),
             ("Observed", "lab"), ("Threshold", "lab")],
            [(str(g.get("code")).replace("_", " "),
              "yes" if g.get("applicable") else "no",
              "yes" if g.get("triggered") else "no",
              pretty(g.get("value")), pretty(g.get("threshold")))
             for g in ledger])
    S.append(s)

    # ---------------------------------------------------- provenance, terms
    s = Section("provenance", "Provenance and terms")
    s.kv([("Software", "amr-archetypes %s, record schema %s"
           % (__version__, record.get("schema_version", ""))),
          ("Seed", str(record.get("seed"))),
          ("Configuration", "`sha256:%s`" % digest),
          ("Record", ("`sha256:%s`" % record_sha) if record_sha
           else "digest not available: the report was built from an object, "
                "not from the file")])
    s.callout("Terms used in this report", [
        "**Profile group.** A set of isolates the fused layers place together. "
        "It is a description of this collection until the diagnostics say "
        "more.",
        "**Held-out recurrence.** Whether the groups formed on one half of the "
        "traits are found again on the other half, which the same data cannot "
        "manufacture.",
        "**Share of the grouping explained by lineage.** How much of what the "
        "groups explain the lineage label already explains. Near 1: the "
        "groups are the lineages under another name. Near 0: they cut across "
        "lineages.",
        "**Control.** The same calculation on shuffled lineage labels, which "
        "should return roughly zero; a share is read against it.",
        "**Support.** The share of isolates sitting in lineages large enough "
        "to inform the lineage share; below 0.90 the software withholds it.",
        "**Gate.** A condition fixed before the run. If it does not hold, the "
        "software withholds the reading and names the condition that failed.",
    ])
    S.append(s)

    symbols = [
        ("§", "Derived arithmetically from a quantity recorded elsewhere in "
              "the record rather than estimated in this run."),
    ]
    colophon = [
        "amr-archetypes %s · record schema %s · seed %s · configuration "
        "sha256:%s" % (__version__, record.get("schema_version", ""),
                       record.get("seed"), digest),
        "Cite this run as: “amr-archetypes %s, run %s, %s.”"
        % (__version__, run_id, stamp),
        "This report supersedes any earlier report bearing the same run "
        "identifier. It is regenerated from the record and holds no value "
        "that the record does not. The symbols carry the same wording in every "
        "run of this software; no symbol against a value means only that none "
        "of the listed conditions fired. Intervals are printed as computed, "
        "without clipping to the natural bounds of the quantity; clipping "
        "would leave their coverage unchanged and is left to the reader so "
        "that widths stay comparable across runs.",
    ]
    return Report(ident=ident, status=status, sections=S, symbols=symbols,
                  colophon=colophon)


# ------------------------------------------------------------- the rules
def _not_evaluated(record: dict) -> List[str]:
    """Every instrument the run did not use, with the reason the record gives."""
    out: List[str] = []
    if (record.get("mdl_calibration") or {}).get("n_perm", 0) == 0:
        out.append("Permutation null for the description length: not "
                   "requested. The held-out test is the evidence for real "
                   "structure.")
    md = record.get("metadata_diagnostics") or {}
    att = md.get("lineage_attribution") or {}
    if att and not (finite(att.get("ci_low")) and finite(att.get("ci_high"))):
        out.append("Interval on the share of the profile groups explained by "
                   "lineage: not given, because the groups were re-fitted "
                   "inside every cross-validation fold and a lineage drawn "
                   "twice would train a group on rows that are also held "
                   "out. The spread across repeated cross-validation is %s."
                   % num(att.get("lam_cv_sd")))
    infl = record.get("layer_influence") or {}
    if infl.get("n_perm_note"):
        out.append("Permutation test on layer contribution: skipped above "
                   "500 isolates, where it would cost as many network fusions "
                   "as permutations times layers; the leave-one-layer-out "
                   "influence in Table 6 was computed.")
    return out


def _interpretation(record: dict, summary: dict) -> List[str]:
    """Sentences fixed by the readings in the summary. Empty cases drop out."""
    out: List[str] = []
    k = record.get("selected_k")
    held_out = summary.get("p_value_structure_report")
    if held_out is None:
        out.append("The selection returned %s profile group: at the "
                   "resolution of these layers nothing in the collection "
                   "separates into recurring profiles. No reading of types "
                   "follows." % k)
        return out
    if summary.get("inference_status") == "withheld_inadequate_split_design":
        out.append("The %s groups could not be tested against features held "
                   "out of the clustering; they are descriptive only." % k)
    else:
        out.append("The %s groups recur on features held out of the "
                   "clustering (%s)." % (k, held_out))
        verdict = summary.get("discreteness_verdict")
        if verdict == "discrete":
            out.append("They are separated by gaps rather than cut from a "
                       "gradient.")
        elif summary.get("discrete_beyond_a_gradient") is False:
            out.append("They are cuts through a gradient: the isolates shade "
                       "from one profile into the next, and the number of "
                       "groups is a choice, not a finding.")
        elif verdict:
            out.append("Whether they are discrete or a gradient was not "
                       "resolved (%s)." % str(verdict).replace("_", " "))
    lam = summary.get("lineage_attributable_share")
    if finite(lam) and summary.get("lineage_attribution_estimable") is False:
        out.append("Whether the groups are the lineages relabelled could not "
                   "be decided at this typing resolution: only %s of isolates "
                   "sit in lineages of at least two members, below the %s the "
                   "share needs, so its value of %s carries no verdict."
                   % (pct(summary.get("lineage_attribution_support")),
                      pct(0.9, 0), num(lam)))
    elif finite(lam):
        if summary.get("lineage_confounded"):
            out.append("Lineage explains %s of the grouping, at or above the "
                       "gate: read the groups as the lineages, not as types "
                       "that cut across them." % num(lam))
        elif summary.get("lineage_attribution_resolved_at_95ci") is False:
            out.append("Lineage explains %s of the grouping, below the gate, "
                       "but the interval crosses it; the reading is "
                       "unresolved rather than cleared." % num(lam))
        else:
            out.append("Lineage explains %s of the grouping, below the gate: "
                       "the groups cut across lineages." % num(lam))
    codes = set(summary.get("active_gate_codes") or [])
    if "k_selection" in codes:
        out.append("The number of groups is not identified: the description "
                   "length was still improving at the largest number swept, "
                   "so the grouping is a cut at the edge of what was tried.")
    if "empty_stratum" in codes:
        layer = str((record.get("artifact_diagnostics") or {}).get("empty_stratum_layer") or "")
        if layer.startswith("all layers"):
            out.append("The largest group is the isolates that carry none of the "
                       "traits of any layer; it is an absence, not a profile.")
        else:
            out.append("The grouping follows the isolates that carry none of the "
                       "traits of one layer; it is an absence, not a profile.")
    if "phenotype_superiority" in codes:
        out.append("A one-dimensional resistance score predicts the measured "
                   "phenotype better than the grouping does.")
    if "fusion_collapse" in codes:
        out.append("The fusion collapsed onto a single layer; the groups are "
                   "that layer under another name.")
    out.append("These sentences follow from the record by fixed rules and "
               "carry no judgement beyond it.")
    return out


def _baseline_verdict(cmp_: dict) -> str:
    """The outcome of the candidate comparison, in the words the case fixes."""
    if not cmp_:
        return "No candidate groupings are recorded on this run."
    case = cmp_.get("case")
    best = str(cmp_.get("best_in_sample_description_length", "")).replace("_", " ")
    if case == "not_scored":
        return ("The candidates carry no held-out test on this run, so nothing "
                "here ranks them. The description length in sample is largest "
                "for %s, which says how well that grouping compresses these "
                "bits and not which grouping is real." % best)
    n_t, n_r = cmp_.get("n_tested"), cmp_.get("n_reproducing")
    diffs = cmp_.get("distinguishable") or {}
    named = []
    for part, labels in diffs.items():
        bits = ["%s %s" % ("higher on" if v > 0 else "lower on", k.replace("_", " "))
                for k, v in labels.items()]
        named.append("%s (%s)" % (part.replace("_", " "), ", ".join(bits)))
    ext = ("" if not named else
           " Agreement with an external labelling differs distinguishably from "
           "the reported grouping for %s. Whether higher agreement is a merit "
           "depends on the labelling: closer agreement with a lineage label "
           "means the groups are closer to being the lineages, which is the "
           "confounding the attribution measures, not a gain."
           % _join(named))
    if case == "reported_not_reproducible":
        others = _join([p.replace("_", " ") for p in cmp_.get("reproducing_candidates") or []])
        return ("The reported grouping did not reproduce on held-out features "
                "while %s did. The gate on held-out reproduction closes on the "
                "reported grouping by its own rule; read the profile groups of "
                "this run as not established.%s" % (others, ext))
    return ("%s of %s tested groupings reproduce on held-out features. The "
            "reported grouping is one of several admissible descriptions of "
            "this collection; the held-out test does not prefer one of them. "
            "The description length in sample is largest for %s, as is "
            "expected of a grouping fitted by likelihood on these bits; it "
            "does not say which grouping is real.%s" % (n_r, n_t, best, ext))
