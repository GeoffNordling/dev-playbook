---
type: README
title: "Box: sessionxml"
description: The operator cover sheet for the sessionxml box — engine, done, stuck, walls, and audit procedure
---

# Box: sessionxml

Mission: build sessionxml per box/contract.md.

    Engine   one autonomous session in the worktree, with box/prompt.md as
             its mission prompt; the agent runs box/gate.sh before declaring
             done
    Done     box/gate.sh exits 0
    Stuck    tools/sessionxml/BLOCKED.md exists -> halt engine, notify human
    Walls    dot-claude/settings.json — rename to .claude/settings.json
             when instantiating a real box

The engine line is a per-mission choice, not part of the boundary: swap it
(iterative loop, scatter-gather, chained boxes) and nothing else in box/
changes.

Audit procedure (human, ~15 min):

1. `./box/gate.sh` — trustless re-check
2. Run the tool on one of your own real sessions
3. Read `DEVIATIONS.md` and `UPSTREAM.md`
4. Launch the describer workflow on `tools/sessionxml/` (it reads the agent's
   internal tests too) and diff its account against the emissions

Template notes: this is the worked greenfield-CLI example from
/standards/agentic-box.md. To instantiate, copy the tree, replace the
`sessionxml` mission (contract, fixtures, acceptance tests) with yours, and
keep the skeleton — prompt, charter shape, emissions spec, and gate barely
change between CLI boxes.
