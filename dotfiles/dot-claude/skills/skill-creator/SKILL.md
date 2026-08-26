---
name: skill-creator
description: Author a new Claude Code skill bundle against the workspace's skill conventions and the writing-for-agents craft layer. Use when the user says to create a skill.
disable-model-invocation: false
model: opus
effort: xhigh
arguments: [idea]
---

# Skill Creator

Create a new Claude Code skill. `idea` carries whatever the user has already
said about it; the interview in step 2 starts from that and confirms it.

The steps run in order. Step 2 ends by putting its questions to the user and
waiting for the answers, and those answers are the inputs to steps 3–5 — so
the first line of `SKILL.md` gets written at step 5.

## 1. Read the standards

Do both before going further. They split along one seam: conventions is
binding, craft is the skill.

- {Read [skill-conventions.md](~/workspace/dev-playbook/standards/harness/skill-conventions.md) plus its checklist, walked before done}.
  The format `scripts/harness-files-lint` enforces at the commit gate: front matter,
  file structure, length, naming, references, checklist.
- {Run [writing-for-agents](~/.claude/skills/writing-for-agents/SKILL.md) in context} —
  how a document an agent consumes is written so it behaves predictably. Its
  `SKILL-MECHANICS.md` carries the skill-specific half.

This skill is the workflow over those two; the rules live there. {Override [writing-for-agents](~/.claude/skills/writing-for-agents/SKILL.md) on craft guidance with [skill-conventions.md](~/workspace/dev-playbook/standards/harness/skill-conventions.md); they collide}.

## 2. Gather requirements

Ask the user the questions the standards leave to choice:

- **Purpose** — what does this skill do? What problem does it solve? What's the
  success criterion?
- **Use cases** — what specific scenarios should it handle? Any edge cases
  worth calling out?
- **Invocation mode** — `disable-model-invocation: false` (Claude can reach it
  on its own, and so can other skills) or `true` (only the user, typing its
  name)? Surface the trade the standard names: model-invocation spends context
  load on every turn, user-invocation spends the user's own memory.
- **Triggers** — what keywords, contexts, or file types should make Claude
  reach for it, or which fixed dispatcher launches it? Ask this only where the
  invocation-mode answer above was model-invoked; a user-invoked description
  carries no triggers.
- **Model** — ask the user which model the skill runs under (`haiku` /
  `sonnet` / `opus` / `fable`, or `inherit` to follow the session model); it's
  their call. The one mechanic to surface when they decide: a pin only governs
  the turn that loads the skill, so for an interactive, multi-turn skill
  `inherit` is what reflects the rest of the interaction.
- **Effort** — ask the user which effort the skill runs at (`low` / `medium` /
  `high` / `xhigh`); there is no default, and it is their call.
- **Arguments** — none, single free-form (`$ARGUMENTS`), or positional
  (`$0`/`$1`/...)?
- **References** — does the body need supporting files under `references/`?
- **Scripts** — does the skill invoke helper scripts that should live under
  `scripts/` (deterministic ops, repeated logic, places where reliability
  matters)?
- **Tools** — does this skill need an `allowed-tools` restriction, or a
  `disallowed-tools` denial the harness must enforce?

This step is done when every question above carries the user's own answer.

## 3. Write the description

`scripts/harness-files-lint` blocks the commit on the shape, and step 2's
invocation-mode answer picks it: model-invoked is exactly two sentences, the
second opening `Use when` and naming the triggers verbatim, since that
sentence is the auto-invocation match surface; user-invoked is exactly one
sentence, triggers dropped, because no model ever reads it.

## 4. Decide on bundle layout

Rank the content on the information hierarchy. The workspace constrains the
result further.

Keep `SKILL.md` under ~500 lines, and keep references one level deep. Helper
scripts go in `scripts/`, linked relatively (`[check.py](scripts/check.py)`);
the skill-bundle `scripts/` is distinct from any project-root `scripts/`, and
both may coexist.

Place the bundle in the project's `.claude/skills/` if it's project-local, or
in the dotfiles repo's `dotfiles/dot-claude/skills/` for cross-project skills.

## 5. Draft

{Write the new skill bundle, project-local or cross-project home}: `SKILL.md`
and any reference files against the answers from step 2.

- Include a concrete example wherever a rule earns one.
- Mirror the siblings: where the workspace's skills already share a shape
  for a section, read two of them and match it before inventing one. The
  standing example is the Read-first section — "Before doing anything else,
  read end-to-end:", one glossed bullet per doc, then "Then report:
  `READ: <files>`. Proceed only after." — whose report line is what makes
  the read checkable.
- Cite standards for shared rules; another skill's bundle internals are
  reached only as a deliberate pointer, named as such.
- The person in an agent-facing skill is "the user" — one word, no
  synonyms; playbook-lint's agent-facing-voice check blocks the commit
  otherwise.
- A rule belongs to the session that obeys it. When a drafted rule governs
  a *later* session's behavior rather than this skill's own run, move it
  into the artifact that reaches that session — a seeded ruling, a minted
  issue body — and have the skill install the artifact. Restating the rule
  in the skill's own prose makes a second source of truth in a place its
  audience never reads.

## 6. Review with the user

Show the draft. Ask:

- Does this cover the use cases you described?
- Anything missing or unclear?
- Should any section be more or less detailed?
- Where the skill is model-invoked, does the description's `Use when …` clause
  cover the contexts where you'd want it to fire?

Revise based on feedback. Iterate until the user is satisfied.

## 7. Walk the checklist

Walk the checklist in
[skill-conventions.md — Checklist](~/workspace/dev-playbook/standards/harness/skill-conventions.md#checklist)
and confirm each item passes. Fix any failures before considering the skill
done.

Then run dev-playbook's `scripts/harness-files-lint` over the **repo root** of the
repo holding the bundle. Pointing it at the bundle directory finds no skill
roots and passes vacuously ("0 internal skills, all ok") — a pass only
counts when the summary line shows a nonzero skill count.
