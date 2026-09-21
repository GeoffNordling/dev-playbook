---
type: General-Sheet
title: Distribution Family Rule Audit
description: The rule audit over the distribution/ family — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---

# Distribution Family Rule Audit

The family holds five rules, all in
[Distribution Channel](/standards/distribution/channel.md). One
reclassification is proposed, `distribution.the-roster` from deterministic
to stochastic, and none in the other direction. One rule breaks:
`distribution.the-roster` names `lunch` and `date-tree` in workspace-lint's
`GOVERNED` roster, and neither repo sits under the workspace root, so the
audit refuses to start. No rule is weakly checked: three of the five are
checked in full and two, `distribution.one-published-id` and
`distribution.the-roster`, are checked by nothing at all — both carry a
null verifier row. Two rules are low value: `distribution.a-pinned-rev`,
which `build.pre-commit-configyaml` already blocks on at every consumer's
commit gate, and `distribution.the-roster`, whose first clause is true by
definition and whose second clause states a fact about a workstation
rather than about the repo.

| id | rule | kind | proposed | check | state | overlap | value | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `distribution.one-published-id` | "The hook repository's `.pre-commit-hooks.yaml` publishes exactly one hook, `playbook-lint`." | deterministic | deterministic | none | holds | none | high | Test: parse `.pre-commit-hooks.yaml`, assert the id set equals `{playbook-lint}`. The verifier row is null. standards-lint only ties the manifest to the canonical pinned block, under a different id. |
| `distribution.a-publisher-dogfoods-its-manifest` | "A repo whose root holds `.pre-commit-hooks.yaml` lists every hook id that file publishes under a `repo: local` block of its `.pre-commit-config.yaml`." | deterministic | deterministic | full | holds | `standard.the-hosting-pattern` | high | repo-lint `check_dogfood_mirror` asserts published ids minus local ids is empty (`scripts/repo-lint:685`). The hosting-pattern's code mirrors both ways for `scripts/` hooks, so the overlap is in code, not in the predicate. |
| `distribution.a-valid-manifest` | "A `.pre-commit-hooks.yaml` at a governed repo's root passes `pre-commit validate-manifest`." | deterministic | deterministic | full | holds | none | high | playbook-lint appends `uvx pre-commit validate-manifest <root>/.pre-commit-hooks.yaml` when the file is present (`src/dev_playbook/playbook_lint.py:81`). That call is the predicate. |
| `distribution.a-pinned-rev` | "A governed repo's `.pre-commit-config.yaml` pins the hook repository to a `rev`, unless the repo is the hook repository itself." | deterministic | deterministic | full | holds | `build.pre-commit-configyaml` | low | workspace-lint `check_pin` exempts the hook repo by identity and flags a missing config or pin. Seven roster consumers carry a pin; `lunch` and `date-tree` are not on disk to check. |
| `distribution.the-roster` | "A governed repo is named in workspace-lint's `GOVERNED` roster, and every name in the roster is a repo under the workspace root." | deterministic | stochastic | none | breaks | none | low | `GOVERNED` names `lunch` and `date-tree` (`src/dev_playbook/workspace_lint.py:169-170`); neither is under the workspace root, so `workspace_repos` raises and the audit exits 2. |

## Escalations

### `distribution.the-roster` — "A governed repo is named in workspace-lint's `GOVERNED` roster, and every name in the roster is a repo under the workspace root."

The predicate has two clauses, and each fails for its own reason.

The first clause, "a governed repo is named in workspace-lint's `GOVERNED`
roster", cannot be false. The comment above the tuple at
`src/dev_playbook/workspace_lint.py:155-159` says so outright: "Inclusion is
the decision: a repo absent from this tuple is simply not governed." Being
named in the roster is what makes a repo governed, so a script asking
whether a governed repo is named there reads the answer off its own
question. No detector can fail this clause, and none is asked to: the
verifier row is `distribution.the-roster: null`
(`standards/verifiers.yaml:49`).

The second clause, "every name in the roster is a repo under the workspace
root", is false today. `GOVERNED` names ten repos
(`src/dev_playbook/workspace_lint.py:160-171`). Eight sit under
`~/workspace`. `lunch` (line 169) and `date-tree` (line 170) do not:
neither `~/workspace/lunch` nor `~/workspace/date-tree` exists. Both repos
are alive on GitHub — `GeoffNordling/lunch` was updated on 2026-09-18 and
`GeoffNordling/date-tree` on 2026-09-19, and neither is archived — so the
roster names real repos that this workstation has not cloned. The
consequence is not a finding but a refusal: `workspace_repos`
(`src/dev_playbook/workspace_lint.py:332-348`) raises `ToolError` when any
roster name lacks a `.git`, and `main` turns that into exit 2. The whole
workspace audit — settings, protection, labels, issues, and pins — cannot
run on this machine until the roster and the disk agree.

That is the deeper fault. The clause is a claim about a filesystem outside
the repo, so no script reading only repo files can decide it, which is why
the proposed kind is stochastic rather than deterministic. The
[Distribution Explanation](/standards/distribution/explanation.md) already
states the intent in prose: "A roster entry with no such repo under the
workspace root is a false claim, and the audit refuses to run rather than
pass a quietly shorter sweep." That sentence describes how workspace-lint
starts up, not a state a governed repo holds itself to.

Proposal: delete the rule. Its first clause is unfalsifiable and its second
states machine-local state that no member of the population controls, which
is why the value is low, and a deleted rule takes its null verifier row
with it. The intent survives in two places that already carry it: the
explanation's `## The roster` section states the roster's standing as the
declared population, and `workspace_lint.workspace_repos` keeps the loud
refusal, whose exit code answers to `standard.exit-codes`. A rewrite is the
second-best way out if the roster should stay a named rule — "workspace-lint
names every governed repo in its `GOVERNED` roster and audits no repo the
roster omits", which is a fact about repo files — but it still restates the
tuple's own comment. Changing the repo is the wrong move here: cloning two
repos, or dropping two live repos from the roster, would fix the symptom by
altering intent that the commits `54f5a07` ("add lunch to GOVERNED") and
`c1a06b0` ("add date-tree to GOVERNED") put there deliberately.

## Detectors

`scripts/repo-lint` decides `distribution.a-publisher-dogfoods-its-manifest`
through `check_dogfood_mirror`. The leg runs only where the audited root
holds a `.pre-commit-hooks.yaml`; it reads the published ids out of the
manifest with a regex over `- id:` lines, reads the ids of the
`repo: local` block out of `.pre-commit-config.yaml`, and emits one finding
when the published set is not a subset of the local set. The test is a
subset, not an equality, so local-only hooks such as `make-check` and
`web-typecheck` are free additions. The script is not a thin shim — it
carries its whole rule body — but that is `standard.thin-shims`' business,
not this family's.

`scripts/workspace-lint` decides `distribution.a-pinned-rev` through
`check_pin`. It reads the hook repository's URL out of the canonical
template's pinned block, locates the `rev:` line that follows that
`- repo:` line through `rev_line`, and emits the rule id twice over: once
blocking, when the consumer has no `.pre-commit-config.yaml` or no
dev-playbook pin in it, and once advisory, when the pin is present but
behind the hook repo's local `main`. The hook repository exempts itself by
path identity, matching the predicate's "unless" clause. The advisory half
is the detector's real value and no predicate in the family states it.

`scripts/playbook-lint` decides nothing itself; it dispatches the roster and
adds one conditional step. Where the audited root holds a
`.pre-commit-hooks.yaml`, it appends `uvx pre-commit validate-manifest` over
that file (`src/dev_playbook/playbook_lint.py:79-81`), which is the address
the verifier table names for `distribution.a-valid-manifest`. An exit other
than 0 or 1 from any step turns the whole run into exit 2.

`scripts/standards-lint` decides no distribution rule, but its
`check_hook_surfaces` is the reason the dogfood overlap exists. It compares
the manifest's detector hooks — those whose `entry` starts with `scripts/` —
against the `repo: local` block's detector hooks in both directions under
`standard.the-hosting-pattern`, and, in dev-playbook only, compares the full
manifest against the canonical template's pinned dev-playbook block under
`standard.offered-by-the-canonical-template`. That second leg constrains
what the manifest may publish without ever stating the count of one.
