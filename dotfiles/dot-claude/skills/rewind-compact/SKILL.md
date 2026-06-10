---
name: rewind-compact
description: Prepare a limited conversation rewind, compressing the discarded turns into a "Tangential compaction summary."
disable-model-invocation: true
effort: medium
argument-hint: "<rewind target>"
---

# Rewind Compact

Long tangential explorations (document polishing, design iteration, prototyping, etc.) can consume many turns whose outcome is fully captured on disk. Rewinding past them compacts the context — but past-self has no memory of what happened after the rewind target. This skill produces a parsimonious "Tangential compaction summary" that the user pastes in after rewinding, bringing past-self up-to-date with minimal context usage.

The `/rewind` command allows the user to select any previous **user-typed message** as a checkpoint — your replies and tool results are not selectable. Picking one rewinds the conversation to the state *just before the selected message was sent*: the picked message and everything after it are discarded.

This skill relies on the concept of a **rewind target**: the specific **user-typed message** the user desires to rewind the conversation to. All relevant information between the **rewind target** and the current turn is compressed into the **Tangential compaction summary**, which the user will copy to clipboard and add back to the context window after performing the `/rewind`.

## Procedure

1. **Confirm the rewind target.** Scan backward to find the turn matching `$ARGUMENTS`, which is a semantic description of the point the user wants to rewind to.
   - The **rewind target** is always a **user-typed message**. It is the point in the conversation that initiated the tangent.
   - The **rewind target**, and all messages after it, will be deleted by this procedure.

2. **Commit all uncommitted work.**
   - Use `/commit` and label the commit specifically as a /rewind-compact point.

3. **Inventory state-on-disk changes** between the rewind target and now:
   - Files written or edited (list paths).
   - Commits made (note IDs and branches).
   - Other persistent artifacts (GitHub issues, PRs).

4. **Inventory in-conversation information** between the rewind target and now:
   - Instructions, decisions, side notes, insights, asides.
   - Include only what can't be recovered by re-reading the committed files — anything already captured on disk is dropped.
   - Prepare to summarize this information in a concise, compact form that conveys the important ideas without all the little details.

5. **Output two artifacts**:
   1. The "Tangential compaction summary" inside a fenced code block (so the user can copy it verbatim and paste it after they invoke `/rewind`).
   2. The verbatim text of the **rewind target** — the message the user selects in `/rewind`. Label it `**Your /rewind selection target:**` and present it as a blockquote.

## Output format

````
```
**Tangential compaction summary:**

A tangential iterative exploration of approximately <N> turns occurred from this point. The conversation was then rewound back to here. The current state of <file path> is preferred — re-read it to bring yourself up to date.

The following commits landed during the tangent (not commits you authored):
   - <commit-id> on <branch>.
   - <commit-id> on <branch>.
   - ...

<Other in-conversation information, parsimoniously stated. Omit this paragraph if everything was captured on disk.>
```

**Your /rewind selection target:**

> <verbatim text of the rewind target>
````

## Notes

- Count turns by scanning, not by asking the user.
- "Re-read the file" instructions must use full paths so past-self knows exactly what to load.
- Multiple files may have changed — list them all.
- If past-self's prior work at the rewind target was substantive (a draft, a diagram, a decision), explicitly say "the current state is preferred" so they don't try to redo it.
