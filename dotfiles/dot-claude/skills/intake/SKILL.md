---
name: intake
description: Triage work at the front door — adopt a rushed, untriaged issue or capture a fresh idea, and leave it briefed and routed. Use when the user hands over a raw idea or a rushed stub to be triaged, or when /candidate-promote passes a promoted entry through.
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
- **Claims — surface and pick.** Take each factual claim the idea rests on — a file is missing, a script behaves a certain way, a rule goes unenforced — and sort it: the ones the approach stands on go to the user as a **proposed-probe list**, and they pick which are worth measuring ([Claim provenance](~/workspace/dev-playbook/standards/tracking/issue-authoring.md#claim-provenance)); peripheral claims ride as `assumed` freely. Run the picked probes immediately, in-context, as ordinary tool calls, keeping each probe's command and observed output for the probe-record comment §5 posts.

Report what both checks found and where you looked. On a hit — existing coverage, or a picked probe that fails — put the evidence to the user; the proceed-or-kill call is theirs.

### 3. Pick the four-tuple

- `category:*` — pick one.
- `mode:*` — `mode:direct` or `mode:spike`; those are the only two the scheme carries.
- `tests:*` — for `mode:direct`, ask the user; `mode:spike` is always `tests:no`.
- `phase:*` — the routing decision, and intake's real deliverable. Never leave the issue at `phase:intake` — on the fast path §5 holds it there only until §6's verdict moves it, or the user parks the beat and the issue holds here for the next session.

Routing, given the mode:

| The work | Routes to | Why |
|---|---|---|
| `mode:spike` | `phase:spike` | A question is answered inside the definition region; it never enters the factory. |
| `mode:direct`, specifiable on the spot | `phase:build`, set at §6's issue-review verdict — §5 writes `phase:intake` | The brief is complete and the approach settled, so nothing is left to design. The verdict is what releases the issue — brief completion alone does not, per [readiness](~/workspace/dev-playbook/standards/tracking/issue-authoring.md#readiness). |
| `mode:direct`, needing exploration, tradeoffs, or slicing | `phase:design` | The approach isn't settled, or the work is bigger than one build. Design re-authors the brief or decomposes. |

Ask the user when the call isn't clear. Routing is a one-way handoff — nothing comes back to intake.

### 4. Draft the brief

Per the issue conventions: the build-leaf brief for `mode:direct`, the spike brief for `mode:spike`. When **adopting**, rewriting the stub's body into the brief format is mandatory — every adopted issue leaves with an authored body. Structure what the user wrote, don't discard it.

Work routing to `design` still gets the best brief the interview supports; design re-authors it at its exit. An issue parked at `design` is not yet ready, and that is the expected state — readiness is settled at the issue-review verdict that releases the issue, not here.

### 5. Confirm, then land

Before writing anything to GitHub, reflect your read back to the user and land only on their **explicit nod**. This is a non-optional **hard gate**, not a courtesy: no label lands in the definition region on the agent's own authority, and **adopt** *overwrites* the existing body, so without the nod the rewrite lands silently. In one message, show:

- **Intent** — a one- or two-line restatement of the work as you understand it.
- **The four-tuple** — `category` / `mode` / `tests` / routed `phase`, each with a few words of why.
- **The brief, in miniature** — a few-line sketch of the §4 draft: scope, the load-bearing decisions, the shape of the acceptance criteria. Never the body verbatim — the full text lands on the issue, where it's read. For **adopt**, say in a line what the rewrite keeps and drops from the stub.

Ask them to confirm or correct; on a correction, revise and re-confirm. This is a fast alignment, not a ceremony — when nothing needs adjusting, they nod and you land at once. Two things do **not** satisfy this gate: a narrow clarifying question, and a completed /grill-with-docs — however thorough the §1 grill, it sharpened *intent*, while §5 confirms the *authored artifact*; neither substitutes for the other. (A deeper terminology or domain dispute is a /grill-with-docs matter per §1, not this beat.)

On the nod, **bind `<phase>` before running either command below**. Work routed to `design` or `spike` writes its routed phase. The fast path writes `phase:intake` — never `phase:build`, which §6's verdict sets and nothing here does; the hold is momentary, since §6 runs next in this same session — unless the user parks the beat, and then it holds here for the next session.

**Capture** — create the issue at that phase:

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

For **adopt** on a `design` or `spike` route, drop a carried `phase:intake` with `--remove-label "phase:intake"`; on the fast path it is the phase being written, so `--add-label` mints it or leaves the carried one in place. Then, with the issue live, post the **probe-record comment** §2 accumulated — each picked probe's command and its observed output — so the brief's `measured` claims have their citation before review reads them.

### 6. The issue-review beat — fast path only

An issue routed to `phase:build` is released by the [issue-review verdict](~/workspace/dev-playbook/software-factory/human-checkpoints.md#the-issue-review-verdict), never by the §5 nod alone. Work routed to `design` or `spike` skips this section — design runs the beat at its own exit, and a spike never enters the factory.

1. **Dispatch both lenses in one message**, as fresh-context subagents: one invokes `/issue-review-claims <issue>`, the other `/issue-review-simulation <issue>`, each pinned to the model its skill file names. They read only the issue and the repo — never this session's conversation — and return findings raw.
2. **Synthesize the consolidated disposition list** — both lenses' findings merged and deduplicated, each disposition carrying a recommendation. The user rules on dispositions, never on raw findings one by one.
3. **Take the verdict.** *Pass* — apply or demote per the ruled dispositions (the body is editable until launch), post the **verdict-record comment** — date, lenses run, findings count, disposition gist, verdict — then `gh issue edit <issue> --remove-label "phase:intake" --add-label "phase:build"`. *Back to design* — the brief needs more than the front door gives it: post the verdict-record comment, then route the issue there (`gh issue edit <issue> --remove-label "phase:intake" --add-label "phase:design"`), where the brief is re-authored and the beat reruns at design's own exit, the verdict record its work order. Re-review is always a full fresh run of both lenses.

The user may always skip the beat, cut it short, or advance anyway — the review binds the factory's autonomous path, never the user.

## Output

Report in the standard form: `<repo>#<issue> · phase: intake · <one-line summary> · routed to <phase> · brief in issue`. Where the user parked §6's beat, `routed to <phase>` reads `awaiting verdict` instead: the issue holds at `phase:intake`, and nothing is routed until the verdict comes.
