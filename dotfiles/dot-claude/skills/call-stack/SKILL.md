---
name: call-stack
description: Show the conversation as a call stack of levels, each with the user message that opened it, what was discussed and settled there, and what it still owes. Use when the user asks for the call stack or where the conversation stands, or when a compaction or rewind skill needs the stack.
disable-model-invocation: false
model: inherit
effort: medium
---

# Call Stack

Show where the conversation stands as a call stack: the levels of focus
it opened, outermost first. A level is a question the conversation had
to answer before it could carry on with what it was doing. If it is not
obvious that something is a level, it is not one; fewer levels beat
more.

## Procedure

1. Walk the user-typed messages from the session start, or the last
   compaction, to now, and mark the one that opened each level. Done
   when every level has its opening message.

2. {Report the call stack, one block per level, then one line for what
   sits outside the whole stack} in the format below. Done when every line stands
   alone for a reader who has forgotten the transcript.

## Format

One block per level, then one closing line:

```
**Level <n> — <focus, one line>**
- **User message:** "<first seven words of the opening message>…"
- **Discussed:**
  - <what was considered here, including what was dropped>
- **Settled:**
  - <one thing decided or produced here>
- **Owed:** <what this level still needs before it can close>

**Outside the stack:** <what was done or said that belongs to no level>
```

- The user message marks a `/rewind` checkpoint: quote its first seven
  words verbatim and stop.
- A settled bullet names the thing itself, the ruling, the file, the
  commit, in a line that needs no transcript.
- Owed is the goal in general terms, not a checklist. A level with
  nothing owed is closed, and the level above resumes on what it
  settled.
- A field with nothing in it says `nothing yet` or `nothing`.
