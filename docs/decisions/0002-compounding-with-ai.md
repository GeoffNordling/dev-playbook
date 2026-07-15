---
type: Decision-Record
title: Compounding Workflow with AI
description: Establish tiered instruction loading — a global behavioral CLAUDE.md, nested per-project variants, and edit-time Python linting via project-local ruff
---

# Compounding Workflow with AI

**Status:** The edit-time ruff hook decisions (the "Edit-time Python verification" and "Project-local ruff" adopt bullets, the matching "global-ruff fallback" alternative, and the 2026-06-06 amendment) are superseded by [Decision Record 0008](0008-retire-edit-time-ruff-hook.md) in part (issue #127). The tiered-instruction decisions stand.

## Context

Audited this workspace against the source article above. Three gaps to close, several practices to keep, several to reject.

| Gap | Effect |
|---|---|
| No global `~/.claude/CLAUDE.md` (universal behavioral contract) | Behavioral preferences scattered across per-repo CLAUDE.mds or absent entirely |
| No standard for nested CLAUDE.md inside a repo | A repo with distinct sub-projects had no codified way to layer rules |
| Verification ran only at commit time (`.pre-commit-config.yaml`) | Lint/format feedback didn't reach the model inside its edit loop |

## Decision

### Adopt

- **Global behavioral CLAUDE.md** at `dotfiles/.claude/CLAUDE.md` (Stow-linked to `~/.claude/CLAUDE.md`). XML-tagged: `<behavior>`, `<teaching>`, `<markdown>`. Holds universal preferences only — no operational rules (those stay in `~/.claude/rules/*.md`), no per-repo content.
- **Nested CLAUDE.md as a documented hierarchy.** Repo-documentation standard now has a `## CLAUDE.md hierarchy` section and an Optional row for `<sub-project>/CLAUDE.md`. Nested files hold only the delta from the parent; same scope as the root (operational instructions, not project description).
- **Edit-time Python verification.** PostToolUse hook on `Edit|Write|MultiEdit` runs `ruff format` then `ruff check --fix` on edited Python files. Format diffs apply silently; remaining unfixable lints reach Claude inline as system-reminder errors via exit-2 + stderr. (Amended 2026-06-06 — the `check` step now ignores four name-binding rules at edit time; see [Amendment: edit-transient lint rules](#amendment-2026-06-06--edit-transient-lint-rules-issue-78).)
- **Project-local ruff.** The hook walks up from the edited file looking for `.venv/bin/ruff` and uses whatever the project pinned. No global ruff. Editing Python outside any uv-managed project fails loud with a `uv sync` hint.
- **Fail-loud as a behavioral preference.** Added to `<behavior>` in the global CLAUDE.md after a too-defensive first cut of the hook script. No silent defensive skips, no `|| true` fallbacks, no "just in case" guards.

### Reject

- **Codified always-loaded reading order in CLAUDE.md.** Different sessions do different things; reading order belongs in skills (e.g. `/orient`), invoked when the session warrants it.
- **INDEX.md per project.** Useful for corporate/team repos with significant out-of-repo context (Slack, Drive); not yet applicable to this workspace's largely self-contained repos. Revisit if a business repo lands.
- **Per-repo CLAUDE.md as onboarding/glossary doc.** Existing taxonomic style kept; `/orient` handles the day-one reading-order role.
- **Auto-memory.** `autoMemoryEnabled: false` retained. The human is the programmer of context; auto-memory makes that uncontrolled.
- **Global ruff install.** Drifts from per-repo `pyproject.toml` / `uv.lock` pins; would cause format-bounce loops where the hook formats one way and CI formats it back another.
- **Folding rules into the global CLAUDE.md.** `~/.claude/rules/*.md` kept as separate files; loading semantics are equivalent and the split keeps each rule self-contained.

### Adapt

- **XML tags inside CLAUDE.md.** Adopted from the article (Claude models are trained with XML structure); replaces Markdown headers in the global file. Per-repo CLAUDE.mds remain Markdown-section based — they're reference taxonomies, not behavioral contracts.
- **Teaching block format.** Article's `> 💡 …` blockquote pattern adopted as-is.

## Why

The change makes the instruction surface explicitly **tiered**:

| Tier | Example | Loads |
|---|---|---|
| Universal preferences | `~/.claude/CLAUDE.md` | Every session |
| Universal operational rules | `~/.claude/rules/*.md` | Every session |
| Repo | `<repo>/CLAUDE.md` | Sessions in that repo |
| Project | `<repo>/<sub-project>/CLAUDE.md` | Sessions in that sub-project |
| Workspace governance | `standards/`, `sdd-standards/` | When referenced |
| Workflow | `.claude/skills/*/SKILL.md` | On invocation |

Before this Decision Record, universal preferences were either absent or scattered. After, each piece of instruction has exactly one home and one load trigger.

The edit-time hook closes the verification loop. Pre-commit was the only ruff gate; the model would only learn about lint issues after a human committed and saw the failure. Now the model sees them inside the same edit loop and corrects without round-trips.

Project-local ruff is the only stable answer. Each repo's `pyproject.toml` pins a specific ruff version; CI uses that pin. A global ruff would diverge in version, in selected rules, or in formatter behavior, producing edit-time → CI bounce. Walk-up resolution guarantees the hook uses the same ruff the project will.

## Alternatives considered

| Alternative | Why not |
|---|---|
| Universal preferences at `~/CLAUDE.md` (instead of `~/.claude/CLAUDE.md`) | Functionally equivalent for sessions under `$HOME`, but `~/.claude/CLAUDE.md` is Claude Code's documented user-memory location. Picking the canonical home avoids the "loaded by walk-up accident" semantics of `~/CLAUDE.md`. |
| Keep `dotfiles/CLAUDE.md` Stow-linked to `~/CLAUDE.md` with universal content | Conflated the dotfiles-project file with the universal-preferences file. Cleaner to put the universal file at `~/.claude/CLAUDE.md` and remove the `~/CLAUDE.md` symlink entirely. |
| Inline guides via `@import` in CLAUDE.md | Defeats the lazy-load benefit — every session pays for content it may not use. Article's "tell CLAUDE.md to read them when relevant" approach kept. |
| Hook with global-ruff fallback after project-local lookup | Adds version-drift risk back. Fail-loud when no project venv is present is the design, not a gap. |
| Block at the matcher (`Edit|Write|MultiEdit` and only `*.py`) | Claude Code's matchers filter on tool name, not file path. Filtering inside the hook is the only option. |

## Consequences

- New: `dotfiles/.claude/CLAUDE.md` (Stow-linked to `~/.claude/CLAUDE.md`).
- New: `dotfiles/.claude/hooks/ruff-edit.sh`. Stow folds the new `hooks/` directory into `~/.claude/hooks/` automatically.
- Modified: `dotfiles/.claude/settings.json` — added `PostToolUse` hook entry.
- Modified: `standards/repo-documentation.md` — `## CLAUDE.md hierarchy` section + `<sub-project>/CLAUDE.md` row in the Files table.
- Modified: `CLAUDE.md` (dev-playbook root) — LaTeX-in-Markdown rules promoted to global; "no secrets" line dropped (already part of base behavior).
- Removed: `dotfiles/CLAUDE.md`. Its content was redundant with `rules/edit-in-dev-playbook.md` and the dev-playbook root CLAUDE.md, and it was being loaded universally as a side effect of where Stow placed its symlink.
- New rule that any future hook script `SHALL` flow signal to Claude (exit 2 + stderr) or stay silent (exit 0). Other non-zero exit codes go only to the human-visible terminal scrollback and are not used.
- Open follow-ups (deliberately deferred):
  - Watcher-pair pattern for execution/direction drift on long sessions.
  - `bin/transcript-reader` to enable transcript mining for config gaps.
  - Worklog auto-post hook on substantial task completion.
  - `standards/agent-hooks.md` to be extracted if a second hook lands and shared conventions emerge.
- The cookiecutter project template (`project-template/`) does not yet propagate any of these conventions. Cookiecutter-generated repos start with their own pyproject.toml + uv setup, which means the edit-time hook works for them out of the box. No template change needed for this Decision Record.

## Amendment (2026-06-06) — edit-transient lint rules (issue #78)

### Problem

The edit-time hook fires after *every* `Edit`/`Write`, but a multi-location
refactor (rename a symbol, move a definition) can only be expressed as a
*sequence* of single-location edits. The file therefore necessarily passes
through intermediate states where a binding is briefly unused or a name is
briefly undefined. With the full rule set live on every edit, those transient
states get "corrected" destructively:

1. Edit the `import` to the new name; the new import is momentarily unused.
2. `ruff check --fix` judges it unused (**F401**) and **deletes the import**.
3. Subsequent edits reference a now-undefined name, cascading **F821**, and the
   hook exits non-zero on each transient state.

A routine rename became corruption the model had to detect and undo, rather than
a clean series of edits.

### Decision

The edit-time `check` step now passes `--ignore F401,F811,F821,F841` — the four
pyflakes name-binding rules a multi-step edit unavoidably passes through:

| Rule | Meaning | Why edit-transient |
|---|---|---|
| F401 | unused import | the renamed import is unused until its call sites are updated; `--fix` *deletes* it |
| F841 | unused local variable | the variable analogue of F401; `--fix` *deletes* the assignment |
| F811 | redefinition of unused name | both old and new definitions coexist mid-move |
| F821 | undefined name | a usage updated before its import/definition is briefly undefined |

`--ignore` on the ruff CLI *extends* the project's configured ignore list rather
than replacing it (verified on ruff 0.15.14), so a project's own disabled rules
stay disabled.

### Why this loses no coverage

Pre-commit (the dev-playbook `ruff` + `ruff-format` hooks; `astral-sh/ruff-pre-commit`
in consumer repos) runs the **full** rule set and stays the gate of record for
these four. The edit-time hook was always *additive* fast feedback, not the
enforcing gate — so relaxing four rules there changes only *when* a genuinely
unused import is reported (commit time instead of mid-edit), never *whether*.
Everything else still applies at edit time: `ruff format`, all other safe
autofixes, and exit-2 blocking on any real unfixable lint (e.g. E711).

### Considered but not done

Moving *all* lint/checking out of the edit-time hook and onto pre-commit only.
That would more fully honor "this should happen at pre-commit," but it discards
the in-loop feedback Decision Record 0002 deliberately added (the model corrects without a
commit round-trip). Deferred as a separate decision; the minimal fix above
removes the corruption without giving that up.

### Changed

- `dotfiles/dot-claude/hooks/ruff-edit.sh` — `check --fix` gains
  `--ignore F401,F811,F821,F841`, with a comment cross-referencing this amendment.
