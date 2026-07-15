---
name: prototype
description: Build throwaway code that answers one design question, then keep only the answer. Routes between a logic branch (a portable pure module driven by hand) and a presentation branch (several structurally-different variants on one switchable surface). Use when the user wants to prototype, sanity-check a state machine or data model, mock up alternatives, explore design options, or says "prototype this", "let me play with it", "try a few designs".
disable-model-invocation: false
model: inherit
effort: high
---

# Prototype

A prototype is throwaway code that answers **one** question. The question decides the shape; the answer is the only thing you keep.

This skill is engine-agnostic. A prototype can be driven by hand in a session or run by an autonomous loop — how it's executed changes neither what a prototype is nor where its code lives.

## Pick a branch

Identify the question being answered — from the prompt, the surrounding code, or by asking:

- **"Does this logic / state model hold up?"** → [logic.md](references/logic.md). A portable pure module (reducer, state machine, or function set) behind a throwaway harness, pushed through cases that are hard to reason about on paper.
- **"What should this look like / how should this read?"** → [presentation.md](references/presentation.md). Several structurally-different variants on one switchable surface, judged against the real surrounding context.

Getting the branch wrong wastes the prototype. If it's genuinely ambiguous and the user is unreachable, default by the surrounding code (a backend module → logic; a rendered surface → presentation) and state the assumption at the top of the prototype.

## Where prototype code lives

Decide this *with the user* — don't guess it. Before creating the prototype, say where it will go and why; let them confirm or redirect.

The default home is a top-level `prototypes/<name>/` directory, a sibling of `src/` — **never** under `src/`, which would put it on the import path. Production code does not import from `prototypes/`; the prototype may merge to `main` but is not integrated until it graduates. This is the right home for anything not yet trusted, and the safe fallback when no other location is settled.

The usual reason to put it elsewhere is judgement: a presentation variant often only reads true butting up against the real page or module, so it may be worth living next to what it prototypes — named so a casual reader sees it's a prototype, not production. That's a call to make together in the moment, not a rule to apply silently.

If the user is unreachable (an autonomous run), don't invent a placement — use `prototypes/<name>/` and note where it went so the choice can be revisited.

## Rules for both branches

1. **Throwaway from day one, named as such.** No tests, no error handling beyond what makes it runnable, no abstractions, no "what if we need X later."
2. **One command to run.** Use the project's existing task runner; the user starts it without thinking.
3. **No persistence by default.** State lives in memory. If the question *is* about persistence, hit a scratch store named so it's obviously disposable.
4. **Surface the state.** After every action (logic) or on every variant switch (presentation), show the full relevant state so the user sees what changed.
5. **Keep the question-answering part portable.** The harness or shell is disposable; the module behind it should lift into real code unchanged.

## When done

The answer is the only durable artifact. Capture it — and the question it answered — somewhere lasting: a commit message, a Decision Record (see [Decision Record conventions](~/workspace/dev-playbook/standards/decisions/records.md)), an issue, or a `NOTES.md` beside the prototype. If the user is around, that's a quick conversation; if not, leave the placeholder so the verdict can be filled in before the prototype is deleted or absorbed.

Then **graduate or delete**: fold the validated decision into real code — rewritten to production standard, since the prototype was written under throwaway constraints — or remove it. Don't leave prototypes rotting in the repo.
