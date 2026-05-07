# _Scratch_: Compounding workflow with AI

**Status:** scratchpad. Promote to numbered ADR after implementation lands.

## Context

Read "How to Work and Compound with AI" and audited this machine + dev-playbook against the article's practices. Three gaps to close:

1. No global `~/.claude/CLAUDE.md` (behavioral contract loaded every session).
2. No codified pattern for nested CLAUDE.md when a repo holds distinct sub-projects.
3. Verification runs only at commit time (`.pre-commit-config.yaml`); the model doesn't see lint feedback inside its edit loop.

Rejected explicitly: codified always-loaded reading order, abandoning `rules/`, switching per-repo CLAUDE.md to onboarding style, INDEX.md per project, transcript-mining tooling (deferred), enabling auto-memory.

## Instruction surface

Files that act as instructions to the model, by load semantics:

| Path | Loads when | Tier |
|---|---|---|
| `~/.claude/CLAUDE.md` | Every session, everywhere | Universal |
| `~/.claude/rules/*.md` | Every session, everywhere | Universal operational |
| `~/workspace/<repo>/CLAUDE.md` | Sessions inside that repo | Repo |
| `~/workspace/<repo>/<sub-project>/CLAUDE.md` | Sessions inside that sub-project | Project |
| `standards/*.md`, `sdd-standards/*.md` | Only when a skill or CLAUDE.md points at them | Workspace governance |
| `.claude/skills/*/SKILL.md` | On invocation | Workflow |

## Audit of existing instruction content

| Location | Content | Tier it actually is | Action |
|---|---|---|---|
| `rules/bash-commands.md` | `!` prefix is fake; hand off interactive commands | Universal | Keep. |
| `rules/edit-in-dev-playbook.md` | Symlinks under `~/` route to dotfiles; edit source | Universal | Keep. |
| `~/CLAUDE.md` (was `dotfiles/CLAUDE.md` via Stow) | Edit source not symlink; run sync; layout | Dotfiles project, but loaded everywhere | **Removed.** Replaced by `~/.claude/CLAUDE.md` (universal preferences) at a new source path. |
| `dev-playbook/CLAUDE.md` → "no secrets" rule | Don't commit secrets to a public repo | Universal default | **Dropped.** Already part of base behavior. |
| `dev-playbook/CLAUDE.md` → "LaTeX in Markdown" | `\ast` not `*`; no `\;` | Universal | **Promoted to global CLAUDE.md.** |
| `dev-playbook/CLAUDE.md` → sync-dotfiles, pre-commit SoT, agent skills | Repo-specific operations | Repo | Kept. |

## Implementation: global CLAUDE.md

New file at `dotfiles/.claude/CLAUDE.md`, Stow-symlinked to `~/.claude/CLAUDE.md`. Three XML-tagged sections:

- `<behavior>` — direct, push back, root-cause, fail-fast, scoped diffs, terse.
- `<teaching>` — 1–2 sentence explainer in `> 💡 …` blockquote when a new term surfaces.
- `<markdown>` — GitHub LaTeX rendering quirks (`\ast`, no `\;`).

The "fail fast and loud" bullet was added at user direction after observing a too-defensive first cut of the ruff hook.

## Implementation: nested CLAUDE.md

`standards/repo-documentation.md` gained a `## CLAUDE.md hierarchy` section and a `<sub-project>/CLAUDE.md` row in the Files table. A repo `MAY` add nested files at sub-project roots; they hold the delta only, not duplicates of the parent. Same scope as root: operational instructions, no project description.

## Implementation: edit-time Python hook

**Wiring.** `dotfiles/.claude/hooks/ruff-edit.sh`, called from `dotfiles/.claude/settings.json` as `PostToolUse` with matcher `Edit|Write|MultiEdit`. Runs `ruff format` then `ruff check --fix` on the edited file.

**Why.** Pre-commit catches ruff issues at commit time. This hook catches them inside the same edit loop the model is iterating in, so corrections happen without round-trips.

**Project-local ruff, no global install.** The hook walks up from the edited file looking for `.venv/bin/ruff` and uses whatever the project pinned in `pyproject.toml` / `uv.lock`. A global ruff would drift from per-repo pins, causing format-bounce loops. Editing a Python file outside any uv-managed project fails loud with a hint to run `uv sync` — a deliberate surface, not a silent skip.

**Exit-code contract for PostToolUse** (per Claude Code hooks docs):

| Exit | Behavior | Use when |
|---|---|---|
| 0 | Success. Stderr is NOT shown to Claude. | Nothing to surface. |
| 2 | "Blocking" error. Stderr fed to Claude as an error message. | Anything Claude must address. |
| Other | Non-blocking. Stderr goes to user-visible terminal scrollback only. | Avoid — every signal should reach Claude or stay silent. |

PostToolUse cannot actually block (the tool already ran); exit 2 is the only signal that puts stderr in front of Claude after a tool call.

**Fail-loud principle.** Every contract violation (missing field, malformed JSON, missing project venv, format failure) exits 2 with an explanation. No silent skips, no `|| true` fallbacks, no defensive guards that paper over unexpected state. The one silent-exit-0 path is non-`.py` files — not a fault, just out of scope (the matcher fires on every Edit|Write|MultiEdit regardless of extension).

## Decisions

- [x] Create `dotfiles/.claude/CLAUDE.md` (Stow → `~/.claude/CLAUDE.md`), XML-tagged.
- [x] Move LaTeX-in-Markdown rules from `dev-playbook/CLAUDE.md` into the new global file.
- [x] Drop the "no secrets" line from `dev-playbook/CLAUDE.md`.
- [x] Update `standards/repo-documentation.md` to codify nested CLAUDE.md.
- [x] Add `PostToolUse` hook + `ruff-edit.sh` script.
- [ ] Phase 1 tests pass (script logic).
- [ ] Phase 2 integration test passes (after Claude Code restart).
- [ ] Promote this scratchpad to a numbered ADR.

## Out of scope (logged for later)

- Watcher-pair pattern for execution/direction drift.
- Transcript reader (`bin/transcript-reader`) as the foundation for transcript mining.
- Worklog auto-post hook on substantial task completion.
- INDEX.md pattern (revisit if a business/team repo lands).
- `standards/agent-hooks.md` as a home for shared hook conventions — extract if a second hook lands and the patterns repeat.

## Implementation log

- 2026-05-07: Created `dotfiles/.claude/CLAUDE.md`. Stow synced to `~/.claude/CLAUDE.md`.
- 2026-05-07: Removed `dotfiles/CLAUDE.md` and orphaned symlink at `~/CLAUDE.md`.
- 2026-05-07: Trimmed `dev-playbook/CLAUDE.md` (removed "no secrets" line and LaTeX section).
- 2026-05-07: Codified nested CLAUDE.md in `standards/repo-documentation.md`.
- 2026-05-07: Added `dotfiles/.claude/hooks/ruff-edit.sh` (project-local ruff via walk-up). Wired `PostToolUse` matcher in `settings.json`. Pending: Phase 1 + Phase 2 tests.
