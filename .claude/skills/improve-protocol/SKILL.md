---
name: improve-protocol
description: Observe an executing agent and improve the protocol based on what you see
model: opus
effort: high
---

# Improve Protocol

Prime a session for iteratively improving the Align, Map, Execute
protocol by observing an executing agent's behavior.

## Context

The protocol has two files — a tuple:

- `protocols/align-map-execute/formulation.md` — the mathematical
  formulation. This is the ground truth.
- `protocols/align-map-execute/SKILL.md` — the
  plain-language instruction that executing agents read.

The math is authoritative. When the two diverge, the instruction is wrong.

## Steps

1. Read both protocol files.
2. Tell the user you are ready for observations.

## Workflow

The user will share observations from an executing agent — output it
produced, artifacts it wrote, decisions it made, or behavior that missed
the mark. For each observation:

1. **Diagnose.** Identify where the gap is. Did the instruction fail to
   convey what the math specifies? Or does the math itself not capture
   what the user actually wants? Often it is both. Conclusions must be
   supported by the evidence the observation actually provides:
   - An agent correcting after explicit human direction is not evidence
     that the instruction is sufficient — it only shows the agent can
     follow a direct command.
   - The test for instruction sufficiency is whether a fresh agent,
     reading only the instruction, would behave correctly without human
     correction.
   - When the evidence is ambiguous, say so. Do not resolve ambiguity
     by asserting a conclusion.
2. **Align.** Discuss the fix with the user before editing. The user
   decides what the protocol should say — you help them think through
   implications and find precise wording.
3. **Update math first.** If the mathematical formulation needs to change,
   edit it and get user approval before touching the instruction.
4. **Update instruction.** Make the instruction match the math. Preserve
   existing phrasing where it still aligns — do not rewrite sentences
   that are already correct.
5. **Commit.** When the user is satisfied, commit and push both files.

The user then launches a new executing agent and brings back fresh
observations. Repeat until the executing agent's behavior converges
on the user's intent.
