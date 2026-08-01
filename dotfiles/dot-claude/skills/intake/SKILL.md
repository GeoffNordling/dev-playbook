---
name: intake
description: Triage work at the front door — adopt a rushed, untriaged issue or capture a fresh idea, deciding its category, mode, and tests, authoring the brief, and routing it to the node that takes it next. Use when the user invokes /intake, hands over a raw idea or a rushed stub to be triaged, or when /candidate-promote passes a promoted entry through.
disable-model-invocation: false
model: inherit
effort: xhigh
---

# Intake

The front door for work, and the first state of the [definition region](~/workspace/dev-playbook/software-factory/software-factory.md#the-definition-region). Input arrives under-formed and leaves as a tracked issue carrying the full four-tuple, a body brief, and a phase naming what takes it next. Two entry forms:

- **Capture** — the user passes a free-form idea as text. Intake creates the issue.
- **Adopt** — the user passes the number or URL of an issue someone threw up rushed and incomplete. It sits untriaged at `phase:intake` — or carries no labels at all; treat both the same. Intake triages it in place and rewrites its body.

**One issue, never many.** Intake does not slice and never mints an epic. Work that turns out to be a plan rather than a piece routes to `design`, which owns decomposition; §3 makes that routing call.

## Read first

Before doing anything else, read end-to-end:

- [software factory standard](~/workspace/dev-playbook/software-factory/software-factory.md) — the two regions, the label scheme, and where an issue goes when intake releases it.
- [issue authoring](~/workspace/dev-playbook/standards/tracking/issue-authoring.md) — the brief formats, brief principles, and the readiness bar.

Then report: `READ: software-factory.md, issue-authoring.md`. Proceed only after.

## Process

### 1. Read the input

- **Capture** — the text passed in is the raw idea.
- **Adopt** — `gh issue view <issue> --comments` and read its title, body, and comments as the raw idea. Note which labels, if any, it already carries; you will rewrite its body.

Either way, invoke /grill-with-docs to sharpen the raw idea, then return — **every time**, in both Capture and Adopt, run once over the raw idea and always before the §4 draft and the §5 write. Understanding intent precedes authoring, with no fuzziness condition that lets the grill be skipped.

### 2. Check the idea against the repo

Two checks, both run before a line of the brief is written:

- **Redundancy.** Search dev-playbook's skills, standards, and scripts, plus the open issues of the repo the idea belongs to, for work that already covers the idea. Search by concept, not by the wording the idea arrived in.
- **Claims.** Take each factual claim the idea rests on — a file is missing, a script behaves a certain way, a rule goes unenforced — and check it against the tree.

Report what both checks found and where you looked. On a hit — existing coverage, or a claim that fails — put the evidence to the user; the proceed-or-kill call is theirs.

### 3. Pick the four-tuple

- `category:*` — pick one.
- `mode:*` — `mode:direct` or `mode:spike`. `mode:sdd` is a retained label the factory does **not** support and intake never mints, per [software-factory.md → SDD is not supported](~/workspace/dev-playbook/software-factory/software-factory.md#sdd-is-not-supported).
- `tests:*` — for `mode:direct`, ask the user; `mode:spike` is always `tests:no`.
- `phase:*` — the routing decision, and intake's real deliverable. Never leave the issue at `phase:intake`.

Routing, given the mode:

| The work | Routes to | Why |
|---|---|---|
| `mode:spike` | `phase:spike` | A question is answered inside the definition region; it never enters the factory. |
| `mode:direct`, specifiable on the spot | `phase:build` | The brief is complete, so the issue is ready and the factory takes it from here. |
| `mode:direct`, needing exploration, tradeoffs, or slicing | `phase:design` | The approach isn't settled, or the work is bigger than one build. Design re-authors the brief or decomposes. |

Ask the user when the call isn't clear. Routing is a one-way handoff — nothing comes back to intake.

### 4. Draft the brief

Per the issue conventions: the build-leaf brief for `mode:direct`, the spike brief for `mode:spike`. When **adopting**, rewriting the stub's body into the brief format is mandatory — every adopted issue leaves with an authored body. Structure what the user wrote, don't discard it.

Work routing to `design` still gets the best brief the interview supports; design re-authors it at its exit. An issue parked at `design` is not yet ready, and that is the expected state — readiness is checked at the crossing into the factory, not here.

### 5. Confirm, then land

Before writing anything to GitHub, reflect your read back to the user and land only on their **explicit nod**. This is a non-optional **hard gate**, not a courtesy: no label lands in the definition region on the agent's own authority, and **adopt** *overwrites* the existing body, so without the nod the rewrite lands silently. In one message, show:

- **Intent** — a one- or two-line restatement of the work as you understand it.
- **The four-tuple** — `category` / `mode` / `tests` / routed `phase`, each with a few words of why.
- **The brief, in miniature** — a few-line sketch of the §4 draft: scope, the load-bearing decisions, the shape of the acceptance criteria. Never the body verbatim — the full text lands on the issue, where it's read. For **adopt**, say in a line what the rewrite keeps and drops from the stub.

Ask them to confirm or correct; on a correction, revise and re-confirm. This is a fast alignment, not a ceremony — when nothing needs adjusting, they nod and you land at once. Two things do **not** satisfy this gate: a narrow clarifying question, and a completed /grill-with-docs — however thorough the §1 grill, it sharpened *intent*, while §5 confirms the *authored artifact*; neither substitutes for the other. (A deeper terminology or domain dispute is a /grill-with-docs matter per §1, not this beat.)

On the nod:

**Capture** — create the issue at its routed phase:

```bash
gh issue create --title "..." \
  --label "<category>" --label "<mode>" --label "<tests>" --label "<phase>" \
  --body "$(cat <<'EOF'
...body...
EOF
)"
```

**Adopt** — set the four-tuple and overwrite the body on the existing issue:

```bash
gh issue edit <issue> \
  --add-label "<category>" --add-label "<mode>" --add-label "<tests>" --add-label "<phase>" \
  --body "$(cat <<'EOF'
...body...
EOF
)"
```

If the stub carried `phase:intake`, drop it with `--remove-label "phase:intake"`; if it carried no labels, there is nothing to remove. Either way the issue ends at its routed phase.

## Output

Report in the standard form: `<repo>#<issue> · phase: intake · <one-line summary> · routed to <phase> · brief in issue`.
