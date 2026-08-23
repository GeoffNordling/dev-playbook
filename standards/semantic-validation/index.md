# standards/semantic-validation/ — index

LLM-judged assertions on files, one concern per document. Start at
[Judgment Declarations](/standards/semantic-validation/declarations.md).

Ordering: reading order.

- [Judgment Declarations](/standards/semantic-validation/declarations.md) — The judgment model and YAML declaration format — claim, evidence, bench, and the content-addressed key
- [The Cache Gate](/standards/semantic-validation/cache-gate.md) — The deterministic pytest gate and the spectrum of positions on it — a judgment is gated iff a pytest asserts its cache entry
- [Consuming Judgments](/standards/semantic-validation/consuming.md) — The consumer-repo recipe — editable path dependency, declarations, a position on the gate spectrum, lint hook, sweep pickup
