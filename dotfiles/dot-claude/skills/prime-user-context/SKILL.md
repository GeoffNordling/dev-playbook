---
name: prime-user-context
description: Produce a structured primer for resuming work after a context switch
disable-model-invocation: true
effort: medium
allowed-tools: Bash(git *) Bash(gh *)
---

# Context Primer

You are helping the user get back up to speed after a break.

Review the full conversation history and the repo's current state, then output
a primer in exactly this format:

## Output format

```
## Context Primer

### What we're working on
The objective and its scope. If a GitHub issue is referenced, include its title
and what it asks for.

### What we've accomplished
Bullet list of what's been done so far — decisions made, problems solved,
things built. Focus on substance, not file paths.

### Where we stopped
What we were in the middle of or had just finished when the conversation ended.
Include the branch name.

### Planned next steps
What remains to be done.

### Key context
Non-obvious decisions, constraints, discoveries, or user preferences that a
newcomer would need. Omit this section if nothing notable.
```

## Rules

- Be factual and specific. If you are unsure about something, omit it.
- Keep the total primer under 40 lines. Compress ruthlessly.
- You MAY run git commands to verify current branch, recent commits, and
  working-tree status so the primer reflects reality, not stale memory.
