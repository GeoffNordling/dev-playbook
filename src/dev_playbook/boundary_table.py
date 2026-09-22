"""Write the boundary table, ``standards/boundaries.yaml``, and lint it.

The boundary table says where each check runs. It has one row per address the
verifier table (``standards/verifiers.yaml``) names, a first-party detector by
path or a dependency by its hook id or name, valued by the gates that run it,
in a fixed order drawn from four:

- ``commit`` — the pre-commit stage, at ``git commit``;
- ``push`` — the pre-push stage, at ``git push``, which runs ``make check``;
- ``ci`` — a workflow under ``.github/workflows/``;
- ``on-demand`` — no gate; the check is a registered ungated audit the user
  runs by hand (``playbook_lint.UNGATED_AUDITS``).

Nothing is hand-maintained. The table is derived from the wiring itself:
``.pre-commit-config.yaml`` with each hook's stages, ``make -n check`` for
the pre-push hook's recipe, each workflow's ``run`` steps with their ``SKIP``,
and the ungated registry. The ``playbook-lint`` hook expands to its roster and
the manifest validation it runs where a manifest exists. The same derivation is
the lint (standards/standard/detectors.md, The boundary table): a committed
table that differs from a fresh write is a finding, and so is an address that
no gate runs and no registration excuses, or one registered ungated that a
gate runs after all.

Two modes, keyed like the verifier table on the canonical consumer template.
In **dev-playbook mode** the rows are the roster, the registered audits, and
the dependency addresses. In **consumer mode** the rows are the repo's own
``scripts/`` hooks; the union with dev-playbook's table is read from the
pinned clone, as the verifier table is.

Output:
    stdout — one finding per line, ``file: standard.rule message``.
    stderr — one readable summary line.
    exit   — 0 clean, 1 findings, 2 cannot run.

Usage:
    boundary-table [directory]           lint: derive, compare, never write
    boundary-table --write [directory]   derive and write the table
    boundary-table --list-rules
"""

import argparse
import subprocess
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from dev_playbook import gitrepo
from dev_playbook.findings import print_rules, render
from dev_playbook.playbook_lint import (
    DETECTORS,
    MANIFEST,
    UNGATED_AUDITS,
    VALIDATE_MANIFEST,
)
from dev_playbook.verifier_table import (
    DEPENDENCY_RULES,
    LOCAL_CONFIG,
    CannotRun,
    dev_playbook_mode,
    hooks_of,
    local_detectors,
    yaml_mapping,
)

THE_BOUNDARY_TABLE = "standard.the-boundary-table-generated-from-the-wiring"
EVERY_ADDRESS_RUNS_SOMEWHERE = "standard.every-address-runs-somewhere"

RULES = (THE_BOUNDARY_TABLE, EVERY_ADDRESS_RUNS_SOMEWHERE)

TABLE = "standards/boundaries.yaml"
WORKFLOWS = ".github/workflows"
AGGREGATE_HOOK = "playbook-lint"
VALIDATE_MANIFEST_ADDRESS = "pre-commit validate-manifest"

COMMIT = "commit"
PUSH = "push"
CI = "ci"
ON_DEMAND = "on-demand"
GATES = (COMMIT, PUSH, CI)

# pre-commit's stage names, current and legacy, to the gate each is.
STAGE_GATES = {"pre-commit": COMMIT, "commit": COMMIT, "pre-push": PUSH, "push": PUSH}

# The commands a Makefile recipe or a workflow step runs, by the words that
# open them once a ``uv run`` or ``uvx`` prefix is dropped, to the address
# each is. ``pre-commit run`` and ``make`` are expanded, not mapped, below.
COMMANDS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("ruff", "format"), "ruff-format"),
    (("ruff", "check"), "ruff-check"),
    (("mypy",), "mypy"),
    (("shellcheck",), "shellcheck"),
    (("shfmt",), "shfmt"),
    (("pre-commit", "validate-manifest"), VALIDATE_MANIFEST_ADDRESS),
)

HEADER = """\
# The boundary table: every check address the verifier table names, and the
# gates that run it. commit is the pre-commit stage at `git commit`; push is
# the pre-push stage at `git push`, which runs `make check`; ci is a workflow
# under .github/workflows/; on-demand is a registered audit no gate runs.
# Written by scripts/boundary-table, which also fails when this file and a
# fresh write differ. Regenerate with: scripts/boundary-table --write
"""


@dataclass(frozen=True)
class Finding:
    """One nonconformance: a repo-relative location, a rule id, and a message."""

    file: str
    rule: str
    message: str

    def render(self) -> str:
        """The finding as one GNU-format line."""
        return render(self.file, self.rule, self.message)


@dataclass(frozen=True)
class Table:
    """The derived rows and the findings the derivation raised."""

    rows: dict[str, tuple[str, ...]]
    findings: list[Finding]


# --- the rows ---------------------------------------------------------------


def addresses(root: Path) -> set[str]:
    """The addresses the verifier table names for ``root``: the table's rows.

    The same sources the verifier table draws its addresses from: the roster
    it asks, as ``scripts/<name>``, and in dev-playbook mode the dependency
    map's addresses.
    """
    if dev_playbook_mode(root):
        names = {*DETECTORS, *UNGATED_AUDITS}
        return {f"scripts/{name}" for name in names} | set(DEPENDENCY_RULES)
    return {f"scripts/{name}" for name in local_detectors(root)}


# --- the wiring -------------------------------------------------------------


def hook_gates(hook: Mapping, config: Mapping) -> set[str]:
    """The gates a pre-commit hook fires at: its stages, else the config's, else all."""
    stages = hook.get("stages") or config.get("default_stages") or list(STAGE_GATES)
    return {STAGE_GATES[str(s)] for s in stages if str(s) in STAGE_GATES}


def hook_addresses(hook: Mapping, root: Path, skip: frozenset[str]) -> set[str]:
    """The addresses one pre-commit hook runs.

    The aggregate hook expands to its roster; a ``make`` entry expands through
    the Makefile; a ``scripts/`` entry is that script; any other hook is its
    own id, which is an address only where the verifier table names it. A
    hook whose id is in ``skip`` runs nothing.
    """
    hook_id = str(hook["id"])
    if hook_id in skip:
        return set()
    if hook_id == AGGREGATE_HOOK:
        return aggregate_addresses(root, skip)
    entry = str(hook.get("entry", "")).split()
    if entry and entry[0] == "make":
        return make_addresses(root, entry[1:], skip)
    if entry and entry[0].startswith("scripts/"):
        return {entry[0]}
    return {hook_id}


def aggregate_addresses(root: Path, skip: frozenset[str]) -> set[str]:
    """What ``playbook-lint`` runs: its roster less ``SKIP``, and the manifest check."""
    out = {f"scripts/{name}" for name in DETECTORS if name not in skip}
    if (root / MANIFEST).is_file() and VALIDATE_MANIFEST not in skip:
        out.add(VALIDATE_MANIFEST_ADDRESS)
    return out


def commit_stage_addresses(root: Path, skip: frozenset[str]) -> set[str]:
    """What ``pre-commit run`` runs: every hook that fires at the commit stage."""
    out: set[str] = set()
    for config, hook in _config_hooks(root):
        if COMMIT in hook_gates(hook, config):
            out |= hook_addresses(hook, root, skip)
    return out


def make_addresses(root: Path, targets: list[str], skip: frozenset[str]) -> set[str]:
    """The addresses ``make <targets>`` runs, read from what make would execute."""
    try:
        result = subprocess.run(
            ["make", "-n", *targets],
            capture_output=True,
            text=True,
            cwd=root,
            timeout=60,
            env=gitrepo.no_git_env(),
        )
    except (OSError, subprocess.TimeoutExpired) as err:
        raise CannotRun(f"make -n {' '.join(targets)} failed: {err}") from err
    if result.returncode != 0:
        raise CannotRun(
            f"make -n {' '.join(targets)} exited {result.returncode}: "
            f"{result.stderr.strip()}"
        )
    out: set[str] = set()
    for line in result.stdout.splitlines():
        out |= command_addresses(line, root, skip)
    return out


def command_addresses(line: str, root: Path, skip: frozenset[str]) -> set[str]:
    """The addresses one command line runs; a command that is no check runs none."""
    words = line.split()
    if words[:2] == ["uv", "run"]:
        words = words[2:]
    elif words[:1] == ["uvx"]:
        words = words[1:]
    if not words:
        return set()
    if words[:2] == ["pre-commit", "run"]:
        return commit_stage_addresses(root, skip)
    if words[0] == "make":
        return make_addresses(root, words[1:], skip)
    if words[0].startswith("scripts/"):
        return {words[0]}
    for prefix, address in COMMANDS:
        if tuple(words[: len(prefix)]) == prefix:
            return {address}
    return set()


def ci_addresses(root: Path) -> set[str]:
    """The addresses the workflows run: each ``run`` step, under its ``SKIP``."""
    out: set[str] = set()
    workflows = root / WORKFLOWS
    if not workflows.is_dir():
        return out
    for path in sorted(workflows.glob("*.yml")):
        data = yaml_mapping(path)
        top_env = _env(data)
        for job in (data.get("jobs") or {}).values():
            if not isinstance(job, dict):
                continue
            job_env = {**top_env, **_env(job)}
            for step in job.get("steps") or []:
                if not isinstance(step, dict) or "run" not in step:
                    continue
                env = {**job_env, **_env(step)}
                skip = frozenset(
                    n.strip() for n in str(env.get("SKIP", "")).split(",") if n.strip()
                )
                for line in str(step["run"]).splitlines():
                    out |= command_addresses(line, root, skip)
    return out


def _env(node: Mapping) -> dict:
    env = node.get("env")
    return dict(env) if isinstance(env, dict) else {}


def _config_hooks(root: Path) -> list[tuple[Mapping, Mapping]]:
    """Every hook of the repo's pre-commit config, paired with the config."""
    config = root / LOCAL_CONFIG
    if not config.is_file():
        return []
    data = yaml_mapping(config)
    return [(data, hook) for hook in hooks_of(config)]


# --- the derivation ---------------------------------------------------------


def derive(root: Path) -> Table:
    """Derive the table for ``root`` and the findings that dispute it.

    Every address gets a row. The commit and push columns come from the
    pre-commit config's hooks by stage, the ci column from the workflows. An
    address at no gate is ``on-demand`` where it is a registered ungated
    audit, and a finding otherwise; a registered audit a gate runs is a
    finding too, since the registration then lies.
    """
    at: dict[str, set[str]] = {gate: set() for gate in GATES}
    for config, hook in _config_hooks(root):
        for gate in hook_gates(hook, config):
            at[gate] |= hook_addresses(hook, root, frozenset())
    at[CI] = ci_addresses(root)
    registered = {f"scripts/{name}" for name in UNGATED_AUDITS}

    rows: dict[str, tuple[str, ...]] = {}
    findings: list[Finding] = []
    for address in sorted(addresses(root)):
        gates = tuple(gate for gate in GATES if address in at[gate])
        if address in registered and gates:
            findings.append(
                Finding(
                    address,
                    EVERY_ADDRESS_RUNS_SOMEWHERE,
                    f"is registered as an ungated audit but runs at {gates[0]}",
                )
            )
        elif address in registered:
            gates = (ON_DEMAND,)
        elif not gates:
            findings.append(
                Finding(
                    address,
                    EVERY_ADDRESS_RUNS_SOMEWHERE,
                    "runs at no gate and is not a registered ungated audit",
                )
            )
        rows[address] = gates
    return Table(rows, findings)


def render_table(rows: Mapping[str, tuple[str, ...]]) -> str:
    """The table as the text the file holds: a header, then one row per address."""
    body = "".join(
        f"{address}: [{', '.join(gates)}]\n" for address, gates in sorted(rows.items())
    )
    return HEADER + body


# --- the walk ---------------------------------------------------------------


def audit(root: Path, *, write: bool = False) -> list[Finding]:
    """Derive the table and compare it with the committed one; write on request.

    A repo with no address and no table is clean by construction. Otherwise
    the committed text must equal a fresh render; with ``write`` the render
    is written instead of compared, and the other findings still stand.
    """
    table = derive(root)
    path = root / TABLE
    if not table.rows and not path.is_file():
        return table.findings
    text = render_table(table.rows)
    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return table.findings
    findings = list(table.findings)
    if not path.is_file():
        findings.append(
            Finding(TABLE, THE_BOUNDARY_TABLE, "is missing; run boundary-table --write")
        )
    elif path.read_text(encoding="utf-8") != text:
        findings.append(
            Finding(
                TABLE,
                THE_BOUNDARY_TABLE,
                "differs from a fresh write; run boundary-table --write",
            )
        )
    return findings


def main(argv: list[str] | None = None) -> int:
    """Derive the table, lint or write it, print findings; return the exit code."""
    parser = argparse.ArgumentParser(
        prog="boundary-table",
        description="Write standards/boundaries.yaml, or fail where it disagrees.",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="repository root (default: current directory)",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="write the derived table instead of comparing it with the file",
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="print the rule ids this detector can emit, one per line, and exit",
    )
    args = parser.parse_args(argv)
    if args.list_rules:
        return print_rules(RULES)
    root = Path(args.directory).resolve()

    try:
        findings = audit(root, write=args.write)
    except CannotRun as err:
        print(f"boundary-table: cannot run: {err}", file=sys.stderr)
        return 2

    for f in sorted(findings, key=lambda f: (f.file, f.rule, f.message)):
        print(f.render())
    if findings:
        print(f"boundary-table: {len(findings)} finding(s)", file=sys.stderr)
        return 1
    print(f"boundary-table: {'written' if args.write else 'clean'}", file=sys.stderr)
    return 0
