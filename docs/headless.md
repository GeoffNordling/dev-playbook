---
type: General-Sheet
title: Headless Operation
description: Running Claude Code headless on subscription
---

# Headless Operation

Claude Code runs headless with `claude -p` — no terminal, no prompts, one
process per invocation. This covers how it is billed, what each run reports
about itself, and why its file permissions cannot be scoped to a directory.
The decision to use it is [0023](/docs/decisions/0023-headless-on-subscription.md).

## Billing

`claude -p` draws from subscription usage, and nothing in this workspace may
reach the metered API.

Claude Code resolves credentials in a fixed order, and the subscription login
sits at the bottom of it. Anthropic's [IAM
documentation](https://code.claude.com/docs/en/iam) states that in
non-interactive mode a configured key is always used when present — so a stray
`ANTHROPIC_API_KEY` moves the workspace to per-token billing with no prompt and
no warning. Environment variables outrank the login:

`ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`,
`CLAUDE_CODE_USE_BEDROCK`, `CLAUDE_CODE_USE_VERTEX`, `CLAUDE_CODE_USE_FOUNDRY`,
`ANTHROPIC_PROFILE`, `ANTHROPIC_FEDERATION_RULE_ID`,
`ANTHROPIC_ORGANIZATION_ID`.

Settings keys mint or redirect a credential the same way: `apiKeyHelper`,
`awsAuthRefresh`, `awsCredentialExport`.

`CLAUDE_CODE_OAUTH_TOKEN` also outranks the login, and is safe: it is a
subscription credential, not a metered one.

`--bare` skips the keychain and the subscription login outright and demands
an API key, and it is never passed.

[`preflight`](/src/dev_playbook/factory/launcher.py) checks all twelve sources
before every launch and refuses the whole run on a single finding. It reads
the environment and the settings files only — never the keyring.

## How stable the policy is

Subscription coverage of `claude -p` has been withdrawn once already and put
back. Anthropic announced on 2026-05-13 that Agent SDK and `claude -p` usage
would move off the subscription pool, then cancelled the change on 2026-06-15.
The [support
article](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)
states that `claude -p` draws from subscription usage limits.

The signal worth watching is Routines, Anthropic's cloud-hosted scheduled
Claude Code, which is subscription-billed today and in research preview. If it
leaves preview still on subscription, the question is settled favorably. If it
leaves preview metered, the same meter is the obvious next step for `-p`.

## What a run declares about itself

With `--output-format stream-json --verbose`, the first message the harness
emits is an `init` reporting the session's own configuration back:
`apiKeySource`, `session_id`, `cwd`, `model`, `permissionMode`, `tools`, and
`agents`. The terminating `result` message carries `is_error`, `subtype`,
`permission_denials`, `duration_ms`, and the model's final text.

**A run is testable because every guardrail is asserted against state the
harness declares, with no agent behavior in the verdict.** A node that
complied once proves nothing about the next run; an `init` message reporting
`tools: ['Read']` is a fact about the process.

`apiKeySource` appears only in the stream — the plain `--output-format json`
envelope does not carry it.

## What the flags buy

- **`--session-id`** is honored verbatim, so a caller can mint a run's
  identifier up front rather than capturing it from the child afterwards.
- **`--model`** pins the model, and the pin is confirmed in `init`.
- **`--agents`** takes inline agent definitions, which resolve and appear in
  `init`.
- **`--json-schema`** yields a terminal report validated by the harness, so a
  node reports a checked shape instead of prose to be parsed. It silently adds
  a `StructuredOutput` tool to the session, which any assertion over `tools`
  has to expect.
- **`--effort`** accepts `low`, `medium`, `high`, `xhigh`, `max`, and
  `ultracode`. Nothing reports it back, so the pin cannot be verified.

Hooks fire as they do in an attended session, so the measurement pipeline
covers headless runs unchanged.

## Path-scoped permissions do not work

A node was asked to write two files, one under an allowed directory and one
outside it, and judged on whether the outside file existed afterwards and on
`permission_denials`:

| Configuration | Outside file written? | Denials recorded |
|---|---|---|
| no `Write` allow | no | both writes |
| `--allowedTools Write` (bare) | **yes** | none |
| `--allowedTools 'Write(ok/**)'` | no | both writes |
| `--allowedTools 'Write(//abs/ok/**)'` | no | both writes |
| `--disallowedTools 'Write(no/**)'` + allow `Write` | **yes** | none |
| `--disallowedTools 'Write(//abs/no/**)'` + allow `Write` | **yes** | none |
| same deny rule via a `--settings` JSON | **yes** | none |

Bare tool names work in both directions. Every path-scoped rule failed: as an
allow rule it matched nothing, so everything fell through to deny; as a deny
rule it was ignored outright.

**The failure is silent** — no error, no warning, and nothing in
`permission_denials`. A settings file that reads like a fence is not one.

So the only file guardrail available headless is all-or-nothing per tool, plus
deny-by-default. There is no configuration substitute for the write fence an
attended session gets from `EnterWorktree`, which is why the container in
[sandboxing.md](/docs/sandboxing.md) is the only fence left for AFK work.

This was measured under one permission mode and two path forms. A `--debug`
run would show whether the harness reports the rules it is discarding.