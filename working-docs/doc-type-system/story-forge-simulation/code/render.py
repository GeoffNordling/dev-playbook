"""Write every view of the stories fact base into one local HTML page."""

import html
import math
import random
from pathlib import Path

from fact_base import ENV, SHORT, TESTS, cell, citers, d, in_e, nodes, sec, stories

OUT = Path(__file__).resolve().parent.parent / "stories-views.html"
E = html.escape
ORDER = ["Resume", "Projection", "Prep-Unit", "General-Sheet", "File"]
COL = {
    "Resume": "#2f6fdf",
    "Projection": "#1a9e5c",
    "Prep-Unit": "#c9731a",
    "General-Sheet": "#8a54c9",
    "File": "#888",
}
STFILL = {"complete": "#fff", "needs-detail": "#fde9b8", "draft": "#f7c6c6"}
ids = [s["id"] for s in stories]


def stem(s):
    """Return a story's stem."""
    return s["attrs"]["stem"]


_all = sorted({c for i in ids for c in citers(i)})


def short(path):
    """Return the shortest path suffix that names one citer uniquely."""
    parts = path.split("/")
    for k in range(1, len(parts) + 1):
        tail = "/".join(parts[-k:])
        if sum(x.endswith("/" + tail) or x == tail for x in _all) == 1:
            return tail
    return path


def link(s):
    """Link a story name to its card."""
    return f'<a href="#card-{E(stem(s))}">{E(stem(s))}</a>'


def cls(v):
    """Grey out a None cell."""
    return ' class="none"' if v == "None" else ""


def diag(labels):
    """Render header cells with diagonal labels."""
    return "".join(f'<th class="d"><span>{E(x)}</span></th>' for x in labels)


def legend(items):
    """Render a key of swatches and their meanings."""
    return (
        '<div class="key">'
        + "".join(f"<span>{sw} {E(t)}</span>" for sw, t in items)
        + "</div>"
    )


def box(fill, border="#999", w=1):
    """Render a square swatch."""
    return f'<i class="sw" style="background:{fill};border:{w}px solid {border}"></i>'


def dot(c):
    """Render a round swatch."""
    return f'<i class="dot" style="background:{c}"></i>'


def line(c, dash=False):
    """Render a line swatch."""
    return (
        f'<i class="ln" style="border-top:2px {"dashed" if dash else "solid"} {c}"></i>'
    )


STATUS_KEY = [(box(STFILL[k]), f"status {k}") for k in STFILL]

# --- story-to-story facts ---
rel = {(e["source"], e["target"]) for e in d["edges"] if e["relation"] == "related"}
lnk = {
    (e["source"], e["target"])
    for e in d["edges"]
    if e["relation"] == "links"
    and e["source"] in nodes
    and nodes[e["source"]]["type"] == "Story"
    and e["target"] in ids
}
tagset = {s["id"]: set(s["attrs"]["tags"]) for s in stories}
resumes = {i: {c for c in citers(i) if nodes[c]["type"] == "Resume"} for i in ids}


def pair(a, b):
    """Return the four ways two stories relate."""
    return dict(
        declared=(a, b) in rel,
        out=(a, b) in lnk,
        inn=(b, a) in lnk,
        tags=len(tagset[a] & tagset[b]),
        cocited=len(resumes[a] & resumes[b]),
    )


# --- catalog ---
FULL = [h for h, _ in SHORT]
cat = (
    '<table><tr><th></th><th></th><th></th><th class="grp" colspan="6">bullets per section</th><th></th><th></th><th class="grp" colspan="5">files that reach it, by kind</th></tr>'
    '<tr><th class="b">story</th>'
    + diag(["status", "lines"] + FULL + ["tags", "related stories"] + ORDER)
    + "</tr>"
    + "".join(
        f'<tr><td>{link(s)}</td><td class="st {s["attrs"]["status"]}">{s["attrs"]["status"]}</td><td class="c">{s["attrs"]["total_lines"]}</td>'
        + "".join(
            f'<td class="c"{cls(cell(sec(s["id"], h)))}>{cell(sec(s["id"], h))}</td>'
            for h in FULL
        )
        + f'<td class="c">{len(s["attrs"]["tags"])}</td><td class="c">{len(s["attrs"]["related_stories"] or [])}</td>'
        + "".join(
            f'<td class="c">{sum(nodes[c]["type"] == k for c in citers(s["id"])) or ""}</td>'
            for k in ORDER
        )
        + "</tr>"
        for s in stories
    )
    + "</table>"
)
cat_key = legend(
    [
        ('<span class="none">None</span>', 'the section body is "None."'),
        ('<span class="st complete">complete</span>', "status as written in the story"),
    ]
)

# --- query matrix ---
res = sorted(
    ((s, [t(s) for _, t in TESTS]) for s in stories),
    key=lambda r: (-r[1].count(False), stem(r[0])),
)
qm = (
    '<table><tr><th class="b">story</th>'
    + diag([n for n, _ in TESTS] + ["no answers"])
    + "</tr>"
    + "".join(
        f"<tr><td>{link(s)}</td>"
        + "".join(
            f'<td class="c {"ok" if x else "bad"}">{"✓" if x else "✗"}</td>' for x in r
        )
        + f'<td class="c">{r.count(False)}</td></tr>'
        for s, r in res
    )
    + '<tr class="tot"><td>stories answering no</td>'
    + "".join(
        f'<td class="c">{sum(not r[i] for _, r in res)}</td>' for i in range(len(TESTS))
    )
    + "<td></td></tr></table>"
)
qm_key = legend(
    [
        ('<span class="ok">✓</span>', "yes"),
        ('<span class="bad">&nbsp;✗&nbsp;</span>', "no"),
        ("*", "guessed threshold"),
    ]
)

# --- dependency graph: who reaches each story ---
cit = sorted(
    {c for i in ids for c in citers(i)},
    key=lambda c: (ORDER.index(nodes[c]["type"]), c),
)
ROW, TOP, LX, SX = 26, 20, 330, 720
cy = {c: TOP + ROW * i * len(ids) / len(cit) + 10 for i, c in enumerate(cit)}
sy = {i: TOP + ROW * k + 10 for k, i in enumerate(ids)}
p = []
for i in ids:
    for c in citers(i):
        r = sorted({e["relation"] for e in in_e[i] if e["source"] == c})
        p.append(
            f'<path class="e" data-a="{E(c)}" data-b="{E(i)}" d="M{LX},{cy[c]} C{(LX + SX) / 2},{cy[c]} {(LX + SX) / 2},{sy[i]} {SX},{sy[i]}" stroke="{COL[nodes[c]["type"]]}"><title>{E(c)} —{"/".join(r)}→ {E(nodes[i]["attrs"]["stem"])}</title></path>'
        )
for c in cit:
    p.append(
        f'<g class="n" data-id="{E(c)}"><circle cx="{LX}" cy="{cy[c]}" r="5" fill="{COL[nodes[c]["type"]]}"/><text x="{LX - 10}" y="{cy[c] + 4}" text-anchor="end">{E(short(c))}</text></g>'
    )
for s in stories:
    n = len(citers(s["id"]))
    p.append(
        f'<g class="n" data-id="{E(s["id"])}"><rect x="{SX}" y="{sy[s["id"]] - 10}" width="300" height="20" rx="4" fill="{STFILL[s["attrs"]["status"]]}" stroke="{"#c00" if n == 0 else "#999"}" stroke-width="{2 if n == 0 else 1}"/><text x="{SX + 8}" y="{sy[s["id"]] + 4}">{E(stem(s))} <tspan fill="#777">({n})</tspan></text></g>'
    )
dep = (
    f'<svg width="{SX + 320}" height="{TOP + ROW * len(ids) + 10}">'
    + "".join(p)
    + "</svg>"
)
dep_key = legend(
    [(dot(COL[k]), k) for k in ORDER]
    + STATUS_KEY
    + [
        (box("#fff", "#c00", 2), "reached by no file"),
        ("(n)", "number of files reaching it"),
    ]
)

# --- tag matrix ---
tags = sorted(
    (n for n in d["nodes"] if n["type"] == "Tag"),
    key=lambda t: (t["attrs"]["list"], t["attrs"]["order"]),
)
tagged = {(e["source"], e["target"]) for e in d["edges"] if e["relation"] == "tagged"}
tm = (
    '<table><tr><th class="b">story</th>'
    + diag([t["id"][4:] for t in tags])
    + "</tr>"
    + "".join(
        f"<tr><td>{link(s)}</td>"
        + "".join(
            f'<td class="c">{"●" if (s["id"], t["id"]) in tagged else ""}</td>'
            for t in tags
        )
        + "</tr>"
        for s in stories
    )
    + '<tr class="tot"><td>stories per tag</td>'
    + "".join(
        f'<td class="c">{sum((i, t["id"]) in tagged for i in ids)}</td>' for t in tags
    )
    + "</tr>"
    + "<tr><td>tag list</td>"
    + "".join(f'<td class="c l">{t["attrs"]["list"][0].upper()}</td>' for t in tags)
    + "</tr></table>"
)
tm_key = legend(
    [
        ("●", "story carries the tag"),
        ("R", "role-specific list in tags.yaml"),
        ("A", "always-on list"),
    ]
)

# --- story relations 1: story-by-story matrix ---
SHADE = ["#fff", "#e6effc", "#c7dbf7", "#9fc0f0", "#6f9fe6"]


def sm_cell(a, b):
    """Render one cell of the Relation Matrix."""
    if a == b:
        return '<td class="self"></td>'
    x = pair(a, b)
    g = ("●" if x["declared"] else "") + ("→" if x["out"] else "")
    tip = f"{nodes[a]['attrs']['stem']} × {nodes[b]['attrs']['stem']}: declared {'yes' if x['declared'] else 'no'}; body link {'→' if x['out'] else ''}{'←' if x['inn'] else ''}{'none' if not (x['out'] or x['inn']) else ''}; {x['tags']} shared tags; co-cited on {x['cocited']} resumes"
    co = ""
    return f'<td class="c sm{co}" style="background:{SHADE[min(x["tags"], 4)]}" title="{E(tip)}">{g}</td>'


sm = (
    '<table class="smt"><tr><th class="b">story</th>'
    + diag([stem(s) for s in stories])
    + "</tr>"
    + "".join(
        f"<tr><td>{link(s)}</td>" + "".join(sm_cell(s["id"], t) for t in ids) + "</tr>"
        for s in stories
    )
    + "</table>"
)
sm_key = legend(
    [
        ("●", "declared related (related_stories)"),
        ("→", "row story links to column story in its body"),
    ]
    + [
        (box(SHADE[k], "#ccc"), f"{k}{'+' if k == 4 else ''} shared tags")
        for k in range(1, 5)
    ]
    + [("", "hover a cell for resume co-citation counts")]
)

# --- story relations 2: cluster graph of declared relations ---
connected = [i for i in ids if any((i, j) in rel for j in ids)]
alone = [i for i in ids if i not in connected]
edges = sorted({tuple(sorted(x)) for x in rel})
adj = {
    i: {b for a, b in edges if a == i} | {a for a, b in edges if b == i}
    for i in connected
}
comps, seen = [], set()
for i in connected:
    if i in seen:
        continue
    stack, comp = [i], []
    while stack:
        v = stack.pop()
        if v in seen:
            continue
        seen.add(v)
        comp.append(v)
        stack += adj[v]
    comps.append(sorted(comp))
comps.sort(key=len, reverse=True)


def layout(comp):
    """Place one connected group of stories by a force layout."""
    random.seed(7)
    pos = {i: [random.uniform(-1, 1), random.uniform(-1, 1)] for i in comp}
    es = [e for e in edges if e[0] in pos]
    k = 1.0
    for it in range(800):
        t = 0.2 * (1 - it / 800) + 0.002
        disp = {i: [0.0, 0.0] for i in comp}
        for a in comp:
            for b in comp:
                if a == b:
                    continue
                dx, dy = pos[a][0] - pos[b][0], pos[a][1] - pos[b][1]
                dist = math.hypot(dx, dy) or 1e-3
                f = k * k / dist
                disp[a][0] += dx / dist * f
                disp[a][1] += dy / dist * f
        for a, b in es:
            dx, dy = pos[a][0] - pos[b][0], pos[a][1] - pos[b][1]
            dist = math.hypot(dx, dy) or 1e-3
            f = dist * dist / k
            disp[a][0] -= dx / dist * f
            disp[a][1] -= dy / dist * f
            disp[b][0] += dx / dist * f
            disp[b][1] += dy / dist * f
        for i in comp:
            dx, dy = disp[i]
            dl = math.hypot(dx, dy) or 1e-3
            pos[i][0] += dx / dl * min(dl, t)
            pos[i][1] += dy / dl * min(dl, t)
    return pos


GW, q, xy, ox, oy, rowh = 1360, [], {}, 0, 0, 0
for comp in comps:
    pos = layout(comp)
    n = len(comp)
    bw, bh = (
        (300 + 150 * math.sqrt(n), 120 + 110 * math.sqrt(n)) if n > 2 else (300, 120)
    )
    if ox + bw > GW:
        ox, oy, rowh = 0, oy + rowh, 0
    xs = [v[0] for v in pos.values()]
    ys = [v[1] for v in pos.values()]
    sx = (max(xs) - min(xs)) or 1
    sy_ = (max(ys) - min(ys)) or 1
    for i in comp:
        xy[i] = (
            ox + 130 + (pos[i][0] - min(xs)) / sx * (bw - 260),
            oy + 40 + (pos[i][1] - min(ys)) / sy_ * (bh - 80),
        )
    q.append(
        f'<rect x="{ox + 6}" y="{oy + 6}" width="{bw - 12}" height="{bh - 12}" rx="10" fill="none" stroke="#e5e5e5"/>'
    )
    ox += bw
    rowh = max(rowh, bh)
GH = oy + rowh
for a, b in edges:
    (x1, y1), (x2, y2) = xy[a], xy[b]
    both = (a, b) in lnk or (b, a) in lnk
    q.append(
        f'<line class="e" data-a="{E(a)}" data-b="{E(b)}" x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{"#b33" if both else "#999"}" stroke-width="{2.5 if both else 1.5}"/>'
    )
for i in connected:
    x, y = xy[i]
    s_ = nodes[i]
    q.append(
        f'<g class="n" data-id="{E(i)}"><circle cx="{x:.0f}" cy="{y:.0f}" r="8" fill="{STFILL[s_["attrs"]["status"]]}" stroke="#555"/><text x="{x:.0f}" y="{y - 12:.0f}" text-anchor="middle">{E(s_["attrs"]["stem"])}</text></g>'
    )
AY = GH + 40
q.append(
    f'<text x="10" y="{AY - 8}" fill="#777">no declared relations ({len(alone)}):</text>'
)
for n, i in enumerate(alone):
    x, y = 20 + (n % 4) * 300, AY + 12 + (n // 4) * 24
    s_ = nodes[i]
    q.append(
        f'<g class="n" data-id="{E(i)}"><circle cx="{x}" cy="{y}" r="8" fill="{STFILL[s_["attrs"]["status"]]}" stroke="#555"/><text x="{x + 14}" y="{y + 4}">{E(s_["attrs"]["stem"])}</text></g>'
    )
cg = (
    f'<svg width="{GW}" height="{AY + 24 * math.ceil(len(alone) / 4) + 20}">'
    + "".join(q)
    + "</svg>"
)
cg_key = legend(
    STATUS_KEY
    + [
        (line("#999"), "declared related"),
        (line("#b33"), "declared related, and a body link too"),
        ("", "hover a story to isolate its lines"),
    ]
)


# --- story relations 3: neighborhood, on each card ---
def neighbors(a):
    """Return a story's six nearest stories, ranked, with the reasons."""
    out = []
    for b in ids:
        if b == a:
            continue
        x = pair(a, b)
        score = (
            3 * x["declared"] + 2 * (x["out"] or x["inn"]) + x["tags"] + x["cocited"]
        )
        if not score:
            continue
        why = (
            (["declared"] if x["declared"] else [])
            + (
                [
                    "links to"
                    if x["out"] and not x["inn"]
                    else "linked from"
                    if x["inn"] and not x["out"]
                    else "links both ways"
                ]
                if x["out"] or x["inn"]
                else []
            )
            + ([f"{x['tags']} tags"] if x["tags"] else [])
            + ([f"{x['cocited']} resumes"] if x["cocited"] else [])
        )
        out.append((score, b, why))
    out.sort(key=lambda r: (-r[0], r[1]))
    return out[:6]


def card(s):
    """Render one Story Card."""
    a = s["attrs"]
    rows = ""
    for h in FULL + ["Appendix"]:
        x = sec(s["id"], h)
        v = (
            "None."
            if x.get("is_none")
            else f"{x.get('bullets')} bullets, {x.get('body_lines')} lines"
            + (f", {x['h3_count']} H3" if x.get("h3_count") else "")
        )
        rows += f"<tr><td>{h}</td><td{cls('None' if x.get('is_none') else '')}>{v}</td></tr>"
    by = (
        "".join(
            f"<div>{dot(COL[nodes[c]['type']])} {E(short(c))}</div>"
            for c in citers(s["id"])
        )
        or '<span class="none">none</span>'
    )
    nb = (
        "".join(
            f'<div><a href="#card-{E(nodes[b]["attrs"]["stem"])}">{E(nodes[b]["attrs"]["stem"])}</a> '
            + "".join(f'<span class="chip">{E(w)}</span>' for w in why)
            + "</div>"
            for _, b, why in neighbors(s["id"])
        )
        or '<span class="none">none</span>'
    )
    return (
        f'<div class="card" id="card-{E(a["stem"])}"><h3>{E(a["stem"])}</h3><div class="t">{E(a["title"])}</div>'
        f'<div><span class="st {a["status"]}">{a["status"]}</span> · {a["total_lines"]} lines · resume_eligible {a["resume_eligible"]} · leadership {a["leadership_story"]}</div>'
        f"<table>{rows}</table><div><b>tags</b> {E(', '.join(a['tags']))}</div><div><b>reached by</b> {by}</div><div><b>nearest stories</b> {nb}</div></div>"
    )


cards = '<div class="cards">' + "".join(card(s) for s in stories) + "</div>"
card_key = legend(
    [
        ('<span class="chip">declared</span>', "in related_stories"),
        ('<span class="chip">links to</span>', "body link"),
        ('<span class="chip">2 tags</span>', "shared tags"),
        ('<span class="chip">3 resumes</span>', "cited together on resumes"),
        ("", "nearest six, ranked: declared 3, link 2, each tag or resume 1"),
    ]
)

page = f"""<!doctype html><html><head><meta charset="utf-8"><title>Stories Fact Base Views</title><style>
body{{background:#fff;color:#222;font:13px system-ui,sans-serif;margin:16px}}
nav{{position:sticky;top:0;background:#fff;padding:6px 0;border-bottom:1px solid #ddd;z-index:2}} a{{color:#2f6fdf;text-decoration:none}}
h2{{margin-top:36px;scroll-margin-top:40px}} .wrap{{overflow-x:auto}} code{{background:#f3f3f3;padding:0 3px}}
table{{border-collapse:collapse;font:12px ui-monospace,monospace}} td,th{{border:1px solid #ddd;padding:1px 5px}} td.c{{text-align:center;min-width:16px}}
th.d{{height:170px;position:relative;border:none;padding:0}} th.d span{{position:absolute;bottom:6px;left:50%;transform-origin:0 100%;transform:rotate(-45deg);white-space:nowrap;font-weight:normal}} th.b{{vertical-align:bottom;text-align:left}} th.grp{{border:none;border-bottom:1px solid #999;font-weight:normal;color:#555}}
tr:hover td{{background-color:#eef4ff}} tr.tot td{{font-weight:bold;background:#f3f3f3}} td.l,.none{{color:#aaa}}
.ok{{color:#1a9e5c}} .bad{{color:#c00;background:#fdecec}} .st.complete{{color:#1a9e5c}} .st.needs-detail{{color:#b07800}} .st.draft{{color:#c00}}
.smt td.c{{min-width:22px;width:22px;height:20px;padding:0}} td.self{{background:#333}} td.co,.sw.co{{box-shadow:inset 0 -3px 0 #e8903a}}
svg text{{font:12px ui-monospace,monospace;fill:#222}} .e{{fill:none;stroke-width:1.2;opacity:.5}} .e.hi{{opacity:1;stroke-width:3}} .e.lo{{opacity:.05}} .n{{cursor:pointer}}
.sub{{margin:-8px 0 6px;color:#444}} .kind{{font-size:11px;color:#888;border:1px solid #ddd;border-radius:8px;padding:0 6px;margin-left:6px}} .key{{margin:8px 0 10px;padding:6px 8px;border:1px solid #ddd;border-radius:6px;display:inline-block;background:#fafafa}} .key span{{margin-right:16px;white-space:nowrap}}
.sw{{display:inline-block;width:14px;height:14px;vertical-align:middle;border-radius:3px}} .dot{{display:inline-block;width:10px;height:10px;border-radius:50%;vertical-align:middle}}
.ln{{display:inline-block;width:26px;vertical-align:middle}} .chip{{display:inline-block;background:#eef;border-radius:8px;padding:0 6px;margin-left:3px;font-size:11px;color:#446}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(400px,1fr));gap:12px}} .card{{border:1px solid #ccc;border-radius:6px;padding:8px 10px;scroll-margin-top:40px}}
.card:target{{outline:3px solid #2f6fdf}} .card h3{{margin:0;font-family:ui-monospace,monospace}} .card .t{{color:#555;margin-bottom:4px}} .card table{{margin:6px 0;width:100%}}
</style></head><body>
<h1>Stories fact base, views</h1><p>Generated from <code>stories-fact-base.json</code> alone, story-forge commit <code>{ENV["stamp"]["commit"][:7]}</code>. Local file; nothing is hosted. Click any story name for its card.</p>
<nav><a href="#catalog">Catalog</a> · <a href="#queries">Query Matrix</a> · <a href="#reach">Reach Graph</a> · <a href="#tags">Tag Matrix</a> · <a href="#smatrix">Relation Matrix</a> · <a href="#clusters">Cluster Graph</a> · <a href="#cards">Story Cards</a></nav>
<h2 id="catalog">Catalog</h2><p class="sub">What stories exist, and how much is in each? <span class="kind">catalog</span></p>{cat_key}<div class="wrap">{cat}</div>
<h2 id="queries">Query Matrix</h2><p class="sub">Which stories answer no to which question? <span class="kind">cross-reference matrix</span></p><p>Each column is a yes/no question. Sorted by the number of no answers.</p>{qm_key}<div class="wrap">{qm}</div>
<h2 id="reach">Reach Graph</h2><p class="sub">Which files point at each story? <span class="kind">dependency graph</span></p><p><code>stories/index.md</code> is left out, since it links every story. Hover a node to isolate its edges.</p>{dep_key}<div class="wrap">{dep}</div>
<h2 id="tags">Tag Matrix</h2><p class="sub">Which stories carry which tag? <span class="kind">cross-reference matrix</span></p>{tm_key}<div class="wrap">{tm}</div>
<h2 id="smatrix">Relation Matrix</h2><p class="sub">How does each pair of stories relate? <span class="kind">cross-reference matrix</span></p>{sm_key}<div class="wrap">{sm}</div>
<h2 id="clusters">Cluster Graph</h2><p class="sub">Which stories form families? <span class="kind">dependency graph</span></p><p>Stories drawn near the stories they declare related. The layout is computed, so position means nothing beyond closeness.</p>{cg_key}<div class="wrap">{cg}</div>
<h2 id="cards">Story Cards</h2><p class="sub">Everything about one story, on one card. <span class="kind">interface card</span></p>{card_key}{cards}
<script>
document.querySelectorAll('svg').forEach(svg=>svg.querySelectorAll('.n').forEach(n=>{{const id=n.dataset.id,es=svg.querySelectorAll('.e');
n.onmouseenter=()=>es.forEach(e=>e.classList.add(e.dataset.a===id||e.dataset.b===id?'hi':'lo'));
n.onmouseleave=()=>es.forEach(e=>e.classList.remove('hi','lo'));}}));
</script></body></html>"""
OUT.write_text(page)
print(OUT)
