---
name: rewind-compact
description: Prepare a limited conversation rewind, compressing the discarded turns into a Tangential compaction summary.
disable-model-invocation: true
model: opus
effort: medium
arguments: [target]
---

# Rewind Compact

## Procedure

1. **Confirm the rewind target** — the user-typed message the user wants
   to return to, the turn that initiated the tangent. `/rewind` offers
   only user-typed messages as checkpoints, and rewinds the conversation
   to the state *just before* the chosen message was sent: the target and
   everything after it are discarded. Scan backward for the turn `target`
   describes.

2. {Run [/commit](~/.claude/skills/commit/SKILL.md)} and label the commit
   as a /rewind-compact point.

3. **Inventory state-on-disk changes** between the rewind target and now:
   - Files written or edited (list paths).
   - Commits made (note IDs and branches).
   - Other persistent artifacts (GitHub issues, PRs).

4. **Inventory in-conversation information** between the rewind target and
   now:
   - Instructions, decisions, side notes, insights, asides.
   - Include only what can't be recovered by re-reading the committed
     files.
   - Prepare to summarize this information concisely, keeping the
     important ideas and dropping the rest.

5. {Report the Tangential compaction summary; inside a fenced code block,
   so the user can copy it verbatim and paste it after invoking
   `/rewind`} and {Report the verbatim text of the rewind target;
   labelled `**Your /rewind selection target:**` and presented as a
   blockquote}.

## Output format

````
```
**Tangential compaction summary:**

A tangential iterative exploration of roughly <N> turns occurred from this point. The conversation was then rewound back to here. The current state of <file path> is preferred — re-read it to bring yourself up to date.

The following commits landed during the tangent (not commits you authored):
   - <commit-id> on <branch>.
   - <commit-id> on <branch>.
   - ...

<Other in-conversation information, concisely stated. Omit this paragraph if everything was captured on disk.>
```

**Your /rewind selection target:**

> <verbatim text of the rewind target>
````

## Notes

- Give a rough turn count from a quick glance back — don't ask the user, and don't enumerate; precision doesn't matter.
- "Re-read the file" instructions must use full paths so past-self knows exactly what to load.
- Multiple files may have changed — list them all.
- If past-self's prior work at the rewind target was substantive (a draft, a diagram, a decision), say "the current state is preferred" so they don't try to redo it.
