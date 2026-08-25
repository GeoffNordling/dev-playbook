---
type: General-Sheet
title: Port Prompt
description: The dispatch prompt for porting one skill or agent to the edge encoding — fill the <PATH> slot and send
---

# Port Prompt

The prompt sent to each port agent. Fill `<PATH>` with the file to port
(a `dotfiles/dot-claude/skills/*/SKILL.md` or
`dotfiles/dot-claude/agents/*.md` path) and send the body below verbatim.

---

You are working in the dev-playbook repository. Your job is to rewrite
one file, `<PATH>`, and record what would not fit. Everything you need
is in this prompt and the files it names.

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
executes it and the human who reads it. You are not designing rules.
Where the rules cannot express something, do your best with what they
allow and record the leftover honestly.

## Read these files first, whole, in this order

1. `no-more-slop-branch-working-files/EDGE-ENCODING.md` — the encoding
   rules: the primitive map, the grammar, and how chains render. This
   file is the contract; nothing in this prompt overrides it.
2. `no-more-slop-branch-working-files/RESIDUAL-LEDGER.md` — what a
   residual is and how entries read. You will add a section here.
3. `no-more-slop-branch-working-files/CLOA-CHAINS.md` — hand-drawn
   chains from before the code existed. Find the section headed with
   your file's name (most files have one; some do not). It shows what
   the chain should roughly say, but it is older than some rules —
   where it disagrees with EDGE-ENCODING.md, EDGE-ENCODING.md wins.
4. Two finished ports, to see what good looks like — the file beside
   its generated block in
   `no-more-slop-branch-working-files/parser/chains.txt`:
   `dotfiles/dot-claude/skills/log-friction/SKILL.md` (guards, a git
   commit, reports) and
   `dotfiles/dot-claude/skills/ralph-setup/SKILL.md` (a read, a
   skill run, guarded writes, a fenced example that must not parse).
   Notice that both still read as ordinary instructions — the braces
   ride on sentences that were already there.
5. `<PATH>`, end to end.

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
   `no-more-slop-branch-working-files/RESIDUAL-LEDGER.md`, in the same
   style as the existing sections: what converged, and each leftover
   the rules could not express. Large leftovers are fine — record them
   plainly; someone else rules on them later.

## Do not

- Do not commit.
- Do not edit any file other than `<PATH>` and `RESIDUAL-LEDGER.md`.
- Do not change the parser, the encoding rules, or any other skill or
  agent.

## Report

Reply `PORTED`, then one short paragraph: the main decisions you made
and the residuals you recorded. If something prevented you from
finishing at all, describe the problem instead of `PORTED`.
