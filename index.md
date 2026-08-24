---
okf_version: "0.1"
---

# dev-playbook — bundle index

The meta repo that governs every other repository in the workspace: what they
standardize on, how their work is tracked and built, and how the agents that
work them are configured. Start at [dev-playbook](/README.md).

- [dev-playbook](/README.md) — The dev-playbook meta repo — workspace standards, the software factory definition, agent configuration, CLI tools, and reusable harness patterns
- [Candidates](/CANDIDATES.md) — Uncommitted future work — described, not yet promoted to issues
- [CLOA Abstractions](/CLOA-ABSTRACTIONS.md) — The noun-and-verb abstractions that make documentation understandable at the CLOA, and the loop that generates them
- [CLOA Chains](/CLOA-CHAINS.md) — The ledger of finalized reference chains — one recorded entry per unit, written down as it is ruled
- [Factory Survey](/FACTORY-SURVEY.md) — One session's full read of the software factory — a classification of its files, the intent they carry, and sketches for a possible native rewrite
- [No More Slop](/NO-MORE-SLOP.md) — The branch plan — goal, principles, the two tracks, and the current step
- [Vocabulary](/CONTEXT.md) — The workspace's established vocabulary — the canonical terms to use exactly

## Directories

- [docs/](/docs/index.md) — Surveys of third-party tooling and the Decision Records
- [dotfiles/](/dotfiles/index.md) — Claude Code configuration — skills, rules, settings, hooks — managed via GNU Stow, symlinked into home
- [harness-recipes/](/harness-recipes/index.md) — Reusable harness orchestration patterns — prose descriptions of multi-agent workflows backed by code and skills
- [instruments/](/instruments/index.md) — Purpose-built artifact formats and their tooling
- [scripts/](/scripts/index.md) — Executable hook entry points and local dev scripts that automate cross-repo workspace tasks; shared libraries live in src/dev_playbook/
- [software-factory/](/software-factory/index.md) — What the software-factory/ directory holds — the two-region state machine, the factory's operating contract, and its user checkpoints
- [standards/](/standards/index.md) — Cross-project engineering standards that apply to every repository in the workspace
