---
name: sdd-requirements
description: Author functional requirements (`feat` and `req` items) following the workspace SDD standards
disable-model-invocation: true
model: opus
effort: xhigh
argument-hint: "<issue-number>"
---

# SDD Requirements

Author the project's functional requirements — `feat` (high-level capability) and `req` (functional requirement) items — following the workspace SDD standards. The user provides free-form input describing the area to specify or revise.

## Read first

- [Spec standard](~/workspace/dev-playbook/sdd-standards/spec-standard.md) — item anatomy, IDs, artifact types, coverage chain, keyword reference, prose rules (obligation vocabulary and EARS sentence templates), file organization. The full grammar.

## First steps

1. **Require an issue number.** If `$ARGUMENTS` is empty, stop and tell the user to invoke with an issue number (e.g., `/sdd-requirements 18`). The issue is the per-session contract; without it there is no scope.
2. Read GitHub issue #$ARGUMENTS — its body and the most recent `## Agent Brief` comment. The brief pins category, scope, key interfaces, acceptance criteria, and out-of-scope boundaries.
3. Read the project's existing specs if any:
   - `specs/functional_requirements.md` or, if folder-form, `specs/functional_requirements/index.md` and the files it lists.
   - `CONTEXT.md` if it exists, for domain vocabulary.
4. Read the project's `CLAUDE.md`.
5. Tell the user what you found and align on scope before drafting.

## Working with the spec collection

We are bootstrapping `spec-tools` itself; programmatic spec views are not available yet. Work directly with the markdown — read item bodies as needed and use the spec standard as your reference grammar. A future revision of this skill will invoke `spec-tools` for gap reports and aggregate views to identify uncovered requirements at a glance.

## Mandatory plan gate

Before drafting any spec text, present a written plan covering scope (which areas you will specify) and approach (key behaviors to capture, ambiguities to resolve). Wait for explicit user approval. Silence is not approval.

## Drafting

- Use the interview pattern. Ask clarifying questions about behavior, scope, and edge cases before drafting. Surface ambiguities before encoding assumptions. Invoke /grill-me when an interview pass would be heavier than the inline questions in the conversation can carry.
- Invoke /grill-with-docs when domain terminology is fuzzy or `CONTEXT.md` needs updating; that skill produces and sharpens domain docs as decisions land.
- Write each item per the spec standard: backticked `type~name~revision` ID, `Description:` body using EARS templates and obligation vocabulary, `Covers:` for non-roots, `Needs:` for chain continuation.
- One obligation level per item. If `SHALL` and `SHOULD` content mixes, split into separate items.
- Out-of-scope sections: ask the user whether anything belongs there. If yes, capture it. If no, write the section with `NA` so the question is visibly answered.

## Output

Spec markdown only — no code, no tests, no design items. Iterate with the user until the draft is approved.
