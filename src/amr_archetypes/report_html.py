"""The run report as one self-contained page, with the diagnostics drawn.

WHY A SECOND FORM OF THE REPORT. ``report.md`` states the result in prose and
is the form that diffs cleanly between runs. It is not the form in which a
reader sees what the numbers are doing. On the shipped planted control every
one of the sixty per-trait intervals crosses zero, and the prose form prints
the largest of them, 0.128, beside ``estimable: yes``; a reader takes that for
a finding. Drawn as intervals against a ruled zero the same table says in one
look that no single trait is separated from none. The same holds for the gates:
"no diagnostic gate tripped" is true and hides that one gate had a margin of
0.04 while the rest were near 0.5.

WHAT IT ADDS BEYOND THE PROSE FORM. The record holds twenty-eight blocks. The
prose form reads five of them. The four sections added here are the ones that
answer whether the result could be wrong rather than what it is: whether the
grouping is an artefact of the panel, whether a simpler rule does as well,
which layer carries it, and how stable it is under resampling. Reporting a
result while withholding the diagnostics that could undermine it is selective
reporting, whatever the intent.

NO DEPENDENCY. The figures are written as SVG here rather than drawn with a
plotting library, so a report costs the reader nothing to open and the package
keeps matplotlib optional. Coordinates are rounded to two decimals so that two
reports of the same run diff to nothing.
"""
from __future__ import annotations

import math
import re
from typing import Optional

from .report_model import Block, build_report

__all__ = ["render_html_report"]

INK, MID, FAINT = "#1A1A1A", "#4A4A4A", "#8A8A8A"
RULE, PAPER = "#C8C8C4", "#FDFDFB"
ACCENT, FLAG = "#12436D", "#D55E00"


def _finite(x) -> bool:
    return isinstance(x, (int, float)) and not math.isnan(float(x))


def _esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _num(x, nd: int = 3) -> str:
    if not _finite(x):
        return "&#8212;"
    if isinstance(x, bool):
        return "yes" if x else "no"
    return ("%%.%df" % nd) % float(x)


def _pct(x, nd: int = 1) -> str:
    return "&#8212;" if not _finite(x) else ("%%.%df&#8201;%%%%" % nd) % (
        100.0 * float(x))


def _ticks(lo: float, hi: float, target: int = 5) -> list:
    """1, 2 or 5 times a power of ten, spanning the drawn range and no more."""
    if not (_finite(lo) and _finite(hi)) or hi <= lo:
        return [lo] if _finite(lo) else [0.0]
    raw = (hi - lo) / max(target, 2)
    mag = 10.0 ** math.floor(math.log10(raw)) if raw > 0 else 1.0
    for m in (1.0, 2.0, 2.5, 5.0, 10.0):
        if raw <= m * mag:
            step = m * mag
            break
    else:
        step = 10.0 * mag
    start = step * math.floor(lo / step)
    out, v = [], start
    while v <= hi + step * 1e-9:
        if lo - 1e-12 <= v <= hi + 1e-12:
            out.append(round(v, 10))
        v += step
    return out or [lo, hi]


def _r(v: float) -> str:
    return "%.2f" % float(v)


# ------------------------------------------------------------- figures ----
def _fig_mdl(sweep, selected) -> str:
    """Description length saved against the number of groups."""
    if not sweep:
        return ""
    W, H, L, R, T, B = 470, 172, 54, 14, 14, 34
    ks = [p["k"] for p in sweep]
    gs = [float(p["gain"]) for p in sweep]
    xlo, xhi = min(ks) - 0.5, max(ks) + 0.5
    ylo, yhi = min(0.0, min(gs)), max(gs) * 1.12 or 1.0
    X = lambda v: L + (v - xlo) / (xhi - xlo) * (W - L - R)    
    Y = lambda v: H - B - (v - ylo) / (yhi - ylo) * (H - T - B)

    p = ['<svg viewBox="0 0 %d %d" role="img" '
         'xmlns="http://www.w3.org/2000/svg"><title>Description length saved '
         'against the number of profile groups</title>' % (W, H)]
    for t in _ticks(ylo, yhi, 4):
        p.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" '
                 'stroke-width="0.4" shape-rendering="crispEdges"/>'
                 % (_r(L), _r(Y(t)), _r(W - R), _r(Y(t)), RULE))
        p.append('<text x="%s" y="%s" text-anchor="end" class="tk">%s</text>'
                 % (_r(L - 6), _r(Y(t) + 3), "%.0f" % t))
    p.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" '
             'stroke-width="0.6" shape-rendering="crispEdges"/>'
             % (_r(L), _r(Y(0)), _r(W - R), _r(Y(0)), MID))
    p.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" '
             'stroke-width="1.6" stroke-dasharray="3 3"/>'
             % (_r(X(selected)), _r(T), _r(X(selected)), _r(H - B), FAINT))
    d = " ".join("%s%s,%s" % ("M" if i == 0 else "L", _r(X(k)), _r(Y(g)))
                 for i, (k, g) in enumerate(zip(ks, gs)))
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.4"/>'
             % (d, ACCENT))
    for k, g in zip(ks, gs):
        sel = k == selected
        p.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>'
                 % (_r(X(k)), _r(Y(g)), "3.6" if sel else "2.2",
                    ACCENT if sel else MID))
        p.append('<text x="%s" y="%s" text-anchor="middle" class="tk">%d'
                 '</text>' % (_r(X(k)), _r(H - B + 14), k))
    p.append('<text x="%s" y="%s" text-anchor="middle" class="ax">number of '
             'profile groups, k</text>' % (_r((L + W - R) / 2), _r(H - 6)))
    p.append('<text x="6" y="%s" class="ax" transform="rotate(-90 6 %s)">bits '
             'saved</text>' % (_r((T + H - B) / 2), _r((T + H - B) / 2)))
    p.append('<text x="%s" y="%s" class="lbl">selected</text>'
             % (_r(X(selected) + 5), _r(T + 10)))
    return "".join(p) + "</svg>"


def _fig_bars(rows, label: str, note: str = "") -> str:
    """One horizontal bar per row: (name, value, flagged)."""
    rows = [r for r in rows if _finite(r[1])]
    if not rows:
        return ""
    W, L, R, T, ROW, B = 470, 168, 66, 10, 17.0, 22
    H = T + ROW * len(rows) + B
    mx = max(abs(r[1]) for r in rows) * 1.15 or 1.0
    X = lambda v: L + (v / mx) * (W - L - R)

    p = ['<svg viewBox="0 0 %d %.0f" role="img" '
         'xmlns="http://www.w3.org/2000/svg"><title>%s</title>'
         % (W, H, _esc(note or label))]
    p.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" '
             'stroke-width="0.8" shape-rendering="crispEdges"/>'
             % (_r(L), _r(T - 2), _r(L), _r(H - B + 2), MID))
    for i, (name, value, flagged) in enumerate(rows):
        y = T + ROW * i + ROW / 2
        col = FLAG if flagged else ACCENT
        p.append('<text x="%s" y="%s" text-anchor="end" class="rw">%s</text>'
                 % (_r(L - 8), _r(y + 3), _esc(name)))
        p.append('<rect x="%s" y="%s" width="%s" height="6" fill="%s"/>'
                 % (_r(L), _r(y - 3), _r(max(X(abs(value)) - L, 0.6)), col))
        p.append('<text x="%s" y="%s" class="rv">%s</text>'
                 % (_r(W - R + 6), _r(y + 3), "%.2f" % value))
    p.append('<text x="%s" y="%s" text-anchor="middle" class="ax">%s</text>'
             % (_r((L + W - R) / 2), _r(H - 5), _esc(label)))
    return "".join(p) + "</svg>"


_CSS = """
:root{--ink:#1A1A1A;--mid:#4A4A4A;--faint:#8A8A8A;--rule:#C8C8C4;
--paper:#FDFDFB;--accent:#12436D;--flag:#D55E00}
*{box-sizing:border-box}
html{background:#EDEDEA}
body{margin:0;background:var(--paper);color:var(--ink);
font-family:"Source Sans 3","Source Sans Pro","IBM Plex Sans",Helvetica,Arial,
sans-serif;font-size:16px;line-height:1.45;
font-variant-numeric:lining-nums tabular-nums;-webkit-font-smoothing:antialiased}
.sheet{max-width:41rem;margin:0 auto;padding:34px 30px 60px}
h1{font-size:1.30rem;font-weight:600;letter-spacing:-.005em;margin:0 0 2px}
.sub{color:var(--mid);font-size:.94rem;margin:0 0 14px}
h2{font-size:1.0rem;font-weight:600;margin:34px 0 8px;padding-bottom:4px;
border-bottom:.8px solid var(--ink)}
h2 .no{color:var(--faint);font-weight:400;margin-right:.55em}
p{margin:0 0 10px}
.ident{border-top:.8px solid var(--ink);border-bottom:.8px solid var(--ink);
padding:9px 0;margin:0 0 20px;display:grid;
grid-template-columns:repeat(4,1fr);gap:3px 18px}
.ident div{font-size:.76rem;line-height:1.35}
.ident b{display:block;color:var(--faint);font-weight:400;font-size:.68rem;
letter-spacing:.055em;text-transform:uppercase}
.status{margin:0 0 18px}
.status .lead{font-size:.80rem;letter-spacing:.10em;text-transform:uppercase;
color:var(--accent);font-weight:600}
.status .lead.flag{color:var(--flag)}
.status p{margin:4px 0 0;color:var(--mid);font-size:.94rem}
table{border-collapse:collapse;width:100%;margin:10px 0 6px;font-size:.84rem}
caption{caption-side:top;text-align:left;color:var(--mid);font-size:.82rem;
margin-bottom:5px}
caption b{color:var(--ink);font-weight:600}
thead th{border-top:.8px solid var(--ink);border-bottom:.5px solid var(--ink);
padding:5px 7px;font-weight:600;vertical-align:bottom}
tbody td{padding:4px 7px;border:0}
tbody tr:last-child td{border-bottom:.8px solid var(--ink)}
.num{text-align:right}
td.num{white-space:nowrap}
td.num br+*{font-size:.9em;color:var(--mid)}
.lab{text-align:left}
td.nw{white-space:nowrap}
.flagcol{text-align:left;width:2.4em;color:var(--flag)}
figure{margin:16px 0 6px}
figure svg{width:100%;height:auto;display:block}
figcaption{font-size:.82rem;color:var(--mid);margin-top:6px}
figcaption b{color:var(--ink);font-weight:600}
svg text{font-family:inherit;fill:var(--ink)}
svg .tk{font-size:9.5px;fill:var(--mid)}
svg .ax{font-size:10px;fill:var(--mid)}
svg .rw{font-size:10px;fill:var(--ink)}
svg .rv{font-size:10px;fill:var(--mid)}
svg .lbl{font-size:9.5px;fill:var(--faint)}
.notes{margin-top:34px;border-top:.8px solid var(--ink);padding-top:10px;
font-size:.82rem;color:var(--mid)}
.notes dl{display:grid;grid-template-columns:1.6em 1fr;gap:2px 6px;margin:6px 0}
.notes dt{color:var(--flag)}
.notes dd{margin:0}
.colophon{margin-top:26px;border-top:.5px solid var(--rule);padding-top:9px;
font-size:.76rem;color:var(--faint);line-height:1.5}
.colophon code{font-family:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;
font-size:.94em;color:var(--mid);word-break:break-all}
.dl{display:grid;grid-template-columns:13.5em 1fr;gap:2px 14px;font-size:.88rem;
margin:8px 0 4px}
.dl dt{color:var(--mid)}
.dl dd{margin:0}
.ident .wide{grid-column:1 / -1}
.ident code{font-family:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;
font-size:.72rem;color:var(--mid);word-break:break-all}
.callout{border-left:2.5px solid var(--accent);padding:6px 0 2px 12px;
margin:14px 0 12px}
.callout .ct{font-size:.80rem;letter-spacing:.06em;text-transform:uppercase;
color:var(--accent);font-weight:600;margin-bottom:4px}
.callout p{font-size:.92rem;margin:0 0 6px}
.part{margin:40px 0 -22px;font-size:.78rem;letter-spacing:.10em;
text-transform:uppercase;color:var(--faint)}
ul{margin:4px 0 10px;padding-left:1.2em}
@media print{
 @page{size:A4;margin:22mm}
 html,body{background:#fff}
 .sheet{max-width:none;padding:0}
 h2,figure,tr,.callout,.notes{break-inside:avoid}
 thead{display:table-header-group}
 h2,caption{break-after:avoid}
 p{orphans:3;widows:3}
 svg,table,figure{print-color-adjust:exact;-webkit-print-color-adjust:exact}
}
"""


def _table(caption, headers, rows) -> str:
    """headers: list of (label, css class). rows: sequences of cells."""
    out = ["<table><caption>%s</caption><thead><tr>" % caption]
    out += ['<th class="%s">%s</th>' % (cls, h.replace("-", "&#8209;"))
            for h, cls in headers]
    out.append("</tr></thead><tbody>")
    for row in rows:
        out.append("<tr>")
        out += ['<td class="%s">%s</td>' % (headers[i][1], cell)
                for i, cell in enumerate(row)]
        out.append("</tr>")
    return "".join(out) + "</tbody></table>"



def _inline(text: str) -> str:
    """Escape, then the two inline marks the model allows, and a line break."""
    t = _esc(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t.replace("\n", "<br>")


_ALIGN = {"lab": "lab", "num": "num", "flag": "flagcol"}


def _render_block(b: Block, figs: dict) -> str:
    if b.kind == "p":
        return "<p>%s</p>" % _inline(b.text)
    if b.kind == "kv":
        out = ['<div class="dl">']
        for k, v in b.rows:
            out.append("<dt>%s</dt><dd>%s</dd>" % (_inline(str(k)), _inline(str(v))))
        return "".join(out) + "</div>"
    if b.kind == "table":
        headers = [(_inline(h), _ALIGN.get(a, "lab")) for h, a in b.headers]
        rows = [[_inline(str(c)) for c in row] for row in b.rows]
        return _table("<b>%s.</b> %s" % (_esc(b.label), _inline(b.caption)),
                      headers, rows)
    if b.kind == "figure":
        svg = figs.get(b.figure, lambda _data: "")(b.data)
        if not svg:
            return ""
        return ("<figure>%s<figcaption><b>%s.</b> %s</figcaption></figure>"
                % (svg, _esc(b.label), _inline(b.caption)))
    if b.kind == "callout":
        out = ['<div class="callout"><div class="ct">%s</div>' % _inline(b.title)]
        for line in b.lines:
            out.append("<p>%s</p>" % _inline(line))
        return "".join(out) + "</div>"
    return ""


def render_html_report(record: dict, summary: dict, *,
                       input_qc: Optional[dict] = None,
                       problems: Optional[list] = None,
                       record_bytes: Optional[bytes] = None) -> str:
    """One self-contained page for a run, from the record it wrote.

    Every value is read from ``record`` or ``summary``; none is recomputed,
    so the page cannot disagree with the file it describes.
    """
    rep = build_report(record, summary, input_qc=input_qc, problems=problems,
                       record_bytes=record_bytes)
    figs = {
        "mdl": lambda d: _fig_mdl(d.get("sweep") or [], d.get("selected")),
        "bars": lambda d: _fig_bars(d["rows"], d["label"], d.get("note", "")),
    }
    A: list[str] = []
    add = A.append
    add('<!doctype html><html lang="en"><head><meta charset="utf-8">')
    add('<meta name="viewport" content="width=device-width,initial-scale=1">')
    add("<title>Run report %s</title><style>%s</style></head><body>"
        % (rep.ident["run"], _CSS))
    add('<main class="sheet">')
    add("<h1>Lineage-conditioned resistance-profile analysis</h1>")
    add('<p class="sub">Run report. Every value is read from the record '
        "written by this run; none is recomputed here.</p>")
    add('<div class="ident">')
    for key, label in (("run", "Run"), ("issued", "Issued"),
                       ("software", "Software"), ("record", "Record"),
                       ("isolates", "Isolates"), ("layers", "Layers"),
                       ("seed", "Seed"), ("configuration", "Configuration")):
        add("<div><b>%s</b>%s</div>" % (label, _esc(rep.ident[key])))
    if rep.ident.get("record_sha256"):
        add('<div class="wide"><b>Record digest</b><code>sha256:%s</code></div>'
            % _esc(rep.ident["record_sha256"]))
    add("</div>")
    st = rep.status
    add('<div class="status"><span class="lead%s">Profile-group claim level '
        "%s &#183; %s</span><p>%s</p></div>"
        % (" flag" if st["flag"] else "", _esc(st["claim_level"]),
           _esc(st["claim_status"]), _esc(st["gates_line"])))
    n = 0
    for sec in rep.sections:
        n += 1
        if sec.part:
            add('<div class="part">%s &#183; the profile groups</div>' % _esc(sec.part))
        add('<h2><span class="no">%d</span>%s</h2>' % (n, _inline(sec.title)))
        for b in sec.blocks:
            add(_render_block(b, figs))
    add('<div class="notes"><b>Notes on reading this report.</b><dl>')
    for sym, text in rep.symbols:
        add("<dt>%s</dt><dd>%s</dd>" % (_esc(sym), _inline(text)))
    add("</dl></div>")
    add('<div class="colophon">')
    add("<br>".join(_inline(line) for line in rep.colophon))
    add("</div></main></body></html>")
    return "".join(A)
