# guides/ — index

The guides: each is instruction on how to do a kind of work, read before
doing it and organized by the work; a guide cites rules in passing and
is never cited to reject work.

Ordering: alphabetical by title.

- [Adopting a Repo-Scoped Standard](/guides/consuming.md) — The consumer-repo recipe for a first repo-scoped standard — grow the standards/ tree, write its checks where dev-playbook keeps its own, wire the local hook that runs them, and bump the pin
- [Bootstrap](/guides/bootstrap.md) — How a repository joins the workspace — repo-init scaffolds a fresh tree, adoption brings an existing one to green; the GitHub tail and roster enrollment complete both
- [Design and Testing](/guides/design-and-testing.md) — What to settle before writing code or a test — the module's small interface, its ports and accepted dependencies, the loud read of a required value, and the test that names a capability, doubles at the port, and asserts on observable outputs
- [Governed Repo](/guides/governed-repo.md) — What a repo in the workspace declares rather than leaves to be inferred — the GOVERNED roster that names it, where a Decision Record sits, what a merged record freezes, and the workstream it stands up on main; read when adding a repo to the workspace or writing a Decision Record
- [Linking Issues](/guides/linking-issues.md) — The `gh api` calls that make one issue a sub-issue of another or blocked by another, and read the open ones back — relationships the `gh` CLI has no subcommand for
- [Repository Settings](/guides/repo-settings.md) — How the GitHub side of a governed repo is set — the origin, the merge settings, the protect-main ruleset, the labels bootstrap-labels mints, and where a unit of work lives
- [Running a Stint](/guides/running-a-stint.md) — How a launching agent runs an unattended stint with the stint command — what to prepare, the one-time setup and what the image holds, the pre-commit gate every commit runs, the target check the stint runs at each checkpoint, the run and its arguments, what comes back to the repository, the stint's folder, the exit codes, and every rule that stops a stint
- [Slop Tics](/guides/slop-tics.md) — The named tics in Claude's slop writing — the patterns to remove from any workspace document
- [Writing a Check](/guides/writing-a-check.md) — How a check that decides one rule is written — a function registered under the rule's id in the repo's src/<package>/checks/, with its test, run by playbook check in dev-playbook and by playbook check --local in a consumer's own hook; read before writing a check
- [Writing for Agents](/guides/writing-for-agents.md) — The craft behind any document an agent consumes — the two loads, the information hierarchy, context pointers, completion criteria, leading words, and pruning; read to write one, never cited to reject one
- [Writing Predicates](/guides/writing-predicates.md) — How to write a rule so a verifier can decide it — one member, one moment, one bool, the property not the witness, the file it reads named, what not how, the future not the past, no new nouns, the trailer, and what is not a predicate; read before writing a rule
