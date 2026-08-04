---
name: rewind-compact
description: Prepare a limited conversation rewind, compressing the discarded turns into a Tangential compaction summary. Use when the user wants to rewind past a long tangent whose outcome is already captured on disk.
disable-model-invocation: true
model: opus
effort: medium
argument-hint: "<rewind target>"
---

# Rewind Compact

Long tangential explorations (document polishing, design iteration, prototyping, etc.) can consume many turns whose outcome is fully captured on disk. Rewinding past them compacts the context — but past-self has no memory of what happened after the rewind target. This skill produces a parsimonious "Tangential compaction summary" that the user pastes in after rewinding, bringing past-self up-to-date with minimal context usage.

The **rewind target** is the **user-typed message** the user wants to return to — the turn that initiated the tangent. `/rewind` offers only user-typed messages as checkpoints; your replies and tool results are not selectable. Picking one rewinds the conversation to the state *just before that message was sent*: the target and everything after it are discarded, so whatever is worth keeping from that stretch travels in the summary the user pastes back in.

## Procedure

1. **Confirm the rewind target.** Scan backward to find the turn matching `$ARGUMENTS`, which is a semantic description of the point the user wants to rewind to.

2. **Commit all uncommitted work.**
   - Use /commit and label the commit specifically as a /rewind-compact point.
   - The commit rides the session's live grant. If it is denied, ask the user
     for /commit-on before going further: everything after the rewind target
     is discarded, so uncommitted work is lost work.

3. **Inventory state-on-disk changes** between the rewind target and now:
   - Files written or edited (list paths).
   - Commits made (note IDs and branches).
   - Other persistent artifacts (GitHub issues, PRs).

4. **Inventory in-conversation information** between the rewind target and now:
   - Instructions, decisions, side notes, insights, asides.
   - Include only what can't be recovered by re-reading the committed files.
   - Prepare to summarize this information in a concise, compact form that conveys the important ideas without all the little details.

5. **Output two artifacts**:
   1. The "Tangential compaction summary" inside a fenced code block (so the user can copy it verbatim and paste it after they invoke `/rewind`).
   2. The verbatim text of the **rewind target** — the message the user selects in `/rewind`. Label it `**Your /rewind selection target:**` and present it as a blockquote.

## Output format

````
```
**Tangential compaction summary:**

A tangential iterative exploration of roughly <N> turns occurred from this point. The conversation was then rewound back to here. The current state of <file path> is preferred — re-read it to bring yourself up to date.

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

- Give a rough turn count from a quick glance back — don't ask the user, and don't enumerate; precision doesn't matter.
- "Re-read the file" instructions must use full paths so past-self knows exactly what to load.
- Multiple files may have changed — list them all.
- If past-self's prior work at the rewind target was substantive (a draft, a diagram, a decision), explicitly say "the current state is preferred" so they don't try to redo it.
