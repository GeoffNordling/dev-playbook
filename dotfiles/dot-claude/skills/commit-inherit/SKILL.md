---
name: commit-inherit
description: Commit staged work with a clean message and push it, on the session's own model. Use when committing infrequently, such as when the user asks for a commit or a unit of work ends.
disable-model-invocation: false
model: inherit
effort: low
arguments: [target]
allowed-tools: Bash(git *), Read, Edit
---

# Commit

Commit and push without narration; speak up only when something is unexpected.

A commit isn't done until it's on origin: after committing, `git push`.

## Args

`target` is free text on where to commit — `main`, `new branch`, `current worktree`, anything. Any phrasing counts as an instruction for the rest of the session.

Off `main`: commit to the branch checked out.

On `main`, no target: stop and ask, per the global rule.

Target given that doesn't match the branch checked out: fail loud, don't commit.

## Worklist

If the diff touches a working documentation set, a directory under
`working-docs/`, read the `Planned` list of that set's `ROOT.md`, or
of the strand's `ROOT.md` where the work has strands. Any item the
diff finishes moves to `Completed` with today's date, in this commit.
An item is finished when the state its body describes is in the tree.

## Staging

1. `git status` and `git diff --stat`
2. Stage the files carrying the work you did in this conversation, and leave the rest — other agents may own those changes
3. `git log --oneline -3` to match commit message style

## All modes

- Always stage `settings.json` changes — they are housekeeping
- Never commit `.env` files, credentials, or secrets
- End the message with: `Co-Authored-By: Claude <noreply@anthropic.com>`
- Commit, then confirm with `git status`, then `git push`. {Report tree clean or which files remain uncommitted, and that the push landed}.
