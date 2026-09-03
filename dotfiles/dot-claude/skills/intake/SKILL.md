---
name: intake
description: Triage work at the front door — adopt a rushed, untriaged issue or capture a fresh idea, and leave it briefed and routed. Use when the user hands over a raw idea or a rushed stub to be triaged, or when /candidate-promote passes a promoted entry through.
disable-model-invocation: false
model: inherit
effort: xhigh
---

# Intake

The front door for work, and the first state of the [definition region](~/workspace/dev-playbook/software-factory/software-factory.md#the-definition-region). Input arrives under-formed and leaves as a tracked issue carrying the full four-tuple, a body brief, and a phase naming what takes it next. Entry forms:

- **Capture** — the user passes a free-form idea as text. Intake creates the issue.
- **Adopt** — the user passes the number or URL of an issue someone threw up rushed and incomplete. It sits untriaged at `phase:intake` — or carries no labels at all; treat both the same. Intake triages it in place and rewrites its body.

**One issue, never many.** Intake does not slice and never mints an epic. Work that turns out to be a plan rather than a piece routes to `design`, which owns decomposition; §3 makes that routing call.

## Read first

Before doing anything else:

- {Read [software factory standard](~/workspace/dev-playbook/software-factory/software-factory.md); the two regions, the label scheme, and where an issue goes when intake releases it}.
- {Read [issue authoring](~/workspace/dev-playbook/standards/tracking/issue-authoring.md); the brief formats, brief principles, and the readiness bar}.

Then say `READ: software-factory.md, issue-authoring.md`. Proceed only after.

## Process

### 1. Read the input

- **Capture** — the text passed in is the raw idea.
- **Adopt** — {Read from GitHub the issue's title, body, and comments as the raw idea; `gh issue view <issue> --json title,body,comments`}. Note which labels, if any, it already carries; you will rewrite its body.

Either way, {Run [/grilling](~/.claude/skills/grilling/SKILL.md) once to sharpen the raw idea}, with {Run [/domain-modeling](~/.claude/skills/domain-modeling/SKILL.md) active throughout}, then return — **every time**, in both Capture and Adopt, before the §4 draft and the §5 write. Understanding intent precedes authoring; not even a clear-seeming idea skips the grill.

### 2. Check the idea against the repo

Checks, run before a line of the brief is written:

- **Redundancy.** Search dev-playbook's skills, standards, and scripts, plus the open issues of the repo the idea belongs to, for work that already covers the idea. Search by concept, not by the wording the idea arrived in.
- **Claims — surface and pick.** Take each factual claim the idea rests on — a file is missing, a script behaves a certain way, a rule goes unenforced — and sort it: the ones the approach stands on go to the user as a **proposed-probe list**, and they pick which are worth measuring ([Claim provenance](~/workspace/dev-playbook/standards/tracking/issue-authoring.md#claim-provenance)); peripheral claims ride as `assumed` freely. Run the picked probes immediately, in-context, as ordinary tool calls, keeping each probe's command and observed output for the probe-record comment §5 posts.

Report what both checks found and where you looked. On a hit — existing coverage, or a picked probe that fails — put the evidence to the user; the proceed-or-kill call is theirs.

### 3. Pick the four-tuple

{Read [Label Scheme](~/workspace/dev-playbook/standards/tracking/label-scheme.md); the dimensions, their values, and what each means} — pick the appropriate value in each.

- `tests:*` — for `mode:direct`, ask the user.
- `phase:*` — the routing decision, and intake's real deliverable. Never leave the issue at `phase:intake` — on the fast path §5 holds it there only until §6's verdict moves it, or the user parks the beat and the issue holds here for the next session.

Routing, given the mode:

| The work | Routes to | Why |
|---|---|---|
| `mode:spike` | `phase:spike` | A question is answered inside the definition region; it never enters the factory. |
| `mode:direct`, specifiable on the spot | `phase:build`, set at §6 on the user's approval — §5 writes `phase:intake` | The brief is complete and the approach settled, so nothing is left to design. Their approval releases the issue — brief completion alone does not, per [readiness](~/workspace/dev-playbook/standards/tracking/issue-authoring.md#readiness). |
| `mode:direct`, needing exploration, tradeoffs, or slicing | `phase:design` | The approach isn't settled, or the work is bigger than one build. Design re-authors the brief or decomposes. |

Ask the user when the call isn't clear. Routing is a one-way handoff — nothing comes back to intake.

### 4. Draft the brief

Per the issue conventions: the build-leaf brief for `mode:direct`, the spike brief for `mode:spike`. When **adopting**, rewriting the stub's body into the brief format is mandatory — every adopted issue leaves with an authored body. Structure what the user wrote, don't discard it.

Work routing to `design` still gets the best brief the interview supports; design re-authors it at its exit. An issue parked at `design` is not yet ready — readiness is settled at the approval that releases the issue, not here.

On the **fast path** — a `mode:direct` brief complete here, so no design session will re-author it — draft every build-leaf heading [issue authoring](~/workspace/dev-playbook/standards/tracking/issue-authoring.md#required-headings) requires except `User intent`, then {Run [/user-intent-mini-interview](~/.claude/skills/user-intent-mini-interview/SKILL.md) for that one}, and §5 confirms a whole brief. Work routing to `design` skips the beat and gets it there instead, and a `mode:spike` brief never carries the heading at all.

### 5. Confirm, then land

Before writing anything to GitHub, reflect your read back to the user and land only on their **explicit nod**. This is a **hard gate**: no label lands in the definition region on the agent's own authority, and **adopt** *overwrites* the existing body, so without the nod the rewrite lands silently. In one message, show:

- **Intent** — a one- or two-line restatement of the work as you understand it.
- **The four-tuple** — `category` / `mode` / `tests` / routed `phase`, each with a few words of why.
- **The brief, in miniature** — a few-line sketch of the §4 draft: scope, the load-bearing decisions, the shape of the acceptance criteria. Never the body verbatim — the full text lands on the issue, where it's read. For **adopt**, say in a line what the rewrite keeps and drops from the stub.

Ask them to confirm or correct; on a correction, revise and re-confirm. This is a fast alignment: when nothing needs adjusting, they nod and you land at once. Two things do **not** satisfy this gate: a narrow clarifying question, and a completed §1 grill — however thorough, it sharpened *intent*, while §5 confirms the *authored artifact*. (A deeper terminology or domain dispute is a §1 grill matter, not this beat.)

On the nod, **bind `<phase>` before running either command below**. Work routed to `design` or `spike` writes its routed phase. The fast path writes `phase:intake` — never `phase:build`, which §6 sets on the user's approval; the hold lasts until §6 ends, or into the next session if the user parks the beat.

**Capture** — {Write to GitHub the new issue at that phase}:

```bash
gh issue create --title "..." \
  --label "<category>" --label "<mode>" --label "<tests>" --label "<phase>" \
  --body ...the brief...
```

**Adopt** — {Write to GitHub the four-tuple and the overwritten body on the existing issue}:

```bash
gh issue edit <issue> \
  --add-label "<category>" --add-label "<mode>" --add-label "<tests>" --add-label "<phase>" \
  --body ...the brief...
```

For **adopt** on a `design` or `spike` route, drop a carried `phase:intake` with `--remove-label "phase:intake"`; on the fast path it is the phase being written, so `--add-label` mints it or leaves the carried one in place. Then, with the issue live, {Write to GitHub the probe-record comment §2 accumulated; each picked probe's command and its observed output — so the brief's `measured` claims have their citation before review reads them}.

### 6. The issue-review beat — fast path only

The two lenses are **your tools** — latent instruments you run to sharpen your own brief before anyone reads it. Work routed to `design` or `spike` skips this section — design runs the beat at its own exit, and a spike never enters the factory.

1. **Dispatch both lenses in one message**, as fresh-context subagents: {Run [/issue-review-claims](~/.claude/skills/issue-review-claims/SKILL.md) `<issue>`} and {Run [/issue-review-simulation](~/.claude/skills/issue-review-simulation/SKILL.md) `<issue>`}, each pinned to the model its skill file names. They read only the issue and the repo — never this session's conversation — and return findings raw.
2. **Edit the brief in place.** Merge and deduplicate both lenses' findings, then apply or demote each on your own judgment, rewriting the body until it is a brief you would hand an autonomous builder. Never stop to have the user rule, and record nothing about the run on the issue — the repaired brief is the whole output.
3. **Present the finished issue** — the URL, what you changed and why, and anything you could not resolve. This is where the user first reads it, so finish it before this line.
4. {If the user approves, and only then, {Write to GitHub the phase move; `gh issue edit <issue> --remove-label "phase:intake" --add-label "phase:build"`}}. Asked for changes, apply and re-present. Sent to design, route it there instead (`--add-label "phase:design"`), where the brief is re-authored and the beat reruns at design's own exit — always a full fresh run of both lenses.

No label crosses out of the definition region on your own authority. The user may always skip the beat, cut it short, or advance anyway.

## Output

{Report the standard form: `<repo>#<issue> · phase: intake · <one-line summary> · routed to <phase> · brief in issue`}. Where the user parked §6's beat, `routed to <phase>` reads `awaiting approval` instead: the issue holds at `phase:intake` until they give it.
