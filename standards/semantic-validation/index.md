# standards/semantic-validation/ — index

The Semantic Validation card's one Standard, a repo's judgment declarations,
and the guides to the cache gate and to consuming the tooling. Start at
[Judgment Declarations](/standards/semantic-validation/declarations.md).

Ordering: reading order.

- [Judgment Declarations](/standards/semantic-validation/declarations.md) — A repo's judgment declarations — the opt-in table, one file per claim family, an entry's fields, and the bar a claim clears
- [The Cache Gate](/standards/semantic-validation/cache-gate.md) — How a judgment is gated — the offline cache check a pytest makes, the spectrum of positions a repo picks from, and the environment variable that arms the gate
- [Consuming Judgments](/standards/semantic-validation/consuming.md) — How another repo picks the judgments tooling up — the editable path dependency, its own declarations, a position on the gate spectrum, the lint hook, and sweep pickup
