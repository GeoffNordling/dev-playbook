---
name: improve-protocol
description: Prime a session for improving the Align, Map, Execute protocol from observations of an executing agent. Use when the user wants to feed observed agent behavior back into the protocol.
disable-model-invocation: true
model: opus
effort: high
---

# Improve Protocol

Prime a session for iteratively improving the Align, Map, Execute
protocol by observing an executing agent's behavior.

## Context

The protocol has two sides — a tuple:

- [formulation.md](~/workspace/dev-playbook/protocols/align-map-execute/formulation.md)
  — the mathematical formulation.
- [protocol-align-map-execute](~/workspace/dev-playbook/dotfiles/dot-claude/skills/protocol-align-map-execute/SKILL.md)
  — the skill bundle carrying the plain-language instruction that
  executing agents read: `SKILL.md` and its `references/`.

The math is authoritative. When the two diverge, the instruction is wrong.

## Steps

1. Read the formulation and the whole skill bundle.
2. Tell the user you are ready for observations.

## Workflow

The user will share observations from an executing agent — output it
produced, artifacts it wrote, decisions it made, or behavior that missed
the mark. For each observation:

1. **Diagnose.** Identify where the gap is. Did the instruction fail to
   convey what the math specifies? Or does the math itself not capture
   what the user actually wants? Often it is both. Conclusions must be
   supported by the evidence the observation actually provides:
   - An agent correcting after explicit direction from the user is not
     evidence that the instruction is sufficient — it only shows the agent
     can follow a direct command.
   - The test for instruction sufficiency is whether a fresh agent,
     reading only the instruction, would behave correctly without a
     correction from the user.
   - When the evidence is ambiguous, say so and leave it open.
2. **Align.** Discuss the fix with the user before editing. The user
   decides what the protocol should say — you help them think through
   implications and find precise wording.
3. **Update math first.** If the mathematical formulation needs to change,
   edit it and get user approval before touching the instruction.
4. **Update instruction.** Make the instruction match the math, preserving
   existing phrasing wherever it still aligns.
5. **Commit.** When the user is satisfied, commit and push both sides.

The user then launches a new executing agent and brings back fresh
observations. Repeat until the executing agent's behavior converges
on the user's intent.
