# Compounding Workflow with AI

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
- **Edit-time Python verification.** PostToolUse hook on `Edit|Write|MultiEdit` runs `ruff format` then `ruff check --fix` on edited Python files. Format diffs apply silently; remaining unfixable lints reach Claude inline as system-reminder errors via exit-2 + stderr.
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

Before this ADR, universal preferences were either absent or scattered. After, each piece of instruction has exactly one home and one load trigger.

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
- The cookiecutter project template (`project-template/`) does not yet propagate any of these conventions. Cookiecutter-generated repos start with their own pyproject.toml + uv setup, which means the edit-time hook works for them out of the box. No template change needed for this ADR.
