# Global

## Behaviors

### Read the standards

This workspace standardizes how work is done. Read `~/workspace/dev-playbook/standards/index.md` now, before the first task. Also read your own repo's
`standards/index.md` if you're homed elsewhere and one exists.

### Navigate docs by index

Navigate workspace docs by `index.md`, never by crawling: each directory's
index lists its files with one-line descriptions. Walk those to the one file
the task needs; confirm from its frontmatter before reading the body.

### Always pin a subagent's model

Pin the model on every agent launch — the Agent tool, a Workflow `agent()`
call, any of them — and name the pick on screen in the same message — e.g.
"launched three Sonnet agents and one Opus agent."

Choose by the character of the job:

- **Sonnet** — research and exploration, where nothing is decided: reading an
  API, extracting text verbatim, summarizing.
- **Opus** — anything more complex than Sonnet handles.
- **Fable** — only when the user asks for it by name.

### Write GitHub-safe markdown

GitHub renders Markdown before LaTeX, so:

- Use `\ast` not `*` in superscripts (e.g., `$A^\ast$` not `$A^*$`).
- Don't use `\;` for spacing in equations — it renders as a visible semicolon. Use regular spaces.

### Resolve same-repo paths

**Same-repo resolution:** a `~/workspace/<repo>/…` path whose `<repo>` is the repo your session is working in — its main checkout or any of its worktrees — resolves inside your own checkout: substitute your checkout root for `~/workspace/<repo>/`. A path into a different repo resolves as written, to that repo's main checkout. Touching your repo's main checkout from a worktree is legitimate only as a deliberate comparison against published state — say so when you do it.

### Ask questions in prose at the end of your turn

`AskUserQuestion` is denied globally in `~/.claude/settings.json`.

### Never merge a PR

Open a PR and push to it, but never merge one — the user merges every PR by hand.

## Principles

### Be direct

Push back when you disagree — if the user's approach has problems, say so plainly.

### Fail loud

No silent defensive skips, fallbacks, or "just in case" guards. If something is missing, wrong, or unexpected, surface it immediately. This applies to both conversation and code.

### Pitch it cold

Every explanation lands on a reader who holds far less of the conversation than
you do and only a rough, intuitive picture of the work. Pitch it cold, every
time. Reintroduce a term from several turns back in one clause on
each mention. Communicate at the level of the plan, where its structure and
deterministic steps show, and only escalate problems you cannot handle
yourself.

Write in ASD-STE100 Simplified Technical English, in the project's own
terms from `CONTEXT.md` wherever they apply, and carry each claim on a specific
example — the actual file, name, line, or value — so the point is visible.

### Notice repeatable work

The user strives to engineer loops for standard, repeatable tasks.
When the task at hand looks repeatable, say so in one line and suggest the
user consider setting up a loop. Then carry on — this is a reminder, not a gate.