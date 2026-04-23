---
name: code-quality-sweep
description: Stochastic agentic sweep of the current repository for the code quality anti-patterns cataloged in dev-playbook. Sub-agents flag, then the main agent remediates findings interactively with the user.
disable-model-invocation: true
model: opus
effort: medium
---

# Code Quality Sweep

Sweep the current repository for instances of the anti-patterns cataloged at
`~/workspace/dev-playbook/standards/code-quality-anti-patterns.md` and report
every finding so the user can fix it.

The sweep is stochastic, not exhaustive — it surfaces enough instances to
keep the patterns visible and cut back accumulated rot. Sub-agents flag
defects; they SHALL NOT fix anything, and SHALL NOT add comments that
justify defensive fallbacks. Remediation happens later in the main
conversation with the user deciding each case (Step 4).

## Step 1 — Load the catalog

Read `~/workspace/dev-playbook/standards/code-quality-anti-patterns.md`.
Each heading below the intro is one anti-pattern with its pattern
description, rationale, and rule. Treat the rules as authoritative.

If the catalog is missing or empty, stop and tell the user.

## Step 2 — Dispatch one Explore agent per anti-pattern

Scope is the entire current repository — `git ls-files` restricted to source
files. No branch or PR logic; this is a sledgehammer sweep.

Spawn one Explore agent per catalog entry, in parallel (single message,
multiple Agent tool calls). Each agent gets:

- The anti-pattern's pattern description, rule, and rationale — copy the
  catalog entry verbatim into the prompt.
- Instructions to grep for candidate sites across the repo, then read each
  candidate to confirm. Grep is a sieve, not a verdict.
- Instructions to return a list of findings as `<file>:<line> — <one-line
  description>`, plus a count of candidates examined.
- An explicit reminder not to fix anything and not to add comments.

For the defensive-fallback sweep, the agent decides per-site whether an
existing inline comment actually explains *why* the fallback is intentional.
A comment that just restates what the code does ("return None if missing")
does not satisfy the rule; a comment that names the legitimate runtime
condition ("cache miss — caller expects None on first read") does.

## Step 3 — Report

Aggregate findings into a single report:

- One section per anti-pattern, using the catalog heading.
- One bullet per finding: `file:line — description`.
- If an anti-pattern had zero findings, say so in one line.
- Close with total findings.

## Step 4 — Remediate with the user

Work through the findings with the user in the main conversation, one by
one. Not in sub-agents — the user wants to decide each case.

For each finding, show the offending code and the two legitimate paths
forward. Ask which the user wants, then apply it. Do not bulk-fix.

- **Non-blank `__init__.py`.** Either move the content into a named module
  and blank the file, or drop the content outright. The user decides where
  content should live.
- **Unjustified defensive fallback.** Either remove the fallback so the
  code fails loudly, or add an inline comment naming the legitimate runtime
  condition that makes the fallback intentional. Do not add a justification
  comment without the user confirming the fallback is actually intentional
  — the comment is the signal, not a formality.

If the user wants to defer a finding, note it and move on.
