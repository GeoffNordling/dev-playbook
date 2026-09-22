"""Write the verifier table, ``standards/verifiers.yaml``, and lint it.

The verifier table maps every rule id declared under ``standards/`` to the
address of the one check that decides it, or to null where no check does. A
rule is declared by the trailer under its heading in a Standard at
``standards/<name>/<topic>.md``: a code span holding ``<name>.<slug>``, then
``· deterministic`` or ``· stochastic``.
An address is a first-party detector by path, ``scripts/repo-lint``; a
dependency by its pinned pre-commit hook id, ``ruff-format``; or a dependency
by its ``pyproject.toml`` name and the subcommand it runs, ``mypy``,
``pre-commit validate-manifest``.

Nothing is hand-maintained. The table is derived: the rule ids from the
trailers, the detector rows from each detector's ``--list-rules``, the
dependency rows from ``DEPENDENCY_RULES`` below. The same derivation is the
lint (standards/standard/detectors.md, The verifier table): a detector that
emits an id no rule heading declares, an id two detectors both emit, a
dependency address that resolves to nothing, or a committed table that differs
from a fresh write is a finding, and a trailer that cannot be read is a run
that cannot proceed.

Two modes, keyed like standards-lint on the canonical consumer template, which
only the hook repo carries. In **dev-playbook mode** the detectors asked are
the playbook-lint roster and the registered ungated audits, and the dependency
rows apply. In **consumer mode** the detectors asked are the repo's own
``scripts/`` hooks, and the table holds only that repo's rules: a row naming a
rule dev-playbook's shipped table carries is a finding, so the two tables union
the way the type registry does.

Output:
    stdout — one finding per line, ``file: standard.rule message``.
    stderr — one readable summary line.
    exit   — 0 clean, 1 findings, 2 cannot run.

Usage:
    verifier-table [directory]           lint: derive, compare, never write
    verifier-table --write [directory]   derive and write the table
    verifier-table --list-rules
"""

import argparse
import re
import subprocess
import sys
import tomllib
from collections.abc import Callable, Mapping
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import yaml

from dev_playbook import gitrepo, md
from dev_playbook.findings import print_rules, render
from dev_playbook.playbook_lint import DETECTORS, UNGATED_AUDITS

# The dev-playbook checkout this module ships in: the pre-commit clone in a
# consumer repo, the working tree when dev-playbook dogfoods it. A consumer's
# run reads the shipped table here.
HOOK_REPO_ROOT = Path(__file__).resolve().parents[2]

THE_VERIFIER_TABLE = "standard.the-verifier-table"
AN_EMITTED_ID_IS_A_RULE_HEADING = "standard.an-emitted-id-is-a-rule-heading"
AN_ADDRESS_EXISTS = "standard.an-address-exists"
A_CONSUMER_ADDS_ONLY_ITS_OWN_RULES = "standard.a-consumer-adds-only-its-own-rules"

RULES = (
    THE_VERIFIER_TABLE,
    AN_EMITTED_ID_IS_A_RULE_HEADING,
    AN_ADDRESS_EXISTS,
    A_CONSUMER_ADDS_ONLY_ITS_OWN_RULES,
)

STANDARDS = "standards"
TABLE = "standards/verifiers.yaml"
CANONICAL_CONFIG = "standards/build/canonical/.pre-commit-config.yaml"
LOCAL_CONFIG = ".pre-commit-config.yaml"
PYPROJECT = "pyproject.toml"
DETERMINISTIC = "deterministic"

# The rules a dependency decides, by the address the table prints. The ids
# are checked against the declared rules like a detector's --list-rules, and
# each address against the repo's hooks and dependencies.
DEPENDENCY_RULES: Mapping[str, tuple[str, ...]] = {
    "pre-commit validate-manifest": ("distribution.a-valid-manifest",),
    "ruff-check": ("python.every-definition-carries-a-docstring",),
    "ruff-format": ("python.formatted-by-ruff-format",),
    "shellcheck": ("shell.shellcheck-clean",),
    "shfmt": ("shell.formatted-by-shfmt",),
}

HEADER = """\
# The verifier table: every rule id declared under standards/, and the address
# of the check that decides it, or null where no check does. Written by
# scripts/verifier-table, which also fails when this file and a fresh write
# differ. Regenerate with: scripts/verifier-table --write
"""

_HEADING = re.compile(r"^(#{2,6})\s+(.+?)\s*#*\s*$")
_TRAILER = re.compile(
    r"^`([a-z][a-z0-9-]*\.[a-z0-9][a-z0-9-]*)` · (deterministic|stochastic)$"
)
_DEPENDENCY_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*")


class CannotRun(Exception):
    """A precondition the generator cannot derive past; surfaces as exit 2."""


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
class Rule:
    """One declared rule: its id, kind, and the file and line of its trailer."""

    id: str
    kind: str
    file: str
    line: int


ListRules = Callable[[str, Path], list[str]]


# --- the declared rules -----------------------------------------------------


def declared_rules(root: Path) -> dict[str, Rule]:
    """Every rule the trailers under ``standards/`` declare, by id.

    A trailer names its own heading: the id is ``<name>.<slug>`` for the
    directory ``standards/<name>/`` and the GitHub slug of the nearest
    heading above it. A trailer whose id says otherwise, one with no heading
    above it, or an id declared twice cannot be tabled, so each raises
    ``CannotRun`` rather than becoming a row the table would then vouch for.
    """
    rules: dict[str, Rule] = {}
    for rel in _standards_files(root):
        name = rel.split("/")[1]
        heading: str | None = None
        for line_no, line in md.content_lines(root / rel):
            if m := _HEADING.match(line):
                heading = m.group(2)
                continue
            t = _TRAILER.match(line.strip())
            if not t:
                continue
            rule_id, kind = t.groups()
            if heading is None:
                raise CannotRun(f"{rel}:{line_no}: trailer `{rule_id}` has no heading")
            expected = f"{name}.{md.github_slug(heading)}"
            if rule_id != expected:
                raise CannotRun(
                    f"{rel}:{line_no}: trailer `{rule_id}` under the heading "
                    f"{heading!r} should read `{expected}`"
                )
            if rule_id in rules:
                first = rules[rule_id]
                raise CannotRun(
                    f"{rel}:{line_no}: `{rule_id}` is already declared at "
                    f"{first.file}:{first.line}"
                )
            rules[rule_id] = Rule(rule_id, kind, rel, line_no)
    return rules


def _standards_files(root: Path) -> list[str]:
    """The tracked Markdown files under ``standards/<name>/``, repo-relative."""
    try:
        files = gitrepo.git_files(root)
    except subprocess.CalledProcessError as err:
        raise CannotRun(f"{root} is not a git checkout") from err
    return [
        rel
        for rel in files
        if rel.startswith(f"{STANDARDS}/")
        and rel.endswith(".md")
        and rel.count("/") >= 2
    ]


# --- the checks asked -------------------------------------------------------


def dev_playbook_mode(root: Path) -> bool:
    """Whether ``root`` is dev-playbook: it carries the canonical template."""
    return (root / CANONICAL_CONFIG).is_file()


def roster(root: Path) -> tuple[str, ...]:
    """The first-party detectors the table asks, by ``scripts/`` name.

    dev-playbook's are the playbook-lint roster and the registered ungated
    audits; a consumer's are the ``scripts/`` hooks of its own pre-commit
    config, the same set standards-lint's hosting pattern holds it to.
    """
    if dev_playbook_mode(root):
        return tuple(sorted({*DETECTORS, *UNGATED_AUDITS}))
    return tuple(sorted(local_detectors(root)))


def local_detectors(root: Path) -> set[str]:
    """Hook ids of the repo's own config whose entry is a ``scripts/`` path."""
    config = root / LOCAL_CONFIG
    if not config.is_file():
        return set()
    return {
        str(hook["id"])
        for hook in hooks_of(config)
        if str(hook.get("entry", "")).startswith("scripts/")
    }


def _hook_ids(root: Path) -> set[str]:
    """Every hook id the repo's own pre-commit config names."""
    config = root / LOCAL_CONFIG
    if not config.is_file():
        return set()
    return {str(hook["id"]) for hook in hooks_of(config)}


def hooks_of(config: Path) -> list[dict]:
    """Every hook mapping of a pre-commit config that carries an id."""
    return [
        hook
        for repo in yaml_mapping(config).get("repos") or []
        if isinstance(repo, dict)
        for hook in repo.get("hooks") or []
        if isinstance(hook, dict) and "id" in hook
    ]


def _dependency_names(root: Path) -> set[str]:
    """Every dependency ``pyproject.toml`` declares, project and groups alike."""
    pyproject = root / PYPROJECT
    if not pyproject.is_file():
        return set()
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    specs: list[object] = list(data.get("project", {}).get("dependencies", []))
    for group in data.get("dependency-groups", {}).values():
        specs.extend(group)
    names: set[str] = set()
    for spec in specs:
        if isinstance(spec, str) and (m := _DEPENDENCY_NAME.match(spec)):
            names.add(m.group(0).lower())
    return names


def yaml_mapping(path: Path) -> dict:
    """The YAML file as a mapping; anything else cannot be read."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise CannotRun(f"{path.name} is not a YAML mapping")
    return data


def list_rules_via_subprocess(name: str, root: Path) -> list[str]:
    """Run ``scripts/<name> --list-rules`` in ``root`` and return its ids.

    The detector's own ``uv run --script`` shebang resolves its dependencies.
    Raises ``CannotRun`` when the script is absent or does not answer the flag.
    A git gate can export an absolute ``GIT_DIR``; ``gitrepo.no_git_env()``
    scrubs it so a spawned detector answers for the repo it is given.
    """
    script = root / "scripts" / name
    if not script.is_file():
        raise CannotRun(f"no scripts/{name} to ask --list-rules")
    try:
        result = subprocess.run(
            [str(script), "--list-rules"],
            capture_output=True,
            text=True,
            cwd=root,
            timeout=60,
            env=gitrepo.no_git_env(),
        )
    except OSError as err:
        raise CannotRun(f"scripts/{name} --list-rules failed: {err}") from err
    except subprocess.TimeoutExpired as err:
        raise CannotRun(f"scripts/{name} --list-rules timed out") from err
    if result.returncode != 0:
        raise CannotRun(f"scripts/{name} does not answer --list-rules")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _ask_all(
    names: tuple[str, ...], root: Path, list_rules: ListRules
) -> dict[str, list[str]]:
    """Each detector's emitted ids, asked concurrently, in name order."""
    with ThreadPoolExecutor(max_workers=max(1, len(names))) as pool:
        answers = list(pool.map(lambda name: list_rules(name, root), names))
    return dict(zip(names, answers, strict=True))


# --- the derivation ---------------------------------------------------------


@dataclass(frozen=True)
class Table:
    """The derived rows and the findings the derivation raised."""

    rows: dict[str, str | None]
    findings: list[Finding]


def derive(
    root: Path,
    list_rules: ListRules = list_rules_via_subprocess,
    *,
    dependencies: Mapping[str, tuple[str, ...]] = DEPENDENCY_RULES,
    upstream_root: Path = HOOK_REPO_ROOT,
) -> Table:
    """Derive the table for ``root`` and the findings that dispute it.

    Every declared rule gets a row. A detector's row is ``scripts/<name>``;
    a dependency's is its address; the rest are null. An id no rule declares,
    a stochastic id a check claims, and an id two checks claim are findings
    under the emitted-id rule; a dependency address the repo does not carry
    is one under the address rule; in consumer mode a row naming an upstream
    rule is one under the consumer rule. The rows are still complete, so a
    ``--write`` after a red run leaves a table that matches the next run.
    """
    rules = declared_rules(root)
    is_dev_playbook = dev_playbook_mode(root)
    findings: list[Finding] = []
    rows: dict[str, str | None] = dict.fromkeys(sorted(rules))

    claims: dict[str, list[str]] = {}
    for name, ids in _ask_all(roster(root), root, list_rules).items():
        claims[f"scripts/{name}"] = ids
    if is_dev_playbook:
        known = _hook_ids(root) | _dependency_names(root)
        if (root / LOCAL_CONFIG).is_file():
            known.add("pre-commit")  # the tool that config file is for
        for address, rule_ids in dependencies.items():
            claims[address] = list(rule_ids)
            if address.split()[0] not in known:
                findings.append(
                    Finding(
                        TABLE,
                        AN_ADDRESS_EXISTS,
                        f"{address} is no hook id of {LOCAL_CONFIG} and no "
                        f"dependency of {PYPROJECT}",
                    )
                )

    decided_by: dict[str, str] = {}
    for address in sorted(claims):
        for rule_id in sorted(set(claims[address])):
            if rule_id not in rules:
                findings.append(
                    Finding(
                        address,
                        AN_EMITTED_ID_IS_A_RULE_HEADING,
                        f"emits {rule_id}, which no rule heading under "
                        f"{STANDARDS}/ declares",
                    )
                )
            elif rules[rule_id].kind != DETERMINISTIC:
                findings.append(
                    Finding(
                        address,
                        AN_EMITTED_ID_IS_A_RULE_HEADING,
                        f"emits {rule_id}, which {rules[rule_id].file} declares "
                        f"{rules[rule_id].kind}",
                    )
                )
            elif rule_id in decided_by:
                findings.append(
                    Finding(
                        address,
                        AN_EMITTED_ID_IS_A_RULE_HEADING,
                        f"emits {rule_id}, which {decided_by[rule_id]} also emits",
                    )
                )
            else:
                decided_by[rule_id] = address
                rows[rule_id] = address

    if not is_dev_playbook and rows:
        upstream = _shipped_table(upstream_root)
        for rule_id in sorted(set(rows) & set(upstream)):
            findings.append(
                Finding(
                    rules[rule_id].file,
                    A_CONSUMER_ADDS_ONLY_ITS_OWN_RULES,
                    f"declares {rule_id}, a rule dev-playbook's table carries",
                )
            )
    return Table(rows, findings)


def _shipped_table(upstream_root: Path) -> dict[str, str | None]:
    """dev-playbook's committed table, read from the clone this hook ships in."""
    path = upstream_root / TABLE
    if not path.is_file():
        raise CannotRun(f"the hook repo at {upstream_root} carries no {TABLE}")
    return yaml_mapping(path)


def render_table(rows: Mapping[str, str | None]) -> str:
    """The table as the text the file holds: a header, then one row per id."""
    body = "".join(
        f"{rule_id}: {'null' if address is None else address}\n"
        for rule_id, address in sorted(rows.items())
    )
    return HEADER + body


# --- the walk ---------------------------------------------------------------


def audit(
    root: Path,
    list_rules: ListRules = list_rules_via_subprocess,
    *,
    write: bool = False,
    dependencies: Mapping[str, tuple[str, ...]] = DEPENDENCY_RULES,
    upstream_root: Path = HOOK_REPO_ROOT,
) -> list[Finding]:
    """Derive the table and compare it with the committed one; write on request.

    A repo that declares no rule and carries no table is clean by
    construction. Otherwise the committed text must equal a fresh render;
    with ``write`` the render is written instead of compared, and the other
    findings still stand.
    """
    table = derive(
        root, list_rules, dependencies=dependencies, upstream_root=upstream_root
    )
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
            Finding(TABLE, THE_VERIFIER_TABLE, "is missing; run verifier-table --write")
        )
    elif path.read_text(encoding="utf-8") != text:
        findings.append(
            Finding(
                TABLE,
                THE_VERIFIER_TABLE,
                "differs from a fresh write; run verifier-table --write",
            )
        )
    return findings


def main(argv: list[str] | None = None) -> int:
    """Derive the table, lint or write it, print findings; return the exit code."""
    parser = argparse.ArgumentParser(
        prog="verifier-table",
        description="Write standards/verifiers.yaml, or fail where it disagrees.",
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
        findings = audit(
            root,
            list_rules_via_subprocess,
            write=args.write,
            dependencies=DEPENDENCY_RULES,
        )
    except (CannotRun, md.UnclosedFence) as err:
        print(f"verifier-table: cannot run: {err}", file=sys.stderr)
        return 2

    for f in sorted(findings, key=lambda f: (f.file, f.rule, f.message)):
        print(f.render())
    if findings:
        print(f"verifier-table: {len(findings)} finding(s)", file=sys.stderr)
        return 1
    print(f"verifier-table: {'written' if args.write else 'clean'}", file=sys.stderr)
    return 0
