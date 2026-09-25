# Committing on the Host

What a commit skill run on the user's machine adds to the commit
procedure: a target, a staging rule, and the push.

## Target

`target` is free text on where to commit — `main`, `new branch`, `current worktree`, anything. Any phrasing counts as an instruction for the rest of the session.

Off `main`: commit to the branch checked out.

On `main`, no target: stop and ask, per the global rule.

Target given that doesn't match the branch checked out: fail loud, don't commit.

## Staging

Stage only the files carrying the work you did in this conversation.
Leave any change you don't recognize — other agents may own it.

## Push

A commit isn't done until it's on origin: after committing, `git push`.
{Report that the push landed}.
