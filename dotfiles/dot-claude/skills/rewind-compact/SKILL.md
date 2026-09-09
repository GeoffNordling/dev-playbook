---
name: rewind-compact
description: Prepare a limited conversation rewind, compressing the discarded turns into a compaction summary to paste after /rewind.
disable-model-invocation: true
model: opus
effort: medium
arguments: [target]
---

# Rewind Compact

## Procedure

1. **Resolve the rewind target** to one user-typed message. `/rewind`
   offers only user-typed messages as checkpoints, and rewinds the
   conversation to the state *just before* the chosen message was sent:
   the target and everything after it are discarded. `target` takes
   two forms:
   - A description of the message: scan backward for the turn it
     describes, the one that initiated the tangent.
   - A level number from a call stack the user ran with `/call-stack`
     earlier in this conversation: the level to resume. The target is
     the message that opened the level directly below it, so `2`
     targets the message that opened level 3.

   Done when one user-typed message is the target.

2. Check for uncommitted work:

   ```
   git status --short
   ```

   {If the tree is dirty, {Run [/commit](~/.claude/skills/commit/SKILL.md)}
   and label the commit as a /rewind-compact point}. Done when the tree
   is clean.

3. **Inventory state-on-disk changes** between the rewind target and
   now: files written or edited (list paths), commits (IDs and
   branches), other persistent artifacts (GitHub issues, PRs). Done
   when every change since the target is listed.

4. **Inventory in-conversation information** between the rewind target
   and now: instructions, decisions, side notes, insights, asides. Only
   what cannot be recovered by re-reading the committed files, kept
   concise. When the target is a level, the call stack on screen
   already holds this: carry it whole, with each change from step 3
   folded onto the Settled line of the level that produced it. Done
   when nothing that matters is left out.

5. {Report the compaction summary; inside a fenced code block, so the
   user can copy it verbatim and paste it after invoking `/rewind`} and
   {Report the verbatim text of the rewind target; labelled
   `**Your /rewind selection target:**` and presented as a blockquote}.

## Output format

````
```
**Tangential compaction summary:**

A tangential iterative exploration of roughly <N> turns occurred from this point. The conversation was then rewound back to here. The current state of <file path> is preferred — re-read it to bring yourself up to date.

The following commits landed during the tangent (not commits you authored):
   - <commit-id> on <branch>.
   - <commit-id> on <branch>.
   - ...

<When the target was a level: "You are at level <N>: <focus>." followed by the call stack, whole. Otherwise the in-conversation information from step 4. Omit this paragraph if everything was captured on disk.>
```

**Your /rewind selection target:**

> <verbatim text of the rewind target>
````

## Notes

- Give a rough turn count from a quick glance back; don't ask the user,
  and don't enumerate. Precision doesn't matter.
- "Re-read the file" instructions must use full paths so past-self knows
  exactly what to load.
- Multiple files may have changed; list them all.
- If past-self's prior work at the rewind target was substantive (a
  draft, a diagram, a decision), say "the current state is preferred" so
  they don't try to redo it.
