---
name: intake
description: Triage work at the front door — adopt a rushed, untriaged issue or capture a fresh idea (one issue or many). Decides category, mode, tests; writes the brief into the issue body; advances the issue past intake. Use when the agents dashboard launches intake.
disable-model-invocation: false
model: opus
effort: xhigh
---

# Intake

The front door for work. Input arrives under-formed and leaves as a ready issue — full four-tuple labels and a body brief, advanced to its first work node. Two entry forms:

- **Capture** — the user passes a free-form idea as text. Intake creates one or many new issues, each born ready.
- **Adopt** — the user passes the number or URL of an issue someone threw up rushed and incomplete. It sits untriaged at `phase:intake` — or carries no labels at all; treat both the same. Intake triages it in place and rewrites its body.

## Read first

Before doing anything else, read end-to-end:

- [workflow standard](~/workspace/dev-playbook/workflow/workflow.md) — label scheme, state-machine graph.
- [issue conventions](~/workspace/dev-playbook/standards/tracking/issues.md) — body format, brief principles, vertical-slice rules.

Then report: `READ: workflow.md, issue-conventions.md`. Proceed only after.

## Process

### 1. Read the input

- **Capture** — the text passed in is the raw idea.
- **Adopt** — `gh issue view <issue>` and read its title and body as the raw idea. Note which labels, if any, it already carries; you will rewrite its body.

Either way, invoke `/grill-with-docs` to sharpen the raw idea, then return — **every time**, in both Capture and Adopt. No fuzziness condition, no escape hatch: understanding intent always precedes authoring. Run it **once**, over the raw idea and **before §2 decomposition** — not per slice — since sharpening intent can change how the work is sliced, and always before the §4–§5 write (Capture) or rewrite (Adopt).

### 2. Decide one issue or many

Single coherent piece → one issue. Plan crossing concerns or layers → break into vertical slices, quizzing the user on granularity and dependencies. Size each slice to the context budget (issue conventions → vertical-slice rules): split anything whose build would push an agent past ~30% context. The build agent won't resize the work, so the split has to happen here. When **adopting** a stub that turns out to be a multi-issue plan, refine the stub into the first slice and create the rest as new issues.

### 3. For each issue, pick the four-tuple

- `category:*` — pick one.
- `mode:*` — pick one. Check for a top-level `specs/` directory; ask the user if SDD applicability is unclear.
- `tests:*` — `mode:sdd` is always `tests:yes`. For `mode:direct`, ask the user.
- `phase:*` — the first work node per the state-machine graph. `mode:sdd` starts at `sdd-specs`. For `mode:direct`, decide whether the work needs a design pass: substantive work that wants solution exploration, prototyping, or tradeoff analysis starts at `design`; trivial work bypasses to its implementation node — `tdd` (`tests:yes`) or `build` (`tests:no`). Ask the user when the call isn't clear. Intake always leaves the issue at this node, never at `phase:intake`.

### 4. Draft the brief

Per the issue conventions. When **adopting**, rewriting the stub's body into the brief format is mandatory — there is no path where intake adopts an issue and leaves the body unwritten. Structure what the user wrote, don't discard it.

### 5. Confirm, then land

Before writing anything to GitHub, reflect your read back to the user and land only on their **explicit nod**. This is a non-optional **hard gate**, not a courtesy: intake is HITL, and **adopt** *overwrites* the existing body, so without the nod the rewrite lands silently. In one message, show:

- **Intent** — a one- or two-line restatement of the work as you understand it.
- **The four-tuple** — `category` / `mode` / `tests` / first-work-node `phase`, each with a few words of why.
- **The brief, in miniature** — a few-line sketch of the §4 draft: scope, the load-bearing decisions, the shape of the acceptance criteria. Never the body verbatim — the full text lands on the issue, where it's read. For **adopt**, say in a line what the rewrite keeps and drops from the stub.

Ask them to confirm or correct; on a correction, revise and re-confirm. This is a fast alignment, not a ceremony — when nothing needs adjusting, they nod and you land at once. Two things do **not** satisfy this gate: a narrow clarifying question, and a completed `/grill-with-docs` — however thorough the §1 grill, it sharpened *intent*, while §5 confirms the *authored artifact*; neither substitutes for the other. (A deeper terminology or domain dispute is a `/grill-with-docs` matter per §1, not this beat.)

On the nod:

**Capture** — create the issue at its first work node:

```bash
gh issue create --title "..." \
  --label "<category>" --label "<mode>" --label "<tests>" --label "<phase>" \
  --body "$(cat <<'EOF'
...body...
EOF
)"
```

Multi-issue plans: create slices in dependency order so each blocker exists before the next slice links to it (wired in step 6).

**Adopt** — set the four-tuple and overwrite the body on the existing issue:

```bash
gh issue edit <issue> \
  --add-label "<category>" --add-label "<mode>" --add-label "<tests>" --add-label "<phase>" \
  --body "$(cat <<'EOF'
...body...
EOF
)"
```

If the stub carried `phase:intake`, drop it with `--remove-label "phase:intake"`; if it carried no labels, there is nothing to remove. Either way the issue ends at its first work node. A stub that was really a multi-issue plan: edit it into the first slice, then `gh issue create` the rest.

### 6. Wire relationships

When intake produced more than one issue, set the native relationships per [issue conventions → Relationships](~/workspace/dev-playbook/standards/tracking/issues.md). Neither has a `gh` subcommand, so use `gh api`; both endpoints take the target issue's internal `id` (not its number), so resolve that first. `{owner}`/`{repo}` are filled from the current repo.

Mark each ordered slice **blocked-by** its predecessor:

```bash
blocker_id=$(gh api repos/{owner}/{repo}/issues/<blocker#> --jq .id)
gh api --method POST repos/{owner}/{repo}/issues/<dependent#>/dependencies/blocked_by -F issue_id="$blocker_id"
```

If the slices roll up under a tracking epic, also add each as a **sub-issue** of it:

```bash
child_id=$(gh api repos/{owner}/{repo}/issues/<child#> --jq .id)
gh api --method POST repos/{owner}/{repo}/issues/<epic#>/sub_issues -F sub_issue_id="$child_id"
```

## Output

Report one line per issue, in the standard form: `<repo>#<issue> · current phase: intake · next phase: <first work node> · <one-line summary> · brief in issue`.
