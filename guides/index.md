# guides/ — index

The guides: each is instruction on how to do a kind of work, read before
doing it and organized by the work; a guide cites rules in passing and
is never cited to reject work.

Ordering: alphabetical by title.

- [Adopting a Repo-Scoped Standard](/guides/consuming.md) — The consumer-repo recipe for a first repo-scoped standard — grow the standards/ tree, write and publish a conforming detector, mirror it, and gate it
- [Bootstrap](/guides/bootstrap.md) — How a repository joins the workspace — repo-init scaffolds a fresh tree, adoption brings an existing one to green; the GitHub tail and roster enrollment complete both
- [Design and Testing](/guides/design-and-testing.md) — What to settle before writing code or a test — the module's small interface, its ports and accepted dependencies, the loud read of a required value, and the test that names a capability, doubles at the port, and asserts on observable outputs
- [Governed Repo](/guides/governed-repo.md) — What a repo in the workspace declares rather than leaves to be inferred — the GOVERNED roster that names it, where a Decision Record sits, what a merged record freezes, and the working documentation set it stands up on main; read when adding a repo to the workspace or writing a Decision Record
- [Linking Issues](/guides/linking-issues.md) — The `gh api` calls that make one issue a sub-issue of another or blocked by another, and read the open ones back — relationships the `gh` CLI has no subcommand for
- [Repository Settings](/guides/repo-settings.md) — How the GitHub side of a governed repo is set — the origin, the merge settings, the protect-main ruleset, the labels bootstrap-labels mints, and where a unit of work lives
- [Slop Tics](/guides/slop-tics.md) — The named tics in Claude's slop writing — the patterns to remove from any workspace document
- [Writing a Detector](/guides/writing-a-detector.md) — The command-line contract of a first-party detector — the order main runs in, what it answers to --list-rules, the line it prints for a finding, and the codes it exits on; read before writing one
- [Writing for Agents](/guides/writing-for-agents.md) — The craft behind any document an agent consumes — the two loads, the information hierarchy, context pointers, completion criteria, leading words, and pruning; read to write one, never cited to reject one
- [Writing Predicates](/guides/writing-predicates.md) — How to write a rule so a verifier can decide it — one member, one moment, one bool, the property not the witness, the file it reads named, what not how, the future not the past, no new nouns, the trailer, and what is not a predicate; read before writing a rule
