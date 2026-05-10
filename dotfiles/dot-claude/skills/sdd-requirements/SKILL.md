---
name: sdd-requirements
description: Author functional requirements (`feat` and `req` items) following the workspace SDD standards. Use when an SDD-mode issue is in `phase/requirements` and needs `feat`/`req` items written, or when the user asks to draft/extend functional requirements for a tracer-bullet issue.
disable-model-invocation: false
model: opus
effort: xhigh
argument-hint: "<issue-number>"
---

# SDD Requirements

Author the project's functional requirements — `feat` (high-level capability) and `req` (functional requirement) items — following the workspace SDD standards.

## First steps

1. **Required reading — do not skip.** Use the Read tool on each file below before any other action. If any file is missing or unreadable, stop and surface that to the user — do not proceed without the standards loaded.
   - [Spec standard](~/workspace/spec-tools/sdd-standards/spec-standard.md) — item anatomy, IDs, artifact types, coverage chain, keyword reference, EARS prose rules, file organization. The full grammar.
   - [Workflow standard](~/workspace/dev-playbook/standards/workflow.md) — labels, worktree convention, PR mechanics, spec-tools bootstrap caveat.

   After reading, post exactly this confirmation line to the user before proceeding: `Loaded: spec-standard, workflow`.
2. **Run `pwd`.** The dispatcher cd's into the worktree before invoking this skill, but the env header's CWD was captured before that. Trust `pwd`, not the header — composing paths from a stale CWD lands outside the worktree.
3. **Require an issue number** in `$ARGUMENTS`. If empty, stop and tell the user to invoke via `/sdd <N>`.
4. Run `gh-show $ARGUMENTS` to load the issue. The body IS the contract.
5. If `pwd` did not already show a worktree path, resolve the worktree per the [workflow standard](~/workspace/dev-playbook/standards/workflow.md#branch-and-worktree). All subsequent steps run inside it.
6. Read the project's existing specs:
   - `specs/functional_requirements.md` (or `specs/functional_requirements/index.md` for folder-form).
   - `CONTEXT.md` for domain vocabulary.
7. Read the project's `CLAUDE.md`.
8. Tell the user what you found and align on scope.

## Mandatory plan gate

Before drafting any spec text, present a written plan covering scope (which areas you will specify) and approach (key behaviours to capture, ambiguities to resolve). Wait for explicit user approval. Silence is not approval.

## Drafting

- Use the interview pattern. Ask clarifying questions about behaviour, scope, and edge cases before drafting. Surface ambiguities before encoding assumptions.
- Invoke /grill-with-docs when domain terminology is fuzzy or `CONTEXT.md` needs updating.
- Write each item per the spec standard: backticked `type~name~revision` ID, `Description:` body using EARS templates and obligation vocabulary, `Covers:` for non-roots, `Needs:` for chain continuation.
- One obligation level per item. If `SHALL` and `SHOULD` content mixes, split into separate items.
- Out-of-scope sections: ask the user whether anything belongs there. If yes, capture it. If no, write the section with `NA`.

## Closing review pass

Before declaring the phase done, run the rubric. Each item is a yes/no check.

- [ ] Every `req` has a `Covers:` to a `feat` (or is a root)?
- [ ] Every `Description:` uses an EARS sentence template?
- [ ] Each item has exactly one obligation level (no `SHALL` mixed with `SHOULD`)?
- [ ] Every item declares `Needs:` or carries `AgentReview:` (no silent chain termination)?
- [ ] Every `feat`'s out-of-scope section is answered (`NA` is fine)?

Surface failures and iterate until the rubric is clean.

## Closing the phase

When the user approves and the rubric passes:

1. **Final check sweep — leave the tree green.** Run the project's test suite, lint, format, and typecheck (per `CLAUDE.md` / `Makefile`). If a command is not defined for the project (e.g., a greenfield repo with no tests yet), note the absence and continue. If any defined command fails, stop and surface the failure — it may have been introduced by this phase or pre-date it, but it must be visible and resolved before the phase closes. Do not commit or bump the phase label on a red tree.
2. Run /commit to commit the spec markdown.
3. Bump the issue's phase label:
   ```bash
   gh issue edit $ARGUMENTS --remove-label "phase/requirements" --add-label "phase/design"
   ```
4. Report: phase done. The user re-invokes `/sdd <N>` when ready for design.

## Output

Spec markdown only — no code, no tests, no design items.
