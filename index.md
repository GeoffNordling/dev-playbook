---
okf_version: "0.1"
---

# dev-playbook — bundle index

- [dev-playbook](/README.md) — The dev-playbook meta repo — workspace standards, workflow definitions, agent configuration, CLI tools, and reusable harness patterns
- [Architecture Vocabulary](/CONTEXT.md) — The shared architecture vocabulary — Module, Interface, Depth, Seam, Adapter, Leverage, Locality — used exactly in every architecture suggestion

## Directories

- [standards/](/standards/index.md) — Cross-project engineering standards that apply to every repository in the workspace
- [docs/](/docs/index.md) — Surveys of third-party tooling and the architecture decision records
- [workflow/](/workflow/index.md) — What the workflow/ directory holds — the intake-to-merge state machine and the standards defining each phase
- [protocols/](/protocols/index.md) — Formal human–agent collaboration protocols — problem-decomposition algorithms and the skills that operationalize them
- [harness-recipes/](/harness-recipes/index.md) — Reusable harness orchestration patterns — prose descriptions of multi-agent workflows backed by code and skills
- [scripts/](/scripts/index.md) — Executable hook entry points and local dev scripts that automate cross-repo workspace tasks; shared libraries live in src/dev_playbook/
- [dotfiles/](/dotfiles/index.md) — Claude Code configuration — skills, rules, settings, hooks — managed via GNU Stow, symlinked into home
