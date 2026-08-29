---
type: General-Sheet
title: Port Prompt
description: The dispatch prompt for porting one skill or agent to the edge encoding — fill the <PATH> slot and send
---

# Port Prompt

The instructions each port agent works from. The dispatch message is two
lines: tell the agent to read this file and follow it, and name the file
to port (a `dotfiles/dot-claude/skills/*/SKILL.md` or
`dotfiles/dot-claude/agents/*.md` path). Everywhere below, `<PATH>`
means the file your dispatch message named.

## Dispatch procedure

The session that launches port agents runs this loop; the agents run
the body below the rule.

1. Pick a batch of unported first-party runbooks from the
   Port roster in `no-more-slop-branch-working-files/REFERENCE-CHAIN.md`
   — never a (3P) runbook before the plan's adoption-policy stage. Launch
   one Sonnet agent per runbook, in parallel, each with the two-line
   dispatch message above. Do not regenerate this file's body into the
   prompt.
2. Do not read the ported files or their diffs — that spends the
   context the subagents exist to save. The agent's report is the
   content review; the user reviews the diffs in the IDE.
3. When the batch lands, verify mechanically only:
   `python3 no-more-slop-branch-working-files/parser/chaingen.py`
   then `--check`, and grep
   `no-more-slop-branch-working-files/RESIDUAL-LEDGER.md` for one
   `## <name>` header per batch runbook. Parallel agents race on the
   ledger; restore a lost section verbatim from its agent's
   transcript, never by rewriting it.
4. Tick the batch's roster checkboxes, then report the round tally:
   completed vs. open, first-party vs. third-party.
5. Commit only on the user's /commit. The gate runs unaided — no
   `SKIP`.

---

You are working in the dev-playbook repository. Your job is to rewrite
one file, `<PATH>`, and record what would not fit. Everything you need
is in this file and the files it names.

## What this is for

This workspace describes every skill and agent at two levels. The high
level is a **Reference chain** — a small generated diagram of what the
file reads, writes, launches, and reports. The repository's owner reads
the chain instead of the file. The low level is the file itself —
natural English instructions that an executing agent follows. Between
the two levels sits deterministic code:
`no-more-slop-branch-working-files/parser/chaingen.py` finds light
structure in the prose (braced spans such as `{Read [x](path)}`) and
generates every chain into
`no-more-slop-branch-working-files/parser/chains.txt`.

Your job is translation. Re-express this one file using only the
existing encoding rules, so the code generates a true chain from it —
while the prose stays natural for its other two readers: the agent that
executes it and the user who reads it. You are not designing rules.
Where the rules cannot express something, do your best with what they
allow and record the leftover honestly.

## Read these files first, whole, in this order

1. `no-more-slop-branch-working-files/REFERENCE-CHAIN.md` — the encoding
   rules: the primitive map, the grammar, and how chains render. This
   file is the contract; nothing in this prompt overrides it.
2. `no-more-slop-branch-working-files/RESIDUAL-LEDGER.md` — what a
   residual is and how entries read. You will add a section here.
3. Two finished ports, to see what good looks like — the file beside
   its generated block in
   `no-more-slop-branch-working-files/parser/chains.txt`:
   `dotfiles/dot-claude/skills/log-friction/SKILL.md` (guards, a git
   commit, reports) and
   `dotfiles/dot-claude/skills/ralph-setup/SKILL.md` (a read, a
   skill run, guarded writes, a fenced example that must not parse).
   Notice that both still read as ordinary instructions — the braces
   ride on sentences that were already there.
4. `<PATH>`, end to end.

## Do

1. Work out what the file's true chain should say: what it reads,
   writes, launches, runs, overrides, and reports, and under what
   conditions.
2. Rewrite `<PATH>` in place so the code generates that chain. The
   rules that recur on every port: braced spans over the fixed keyword
   set (Read, Write, Commit, Report, Launch, Run, Override, If);
   frontmatter `arguments: [name]` replaces `argument-hint` and every
   `$ARGUMENTS` in the body; no narrative introduction — the body is
   instructions; no prose that restates a marked edge; detail you want
   kept out of the chain goes after a semicolon inside the span;
   literal `{` or `}` in examples must sit inside backticks or a
   fenced code block.
3. Run `python3 no-more-slop-branch-working-files/parser/chaingen.py`,
   then read your file's block in
   `no-more-slop-branch-working-files/parser/chains.txt`. Iterate the
   prose until both readings are good: the chain is clean and true,
   and the file still reads as natural instructions a person would
   write. Parsing is the smaller half of the job — a sentence that
   parses but reads awkwardly is not done; rephrase until it does
   both. Always run the real parser — never predict its output from
   memory. Never edit `chaingen.py`, and never edit `chains.txt` by
   hand (regenerating it with the parser is how it changes).
4. Best effort under the rules as written: no new keywords, no new
   frontmatter fields, no rule changes. A sentence the rules cannot
   express stays plain prose in the file. Some files will encode
   completely; others will mostly stay prose because the rules lack
   the expression they need. Both are valid outcomes — a thin chain
   with a large, honest ledger entry is a finished port, not a
   failure.
5. Add a `## <file's name>` section to
   `no-more-slop-branch-working-files/RESIDUAL-LEDGER.md`. A couple of
   sentences, hard limit: name each specific action you could not
   express and why the rules cannot say it — nothing else. Do not
   narrate what converged, do not restate the rules, do not compare
   with other entries or name residual families. Many leftovers is a
   fine outcome; a long entry is not — every agent who ports after you
   reads this whole file, and your words are their context budget.

## Do not

- Do not commit.
- Do not edit any file other than `<PATH>` and `RESIDUAL-LEDGER.md`.
- Do not change the parser, the encoding rules, or any other skill or
  agent.
- Never run `git stash` in any form. This worktree is shared with
  other agents working in parallel; a stash sweeps up and can destroy
  their uncommitted edits. If the corpus-wide parser run fails on a
  file that is not yours, that is a sibling agent mid-edit — verify
  your own file's chain and move on.

## Report

Reply `PORTED`, then one short paragraph: the main decisions you made
and the residuals you recorded. If something prevented you from
finishing at all, describe the problem instead of `PORTED`.
