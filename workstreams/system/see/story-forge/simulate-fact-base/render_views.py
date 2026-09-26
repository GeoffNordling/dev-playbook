"""Render one self-contained HTML page of views over a run's fact base.

Usage: python3 render_views.py <run dir> <target root> <out .html>

Reads <run>/fact-base.json and <run>/instances.json. Writes one page with
four tabs (Map, Lineage, Flow, Checks) and a shared detail panel. All
layout is done in the page's own script; the page loads nothing from the
network.
"""

import json
import sys
from pathlib import Path

AREAS = {
    "stories": "Stories",
    "resume-standards": "Resume and Standards",
    "role-postings": "Role Postings",
    "interview-loops": "Interview Loops",
    "prep-units": "Prep Units",
    "career": "Career",
    "unemployment-benefits": "Unemployment Benefits",
    "skills-and-scripts": "Skills and Scripts",
    "code-and-config": "Code and Config",
    "indexes-and-top-level": "Indexes and Top Level",
}


def load(run: Path) -> dict:
    """Join the fact base and the instance lists into the page's data."""
    fb = json.loads((run / "fact-base.json").read_text())
    inst = json.loads((run / "instances.json").read_text())
    nodes = fb["payload"]["nodes"]
    for n in nodes:
        if n["type"] == "Kind":
            slice_id = n["attrs"]["slice"]
            if slice_id not in AREAS:
                raise SystemExit(f"kind {n['id']} has unknown slice {slice_id!r}")
            n["attrs"]["files"] = inst["instances"].get(n["id"], [])
            if n["id"] in inst["unexpressible"]:
                n["attrs"]["unexpressible"] = inst["unexpressible"][n["id"]]
    return {
        "title": fb["title"],
        "commit": fb["stamp"]["commit"],
        "areas": AREAS,
        "nodes": nodes,
        "edges": fb["payload"]["edges"],
        "orphans": inst["orphans"],
    }


def main() -> None:
    """Read the run, write the page."""
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    run, target, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    data = load(run)
    data["targetRoot"] = str(target.resolve())
    page = (Path(__file__).parent / "views_template.html").read_text()
    blob = json.dumps(data).replace("</", "<\\/")
    out.write_text(page.replace("/*DATA*/null", blob))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
