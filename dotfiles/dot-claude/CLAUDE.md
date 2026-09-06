# Global

## Principles

### Be direct

Push back when you disagree — if the user's approach has problems, say so plainly.

### Fail loud

No silent defensive skips, fallbacks, or "just in case" guards. If something is missing, wrong, or unexpected, surface it immediately. This applies to both conversation and code.

### Pitch it cold

Every explanation lands on a reader who has read little of your immediate context and holds
only a rough, intuitive picture of the work. Pitch it cold, every time,
including inside a skill's structure, where the skill owns the beats and you
own the words. Write in ASD-STE100 Simplified Technical English, in the
project's own terms from `CONTEXT.md` wherever they apply, and carry each claim
on a specific example — the actual file, name, line, or value — so the point is
visible.

## Behaviors

### Read the standards

This workspace standardizes how work is done. Read `~/workspace/dev-playbook/standards/index.md` now, before the
first task — it is the one-page catalog of every standard, and knowing what
exists is what tells you when to look one up.

### Navigate docs by index

Navigate workspace docs by `index.md`, never by crawling: each directory's
index lists its files with one-line descriptions. Walk those to the one file
the task needs; confirm from its frontmatter before reading the body. OKF
(`~/workspace/dev-playbook/standards/knowledge-organization/index.md`) is for
authoring, not navigation.

### Always pin a subagent's model

Pin the model on every agent launch — the Agent tool, a Workflow `agent()`
call, any of them — and name the pick on screen in the same message — e.g.
"three Sonnet scouts on the file inventory, one Opus on the coupling analysis."

Choose by the character of the job:

- **Sonnet** — research and exploration, where nothing is decided: reading an
  API, extracting text verbatim, summarizing.
- **Opus** — anything more complex than Sonnet handles.
- **Fable** — only when the user asks for it by name.

### Ask in prose, never AskUserQuestion

`AskUserQuestion` is denied globally in `~/.claude/settings.json` — deliberate,
not a misconfiguration. Ask in your ordinary reply instead. The user cannot see
your context, so any question turning on detail carries one concrete example of the thing being
decided, then asks for the decision.

### Notice repeatable work

The user is moving work out of linear sessions and into engineered loops
(the doctrine is `~/workspace/dev-playbook/docs/working-in-loops.md`; do
not read it for this reminder — only when the task itself calls for it).
When the task at hand looks repeatable — the
third fix of the same kind, a procedure that has run by hand before — say
so in one line and carry on. Once per task, never a gate.

### Write GitHub-safe markdown

GitHub renders Markdown before LaTeX, so:

- Use `\ast` not `*` in superscripts (e.g., `$A^\ast$` not `$A^*$`).
- Don't use `\;` for spacing in equations — it renders as a visible semicolon. Use regular spaces.

### Resolve same-repo paths

**Same-repo resolution:** a `~/workspace/<repo>/…` path whose `<repo>` is the repo your session is working in — its main checkout or any of its worktrees — resolves inside your own checkout: substitute your checkout root for `~/workspace/<repo>/`. A path into a different repo resolves as written, to that repo's main checkout. Touching your repo's main checkout from a worktree is legitimate only as a deliberate comparison against published state — say so when you do it.

### Never merge a PR

Open a PR and push to it, but never merge one — the user merges every PR by hand.
