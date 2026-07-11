---
okf_version: "0.1"
---

# dev-playbook — bundle index

- [dev-playbook](/README.md) — The dev-playbook meta repo — workspace standards, workflow definitions, agent configuration, CLI tools, and reusable harness patterns
- [Vocabulary](/CONTEXT.md) — The workspace's established vocabulary — the canonical terms to use exactly; currently the module-architecture set (Module, Interface, Depth, Seam, Adapter, Leverage, Locality)

## Directories

- [docs/](/docs/index.md) — Surveys of third-party tooling and the architecture decision records
- [dotfiles/](/dotfiles/index.md) — Claude Code configuration — skills, rules, settings, hooks — managed via GNU Stow, symlinked into home
- [harness-recipes/](/harness-recipes/index.md) — Reusable harness orchestration patterns — prose descriptions of multi-agent workflows backed by code and skills
- [instruments/](/instruments/index.md) — Purpose-built artifact formats and their tooling
- [protocols/](/protocols/index.md) — Formal human–agent collaboration protocols — problem-decomposition algorithms and the skills that operationalize them
- [scripts/](/scripts/index.md) — Executable hook entry points and local dev scripts that automate cross-repo workspace tasks; shared libraries live in src/dev_playbook/
- [standards/](/standards/index.md) — Cross-project engineering standards that apply to every repository in the workspace
- [workflow/](/workflow/index.md) — What the workflow/ directory holds — the intake-to-merge state machine and the standards defining each phase
