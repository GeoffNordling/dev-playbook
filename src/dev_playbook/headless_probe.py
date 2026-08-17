"""Headless probe — the standing check that `claude -p` still carries the AFK factory's contract.

The workspace intends to run its AFK factory nodes as headless `claude -p`
processes on Claude Max subscription OAuth. That intent rests on harness
behaviour Anthropic never promised to keep, so this script re-measures the
load-bearing parts on demand and fails loud when one moves.

Two things it does, in order:

  - **The billing guard** runs first and aborts the whole run on any finding.
    Anthropic's credential precedence puts `ANTHROPIC_API_KEY` third of seven
    and subscription OAuth last, and documents that "in non-interactive mode
    (`-p`), the key is always used when present"
    (https://code.claude.com/docs/en/iam) — so a configured key moves the
    workspace to per-token billing with no warning, and the probe refuses to
    invoke anything at all while one is reachable. The guard covers every
    source that outranks subscription OAuth. It reads the environment and the
    settings files; it never reads the keyring, and nothing here may ever call
    `secret-tool`.

  - **The probes** assert on state the harness declares about itself — the
    `init` message's `cwd`, `model`, `tools`, `session_id`, `apiKeySource`, and
    `agents`, plus the result envelope and the schema-validated result body.
    Nothing here asserts that a model *obeyed* an instruction: an agent
    complying once proves nothing about the next run, so every assertion reads
    a fact the harness reports rather than behaviour a model chose.

`--bare` is never passed and never may be: it skips keychain and OAuth reads
outright and demands `ANTHROPIC_API_KEY`, which is the exact trapdoor the
guard exists to keep shut. The child environment is additionally stripped of
every credential variable as defence in depth.

`invoke` takes no default arguments. Every call states every flag it runs
under, so a probe's configuration is readable at its call site and a forgotten
flag is a type error rather than a silent inherited default.

Exit codes follow the repo's script convention: 0 all probes passed, 1 one or
more failed, 2 the guard tripped or the tool could not run.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import uuid
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

#: Environment variables that route inference somewhere other than subscription
#: OAuth. Every one of these outranks the `/login` credential in Anthropic's
#: documented precedence order, so any of them being set is a hard stop.
BILLING_ENV_VARS = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_BASE_URL",
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
    "CLAUDE_CODE_USE_FOUNDRY",
    "ANTHROPIC_PROFILE",
    "ANTHROPIC_FEDERATION_RULE_ID",
    "ANTHROPIC_ORGANIZATION_ID",
)

#: Settings keys that mint or redirect credentials.
BILLING_SETTINGS_KEYS = ("apiKeyHelper", "awsAuthRefresh", "awsCredentialExport")

#: The structured-output schema standing in for a factory node's terminal
#: report. The harness validates the model's output against it, which is what
#: makes the report contract checkable rather than a parse of model prose.
REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["done", "escalate"]},
        "summary": {"type": "string"},
    },
    "required": ["status", "summary"],
    "additionalProperties": False,
}


@dataclass
class Run:
    """One headless invocation and everything the harness said about it."""

    argv: list[str]
    returncode: int
    init: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] = field(default_factory=dict)
    hook_events: list[str] = field(default_factory=list)
    stderr: str = ""


@dataclass
class Probe:
    """One assertion's outcome."""

    name: str
    passed: bool
    detail: str


def settings_files() -> list[Path]:
    """The settings files a session merges, nearest-scope last."""
    return [
        Path.home() / ".claude" / "settings.json",
        Path.cwd() / ".claude" / "settings.json",
        Path.cwd() / ".claude" / "settings.local.json",
    ]


def billing_guard() -> list[str]:
    """Findings naming every reachable route to per-token billing."""
    findings = []
    for var in BILLING_ENV_VARS:
        if os.environ.get(var):
            findings.append(f"environment: {var} is set")

    for path in settings_files():
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            findings.append(f"{path}: unreadable ({exc})")
            continue
        for key in BILLING_SETTINGS_KEYS:
            if data.get(key):
                findings.append(f"{path}: {key} is configured")
        for var in BILLING_ENV_VARS:
            if data.get("env", {}).get(var):
                findings.append(f"{path}: env.{var} is set")
    return findings


def child_env() -> dict[str, str]:
    """The parent environment with every credential variable removed."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("ANTHROPIC_")}
    for var in (*BILLING_ENV_VARS, "CLAUDE_CODE_OAUTH_TOKEN"):
        env.pop(var, None)
    return env


def invoke(
    prompt: str,
    *,
    model: str,
    session_id: str,
    cwd: Path,
    tools: Sequence[str],
    permission_mode: str,
    effort: str,
    agents: dict[str, Any] | None,
    json_schema: dict[str, Any] | None,
    timeout: int,
) -> Run:
    """Run one headless invocation and parse everything the harness emitted.

    Every argument is required: see the module docstring on why there are no
    defaults. `--bare` is deliberately absent and must stay absent.
    """
    argv = [
        "claude",
        "-p",
        prompt,
        "--output-format",
        "stream-json",
        "--verbose",
        "--model",
        model,
        "--session-id",
        session_id,
        "--permission-mode",
        permission_mode,
        "--effort",
        effort,
        "--tools",
        *(tools if tools else [""]),
    ]
    if agents:
        argv += ["--agents", json.dumps(agents)]
    if json_schema:
        argv += ["--json-schema", json.dumps(json_schema)]

    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            env=child_env(),
            check=False,
        )
    except subprocess.TimeoutExpired:
        return Run(argv=argv, returncode=124, stderr=f"timed out after {timeout}s")

    run = Run(argv=argv, returncode=proc.returncode, stderr=proc.stderr)
    for line in proc.stdout.splitlines():
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        message_type = message.get("type")
        message_subtype = message.get("subtype")
        if message_type == "system" and message_subtype == "init":
            run.init = message
        elif message_type == "result":
            run.result = message
        elif message_type == "system" and message_subtype in (
            "hook_started",
            "hook_completed",
        ):
            run.hook_events.append(str(message.get("hook_event")))
    return run


def probe_run(run: Run, *, expect: dict[str, Any]) -> list[Probe]:
    """Assertions over one run, each reading harness-declared state.

    Every assertion here guards something the factory design leans on: the
    billing source, the ledger join key, where the process was placed, the
    model pin, the tool fence, agent-definition resolution, that the
    measurement hooks still fire, and that the run reported success.
    """
    init, result = run.init, run.result
    if not init:
        return [Probe("harness-init", False, "no init message; run failed to start")]

    probes = [
        Probe(
            "billing-subscription",
            init.get("apiKeySource") == "none",
            f"apiKeySource={init.get('apiKeySource')!r} (want 'none')",
        ),
        Probe(
            "session-id-honored",
            init.get("session_id") == expect["session_id"],
            f"session_id={init.get('session_id')} (ledger join key)",
        ),
        Probe(
            "cwd-placement",
            init.get("cwd") == str(expect["cwd"]),
            f"cwd={init.get('cwd')}",
        ),
        Probe(
            "model-pin",
            str(init.get("model", "")).startswith(f"claude-{expect['model']}-"),
            f"model={init.get('model')} (asked for {expect['model']!r})",
        ),
        Probe(
            "tool-fence",
            init.get("tools") == list(expect["tools"]),
            f"tools={init.get('tools')} (asked for {list(expect['tools'])})",
        ),
        Probe(
            "hooks-fire",
            bool(run.hook_events),
            f"hook events observed: {sorted(set(run.hook_events)) or 'NONE'}",
        ),
        Probe(
            "result-envelope",
            result.get("is_error") is False and result.get("subtype") == "success",
            f"is_error={result.get('is_error')} subtype={result.get('subtype')}",
        ),
    ]

    if "agent" in expect:
        probes.append(
            Probe(
                "agent-definition",
                expect["agent"] in (init.get("agents") or []),
                f"agents={init.get('agents')}",
            )
        )
    if "schema_keys" in expect:
        raw = result.get("result") or ""
        try:
            payload = json.loads(raw)
            shaped = isinstance(payload, dict) and set(payload) == expect["schema_keys"]
        except json.JSONDecodeError, TypeError:
            shaped = False
        probes.append(
            Probe("structured-report", shaped, f"schema-validated body: {raw[:70]!r}")
        )
    return probes


def probe_concurrency(cwd: Path, count: int) -> list[Probe]:
    """Whether N headless processes survive running at once.

    The factory dispatches its reviewer nodes in parallel, so this decides
    whether that fan-out is available or the traverse has to serialize.

    It is opt-in because it is the only probe that can change machine state
    rather than only reading it: every process shares one credential file, and
    a batch launching while that credential is due for renewal could in
    principle have its members renew over each other and force a re-login.
    Whether Claude Code actually renews eagerly, locks the file, or tolerates a
    reused refresh token is unverified — the caution is a guess about
    internals, not a measured failure.
    """
    ids = [str(uuid.uuid4()) for _ in range(count)]
    with ThreadPoolExecutor(max_workers=count) as pool:
        runs = list(
            pool.map(
                lambda session_id: invoke(
                    "say ok",
                    model="sonnet",
                    session_id=session_id,
                    cwd=cwd,
                    tools=[],
                    permission_mode="auto",
                    effort="low",
                    agents=None,
                    json_schema=None,
                    timeout=180,
                ),
                ids,
            )
        )
    succeeded = [r for r in runs if r.result.get("is_error") is False]
    distinct = {r.init.get("session_id") for r in runs if r.init}
    return [
        Probe(
            f"concurrency-{count}",
            len(succeeded) == count and distinct == set(ids),
            f"{len(succeeded)}/{count} succeeded; distinct session ids: {len(distinct)}",
        )
    ]


def main(argv: Sequence[str] | None = None) -> int:
    """Run the guard, then the probes, and report."""
    parser = argparse.ArgumentParser(
        prog="headless-probe",
        description="Assert that `claude -p` still carries the AFK factory's contract.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=0,
        metavar="N",
        help="also run N headless processes at once (opt-in: races credential refresh)",
    )
    parser.add_argument(
        "--guard-only",
        action="store_true",
        help="run the billing guard and exit without invoking anything",
    )
    args = parser.parse_args(argv)

    print("== billing guard ==")
    findings = billing_guard()
    for finding in findings:
        print(f"  BLOCK  {finding}")
    if findings:
        print(
            "\nRefusing to invoke: a configured API key is always used in -p mode, "
            "which bills per token.",
            file=sys.stderr,
        )
        return 2
    print("  ok     no credential outranking subscription OAuth is reachable")
    if args.guard_only:
        return 0

    if not shutil.which("claude"):
        print("claude not found on PATH", file=sys.stderr)
        return 2

    cwd = Path.cwd()
    probes: list[Probe] = []

    print("\n== probes ==")
    sonnet_id = str(uuid.uuid4())
    sonnet = invoke(
        "Report that the toy task finished successfully.",
        model="sonnet",
        session_id=sonnet_id,
        cwd=cwd,
        tools=["Read"],
        permission_mode="auto",
        effort="low",
        agents={
            "toy-node": {
                "description": "A toy factory node",
                "prompt": "You are a toy node.",
            }
        },
        json_schema=REPORT_SCHEMA,
        timeout=180,
    )
    probes += probe_run(
        sonnet,
        expect={
            "session_id": sonnet_id,
            "cwd": cwd,
            "model": "sonnet",
            # `--json-schema` adds a StructuredOutput tool of its own, so a
            # schema-carrying node's fence is always its own list plus that one.
            "tools": ["Read", "StructuredOutput"],
            "agent": "toy-node",
            "schema_keys": {"status", "summary"},
        },
    )

    opus_id = str(uuid.uuid4())
    opus = invoke(
        "say ok",
        model="opus",
        session_id=opus_id,
        cwd=cwd,
        tools=[],
        permission_mode="auto",
        effort="xhigh",
        agents=None,
        json_schema=None,
        timeout=180,
    )
    probes += [
        p
        for p in probe_run(
            opus,
            expect={
                "session_id": opus_id,
                "cwd": cwd,
                "model": "opus",
                "tools": [],
            },
        )
        if p.name in ("model-pin", "tool-fence", "result-envelope")
    ]

    if args.concurrency:
        probes += probe_concurrency(cwd, args.concurrency)

    for probe in probes:
        print(
            f"  {'PASS' if probe.passed else 'FAIL':5}  {probe.name:24}  {probe.detail}"
        )

    failed = [p for p in probes if not p.passed]
    print(
        f"\n{len(probes) - len(failed)}/{len(probes)} probes passed",
        file=sys.stderr,
    )
    return 1 if failed else 0
