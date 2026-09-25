# docs/ — index

The repo's working papers — a mixture of notes, unenforced policies,
intentions, and explorations — and the Decision Records.

- [Headless Operation](/docs/headless.md) — Research on `claude -p` — the credential order, how stable subscription billing is, what a run declares about itself, what the harness loads, two flags, and the path-scoped permissions that do not work
- [Machines](/docs/machines.md) — The machines the workspace runs on — one Fedora primary and two Windows/WSL secondaries — and what differs between them
- [Measurement Derivation](/docs/measurement-derivation.md) — Research for a report over the captured hook events — the assertions it would run first, event semantics, filters, metric formulas, and the cost join
- [Pin Update Process](/docs/pin-update-process.md) — The one place to learn how a change to dev-playbook main reaches every governed repo — the timer, the update-pins run, the green and red landings, the ledger, the hand tools — with a pointer to where each part is documented in full
- [Pin Updates Ledger](/docs/pin-updates.md) — Recent runs of update-pins, one row per governed repo over the last three release heads — when it ran, the release head, the verdict, where the bump landed, and the branches still unmerged
- [System Legibility](/docs/system-legibility.md) — The doctrine — the user understands the systems they own without reading all of them — and the principles and ambitions that serve it

## Directories

- [decisions/](/docs/decisions/index.md) — The Decision Records directory — numbered, immutable records of decisions and their rationale
- [mirrors/](/docs/mirrors/index.md) — Upstream specifications the Standards cite, vendored verbatim so the text a Standard defers to is fixed, readable offline, and never edited here
