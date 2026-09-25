"""Load the stories fact base and define the queries asked of it."""

import json
from collections import defaultdict
from pathlib import Path

FB = Path(__file__).resolve().parent.parent / "stories-fact-base.json"
ENV = json.loads(FB.read_text())
d = ENV["payload"]
nodes = {n["id"]: n for n in d["nodes"]}
stories = sorted(
    (n for n in d["nodes"] if n["type"] == "Story"), key=lambda n: n["attrs"]["stem"]
)
secs = defaultdict(dict)
for n in d["nodes"]:
    if n["type"] == "Section":
        secs[n["id"].split("#")[0]][n["attrs"]["heading"]] = n
out_e, in_e = defaultdict(list), defaultdict(list)
for e in d["edges"]:
    out_e[e["source"]].append(e)
    in_e[e["target"]].append(e)
INDEX = "stories/index.md"
CITER = {"Resume", "Projection", "Prep-Unit", "General-Sheet", "File"}


def citers(sid):
    """Return the files outside stories/index.md that point at a story."""
    return sorted(
        {
            e["source"]
            for e in in_e[sid]
            if e["source"] != INDEX and nodes.get(e["source"], {}).get("type") in CITER
        }
    )


def sec(sid, h):
    """Return the attrs of one section of a story, or {} when absent."""
    return secs[sid].get(h, {}).get("attrs", {})


SHORT = [
    ("Situation and Problem", "Sit"),
    ("Actions", "Act"),
    ("Quantitative Results", "Qnt"),
    ("Qualitative Results", "Qlt"),
    ("To-dos", "Todo"),
    ("Notes", "Note"),
]


def cell(a):
    """Show a section as its bullet count, or None when its body is "None."."""
    return "None" if a.get("is_none") else str(a.get("bullets", "?"))


TESTS = [
    ("status-complete", lambda s: s["attrs"]["status"] == "complete"),
    (
        "quant-not-none",
        lambda s: not sec(s["id"], "Quantitative Results").get("is_none"),
    ),
    ("todos-empty", lambda s: sec(s["id"], "To-dos").get("is_none")),
    ("notes-empty", lambda s: sec(s["id"], "Notes").get("is_none")),
    (
        "sit>=2 bullets*",
        lambda s: sec(s["id"], "Situation and Problem").get("bullets", 0) >= 2,
    ),
    ("act>=3 bullets*", lambda s: sec(s["id"], "Actions").get("bullets", 0) >= 3),
]
W = max(len(s["attrs"]["stem"]) for s in stories)
STATUS = {"complete": "complete", "needs-detail": "needs-dtl", "draft": "draft"}
