# docs/ — index

The repo's working papers — a mixture of notes, unenforced policies,
intentions, and explorations — and the Decision Records.

- [External Skill Verdicts](/docs/external-skill-verdicts.md) — The workspace's verdict on every external skill it has evaluated — skill, verdict, date, and reason, grouped by source
- [Headless Operation](/docs/headless.md) — What `claude -p` guarantees on subscription — billing and the credentials that outrank the login, how stable the policy is, what a run declares about itself, what the harness loads, what the flags buy, and the path-scoped permissions that do not work
- [Machines](/docs/machines.md) — The machines the workspace runs on — one Fedora primary and two Windows/WSL secondaries — and what differs between them
- [Measurement Derivation](/docs/measurement-derivation.md) — How raw captured hook events become measurements — the store, the assertions every report runs first, event semantics, filters, and metric formulas
- [Pin Update Process](/docs/pin-update-process.md) — The one place to learn how a change to dev-playbook main reaches every governed repo — the timer, the update-pins run, the green and red landings, the ledger, the hand tools — with a pointer to where each part is documented in full
- [Pin Updates Ledger](/docs/pin-updates.md) — Recent runs of update-pins, one row per governed repo over the last three release heads — when it ran, the release head, the verdict, where the bump landed, and the branches still unmerged
- [System Legibility](/docs/system-legibility.md) — The doctrine — the user understands the systems they own without reading all of them — and the principles and ambitions that serve it
- [Working in Loops](/docs/working-in-loops.md) — The doctrine — agents work in loops, and the user works on the loops
- [Writing Improvement Process](/docs/writing-improvement-process.md) — The document-writing problem, the intention to improve it iteratively, and the capture step that records what goes wrong each time a document is written

## Directories

- [decisions/](/docs/decisions/index.md) — The Decision Records directory — numbered, immutable records of decisions and their rationale
- [mirrors/](/docs/mirrors/index.md) — Upstream specifications the Standards cite, vendored verbatim so the text a Standard defers to is fixed, readable offline, and never edited here
- [writing-improvement-process/](/docs/writing-improvement-process/index.md) — The writing-improvement process's files — the catalog of recurring problems in Claude's document writing
