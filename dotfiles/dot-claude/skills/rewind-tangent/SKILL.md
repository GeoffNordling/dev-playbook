---
name: rewind-tangent
description: Prepare for a conversation rewind by drafting a "Message from the model" that brings past-self up to date after the rewind.
disable-model-invocation: true
model: opus
effort: medium
argument-hint: "<rewind target>"
---

# Rewind Tangent

Long tangential explorations (document polishing, design iteration, prototyping, etc.) can consume many turns whose outcome is fully captured on disk. Rewinding past them compacts the context — but past-self has no memory of what happened after the rewind target. This skill produces a parsimonious "Message from the model" that the user pastes in after rewinding, bringing past-self up to date without re-loading all the throwaway iteration.

## Rewind target: $ARGUMENTS

## Procedure

1. **Confirm the rewind target.** Scan backward to find the turn matching `$ARGUMENTS`. If ambiguous, ask the user.

2. **Inventory state-on-disk changes** between the rewind target and now:
   - Files written or edited (list paths).
   - Commits made (note IDs and branches).
   - Other persistent artifacts (GitHub issues, PRs).

3. **Inventory in-conversation information** the user conveyed during this span: instructions, decisions, side notes, insights, asides.

4. **Classify each in-conversation item:**
   - Captured in a surviving file or commit → **throwaway** (past-self will see it by reading the file).
   - Not captured anywhere on disk → **candidate non-throwaway**.

5. **Align with the user on the non-throwaway list.** Present the candidates concisely. Let the user confirm or trim.

6. **Commit all uncommitted work — mandatory.** Without a commit, the rewind risks losing disk state, and uncommitted changes can be accidentally reverted. The commit also gives past-self a concrete reference. Use `/commit` and label the commit specifically as a /rewind-tangent contribution.

7. **Output two artifacts** in this order:
   1. The "Message from the model" inside a fenced code block (so the user can copy it verbatim and paste it after rewinding).
   2. The verbatim text of the user message that comes right after the rewind target — this is what the user selects in the `/rewind` picker to land at the correct point. Label it `**Your /rewind selection target:**` and present it as a blockquote.

## Output format

````
```
**Message from the model:**

A tangential iterative exploration of approximately <N> turns occurred from this point. The conversation was then rewound back to here. The current state of <file path> is preferred to <what you produced at this turn> — re-read it to pick up the final form: <brief description of current state>. Committed as <commit-id> on <branch> (not a commit you authored).

<Non-throwaway insights, parsimoniously stated. Omit this paragraph if everything was captured on disk.>
```

**Your /rewind selection target:**

> <verbatim text of the user message that comes right after the rewind target>
````

## Notes

- Count turns by scanning, not by asking the user.
- "Re-read the file" instructions must use full paths so past-self knows exactly what to load.
- Multiple files may have changed — list them all.
- If past-self's prior work at the rewind target was substantive (a draft, a diagram, a decision), explicitly say "the current state is preferred" so they don't try to redo it.
- The `/rewind` selection target is the message *after* the rewind target turn, because Claude Code's `/rewind` lands the conversation at the state immediately before the selected message.

## Example

After ~20 turns iterating on a mermaid diagram in `workflow/workflow.md`:

````
```
**Message from the model:**

A tangential iterative exploration of approximately 20 turns occurred from this point. The conversation was then rewound back to here. The current state of `workflow/workflow.md` is preferred to the graph you just drew — re-read it to pick up the final form: `flowchart LR` with ELK renderer, subgraph swim lanes, diamond gate nodes, self-loops labeled `iterate`. Committed as `1d3e738` on `workflow-standardization` (not a commit you authored).

One ancillary insight not in the file: spec-review and code-review have asymmetric reviewer-of-record. Spec-review = agent checking the human's work product. Code-review = adversarial agent checking the agent's work + human checking both. Carry into Q4 (action authority).
```

**Your /rewind selection target:**

> The self edge is for review round look awkward on screen. Is there any way you can improve the way this displays visually?
````
