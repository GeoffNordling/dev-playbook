---
okf_version: "0.1"
---

# dev-playbook — bundle index

The meta repo that governs every other repository in the workspace: what they
standardize on, how their work is tracked and built, and how the agents that
work them are configured. Start at [dev-playbook](/README.md).

- [dev-playbook](/README.md) — The dev-playbook meta repo — workspace standards, agent configuration, CLI tools, and reusable harness patterns
- [Candidates](/CANDIDATES.md) — Uncommitted future work — described, not yet promoted to issues
- [Vocabulary](/CONTEXT.md) — The workspace's established vocabulary — the canonical terms to use exactly

## Directories

- [doc-types/](/doc-types/index.md) — The documentation type system — what a doc-type is, this repo's instantiation, and one directory per built doc-type
- [docs/](/docs/index.md) — Surveys of third-party tooling and the Decision Records
- [dotfiles/](/dotfiles/index.md) — Claude Code configuration — skills, rules, settings, hooks — managed via GNU Stow, symlinked into home
- [guides/](/guides/index.md) — The guides — instruction on how to do a kind of work, read before doing it and never cited to reject work
- [harness-recipes/](/harness-recipes/index.md) — Reusable harness orchestration patterns — prose descriptions of multi-agent workflows backed by code and skills
- [loops/](/loops/index.md) — The Loop instances — every document typed `Loop`, each a graph of acts, verifications, and yields that drives a state toward a target state
- [scripts/](/scripts/index.md) — Executable hook entry points and local dev scripts that automate cross-repo workspace tasks; shared libraries live in src/dev_playbook/
- [standards/](/standards/index.md) — Cross-project engineering standards that apply to every repository in the workspace
- [workstreams/](/workstreams/index.md) — The workstreams, one directory per line of in-process work, each kept as long as its work runs
