#!/usr/bin/env python3
"""List every instance of every kind in a simulated fact base.

Reads the recognition rule of each Kind node in <run>/slices/*/facts.json,
applies it to the target's tracked files, and writes <run>/instances.json:
the files each kind matches, the files two kinds both claim, the files no
kind claims, and the kinds whose rule matched nothing or cannot be expressed.

Usage: list_instances.py <target> <run>
"""

import json
import re
import subprocess
import sys
from pathlib import Path


def glob_to_regex(glob: str) -> re.Pattern[str]:
    """Compile a glob where * stays in one folder and ** crosses folders."""
    out = ""
    i = 0
    while i < len(glob):
        if glob.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif glob.startswith("**", i):
            out += ".*"
            i += 2
        elif glob[i] == "*":
            out += "[^/]*"
            i += 1
        elif glob[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(glob[i])
            i += 1
    return re.compile(out + r"\Z")


def frontmatter(path: Path) -> dict[str, str]:
    """Top-level scalar keys of a YAML frontmatter block, as strings."""
    try:
        lines = path.read_text(errors="replace").splitlines()
    except IsADirectoryError, FileNotFoundError:
        return {}
    if not lines or lines[0].strip() != "---":
        return {}
    keys: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            keys[m.group(1)] = m.group(2).strip().strip("'\"")
    return keys


def main() -> None:
    """Apply every recognition rule and write <run>/instances.json."""
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    target, run = Path(sys.argv[1]), Path(sys.argv[2])
    partition = json.loads((run / "partition.json").read_text())
    scope = partition.get("scope") or ["all"]

    tracked = subprocess.run(
        ["git", "-C", str(target), "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    if scope != ["all"]:
        prefixes = [s.rstrip("/") + "/" for s in scope]
        tracked = [f for f in tracked if any(f.startswith(p) for p in prefixes)]

    kinds: dict[str, dict] = {}
    for facts_path in sorted(run.glob("slices/*/facts.json")):
        facts = json.loads(facts_path.read_text())
        for node in facts["nodes"]:
            if node.get("type") != "Kind":
                continue
            if node["id"] in kinds:
                sys.exit(
                    f"{node['id']} is described by two slices: {kinds[node['id']]['slice']} and {facts['slice']}"
                )
            kinds[node["id"]] = {
                "slice": facts["slice"],
                "rule": node.get("attrs", {}).get("recognise"),
            }

    matches: dict[str, list[str]] = {}
    unexpressible: dict[str, str] = {}
    for kind, info in kinds.items():
        rule = info["rule"]
        if not rule or rule.get("expressible") is False:
            unexpressible[kind] = (rule or {}).get("why", "no rule given")
            continue
        include = glob_to_regex(rule["glob"])
        excludes = [glob_to_regex(g) for g in rule.get("exclude", [])]
        want = rule.get("frontmatter", {})
        hits = []
        for f in tracked:
            if not include.match(f) or any(x.match(f) for x in excludes):
                continue
            if want:
                fm = frontmatter(target / f)
                if any(fm.get(k) != str(v) for k, v in want.items()):
                    continue
            hits.append(f)
        matches[kind] = hits

    claimed: dict[str, list[str]] = {}
    for kind, hits in matches.items():
        for f in hits:
            claimed.setdefault(f, []).append(kind)

    report = {
        "targetCommit": partition.get("targetCommit"),
        "scope": scope,
        "trackedInScope": len(tracked),
        "counts": {k: len(v) for k, v in sorted(matches.items())},
        "empty": sorted(k for k, v in matches.items() if not v),
        "unexpressible": unexpressible,
        "overlaps": {f: ks for f, ks in sorted(claimed.items()) if len(ks) > 1},
        "orphans": sorted(f for f in tracked if f not in claimed),
        "instances": {k: v for k, v in sorted(matches.items())},
    }
    (run / "instances.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"{len(kinds)} kinds, {len(tracked)} files in scope: "
        f"{sum(len(v) for v in matches.values())} matches, {len(report['empty'])} empty rules, "
        f"{len(unexpressible)} unexpressible, {len(report['overlaps'])} overlaps, "
        f"{len(report['orphans'])} orphans -> {run / 'instances.json'}"
    )


if __name__ == "__main__":
    main()
