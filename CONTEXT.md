# dev-playbook

The meta repo's domain language — the terms that recur across its standards,
workflow, and skills — so any human or agent writing here picks the same word
for the same concept.

## Language

**human**:
A person, as the actor opposite `agent` in the workflow model — dispatches,
reviews, approves, rejects, owns the brief, taps the YubiKey.
_Avoid_: user (see Relationships)

**user**:
The operator a skill is serving at runtime — the one it asks, tells, reports to.
_Avoid_: human (see Relationships)

**agent**:
A non-human actor that produces or reviews work under the workflow — the
counterpart that makes `human` meaningful.

## Relationships

- A **user** is always a **human**; they are not synonyms but a register split.
  The rule for choosing between them lives in
  [doc-conventions.md](~/workspace/dev-playbook/standards/doc-conventions.md).
- Workflow node, label, and mode names are fixed and always use **human**:
  `human-review`, `phase:human-code-review`, `(human, work)`, HITL.

## Example dialogue

> **Skill body:** "Ask the **user** which behaviour areas matter." — serving the
>   operator, no agent in play -> **user**.
> **Workflow doc:** "The **agent** posts findings; the **human** approves or
>   rejects at the next node." — named opposite agent -> **human**.
> **One file, both:** intake says "quiz the **user** on granularity" *and* "the
>   **human** launches /sdd-design" — both correct.

## Flagged ambiguities

- **`user` is not the "User" settings tier.** "User" / "user-level" /
  "user-allowed" names the `~/.claude/` config scope, not a person. Left as-is.
- **Fixed Claude Code tokens keep `user`:** `user-invocable`, `user-only`,
  `user-facing`, `user-memory`, the `user` transcript message role.
- **Downstream end-users** (a product's customers) are a third sense — neither
  operator nor workflow actor. Out of scope here.
- **`human-readable`** is a fixed compound (formatting for people), unrelated.
