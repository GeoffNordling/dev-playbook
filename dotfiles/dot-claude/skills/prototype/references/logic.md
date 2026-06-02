# Logic Prototype

A throwaway harness that lets you drive a state model by hand — for questions about business logic, state transitions, or data shape that look fine on paper and only feel wrong once pushed through real cases.

## When this is the right branch

- "Does this state machine handle the case where X then Y?"
- "Does this data model actually represent the case where…?"
- "I want to feel out what the API should be before writing it."
- Anything where you want to press buttons and watch state change.

## Process

### 1. State the question

Write down, in one paragraph at the top of the prototype, what state model and what question you're prototyping. A logic prototype that answers the wrong question is pure waste — make the question explicit so it can be checked later, including by whoever returns to it.

### 2. Isolate the logic in a portable module

Put the part that answers the question behind a small, pure interface that could be lifted into the real codebase unchanged. Pick the shape that fits the question, not the one easiest to wire to a harness:

- **Pure reducer** — `(state, action) -> state`. Discrete events, single state value.
- **State machine** — explicit states and transitions, when "which actions are even legal right now" is part of the question.
- **A set of pure functions** over a plain data type — no implicit current state, just transformations.
- **A class or module with a clear method surface** — when the logic genuinely owns ongoing internal state.

Keep it pure: no I/O, no terminal or UI code, no logging for control flow. The harness calls into it; nothing flows back. This is what survives the prototype — the harness gets deleted, the validated module gets lifted.

### 3. Build the smallest harness that exposes the state

A hand-driven loop: read one input, dispatch to a handler that mutates state, re-render the full relevant state, repeat until quit. Use whatever the project already runs (a TUI, a notebook, a REPL script) — don't add a new runtime just for the prototype.

Each frame shows two things: the current state (one field per line or formatted, diff-friendly), then the available actions. Replace the view each step rather than appending, so there's one stable frame instead of growing scrollback.

### 4. Make it runnable in one command

Add it to the project's existing task runner. If there's none, put the command at the top of the prototype's notes.

### 5. Drive it, or hand it over

The interesting moments are "wait, that shouldn't be possible" or "huh, I assumed X would be different" — those are bugs in the *idea*, which is the whole point. Add actions as the question evolves; prototypes are meant to grow.

## Anti-patterns

- **Tests.** A prototype that needs tests is no longer a prototype.
- **Real database.** In-memory unless the question is specifically about persistence.
- **Generalizing.** No "what if we want to support X later." One question.
- **Blurring the logic and the harness.** If the module references I/O, prompts, or rendering, it's no longer liftable — and the liftable module is the only thing worth keeping.
