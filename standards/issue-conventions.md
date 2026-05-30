# Issue Conventions

How GitHub Issues are authored in workspace repos. Applies at intake — when
an idea becomes one or many tracked issues.

## The body is the brief

The issue body IS the agent brief. Use this format:

```markdown
**Summary:** one-line description

**Current behavior:**
What happens now (or status quo for an enhancement).

**Desired behavior:**
What should happen after the work is complete. Be specific about edge cases and error conditions.

**Key interfaces:**
- `TypeName` — what changes and why
- `functionName()` — what it returns vs what it should return
- Config shape — any new options needed

**Acceptance criteria:**
- [ ] Specific, testable criterion 1
- [ ] Specific, testable criterion 2

**Out of scope:**
- Things that should NOT be changed
- Adjacent features that are separate

**Blocked by:** #<issue-number> (or "None")
```

## Brief principles

- **Durability over precision.** The issue may sit for days or weeks. Describe interfaces, types, and behavioural contracts. File paths and line numbers go stale.
- **Behavioural, not procedural.** Describe what the system should do, not how to implement it. The agent will explore and decide.
- **Testable acceptance criteria.** Each criterion is independently verifiable.
- **Explicit out-of-scope.** Prevents gold-plating.

## Vertical-slice rules

When one idea becomes many issues, break the plan into **tracer bullet** issues. Each issue is a thin vertical slice cutting through ALL integration layers end-to-end, not a horizontal slice of one layer.

- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests).
- A completed slice is demoable or verifiable on its own.
- Prefer many thin slices over few thick ones.
- **Size to the context budget.** Slice thin enough that building one issue keeps the agent well under ~30% of its context window. Split anything bigger.

Publish issues in dependency order so the `Blocked by` field can reference real issue numbers.
