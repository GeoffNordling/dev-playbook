# Deepening Workflow

How to land a deepening once it's been chosen. Assumes the [architecture vocabulary](~/workspace/dev-playbook/standards/architecture-vocabulary.md) — **module**, **interface**, **seam**, **adapter** — and the [dependency taxonomy](~/workspace/dev-playbook/standards/dependency-taxonomy.md) for classifying what sits behind the seam.

## Testing strategy: replace, don't layer

- Old unit tests on shallow modules become waste once tests at the deepened module's interface exist — delete them.
- Write new tests at the deepened module's interface. The **interface is the test surface**.
- Tests assert on observable outcomes through the interface, not internal state.
- Tests should survive internal refactors — they describe behaviour, not implementation. If a test has to change when the implementation changes, it's testing past the interface.
