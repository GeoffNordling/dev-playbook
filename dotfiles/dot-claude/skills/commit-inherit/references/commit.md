# Commit Procedure

The procedure every commit skill follows. The skill that sent you here
says what to stage and what to do after the commit.

Commit without narration; speak up only when something is unexpected.

## Args

`target` is free text on where to commit — `main`, `new branch`, `current worktree`, anything. Any phrasing counts as an instruction for the rest of the session.

Off `main`: commit to the branch checked out.

On `main`, no target: stop and ask, per the global rule.

Target given that doesn't match the branch checked out: fail loud, don't commit.

## Worklist

If the diff touches a file under `workstreams/`, read the `Planned`
list of that file's head file, the `WORKSTREAM.md` in its own
directory or the nearest directory above, and of each `WORKSTREAM.md`
above it. Any item the diff finishes moves, its bold name still first,
under the `Completed` heading of the same head file with today's date,
in this commit; a head file with no `Completed` heading gets one. An
item is finished when the state its body describes is in the tree.

## Staging

1. `git status` and `git diff --stat`
2. Stage the changes
3. `git log --oneline -3` to match commit message style

## All modes

- Always stage `settings.json` changes — they are housekeeping
- Never commit `.env` files, credentials, or secrets
- End the message with: `Co-Authored-By: Claude <noreply@anthropic.com>`
- Commit, then confirm with `git status`. {Report tree clean or which files remain uncommitted}.
