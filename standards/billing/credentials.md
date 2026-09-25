---
type: Standard
title: Billing Credentials
description: The credentials that would meter a Claude run — the variables and settings keys that carry one, and the four surfaces checked for them
population: "a machine that runs Claude, with the repository it commits from"
---

# Billing Credentials

Work is billed to the subscription. A metered credential is an API key, a
different endpoint, or a cloud provider's billing. `CLAUDE_CODE_OAUTH_TOKEN`
is a subscription credential, not a metered one.

The **billing variables** are `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`,
`ANTHROPIC_BASE_URL`, `CLAUDE_CODE_USE_BEDROCK`, `CLAUDE_CODE_USE_VERTEX`,
`CLAUDE_CODE_USE_FOUNDRY`, `ANTHROPIC_PROFILE`,
`ANTHROPIC_FEDERATION_RULE_ID`, and `ANTHROPIC_ORGANIZATION_ID`.

> **Why.** Claude run non-interactively prefers a configured credential
> over the subscription login and says nothing. The run succeeds and the
> cost arrives later, so no loud failure shows the fault.

## No metered variable in the environment

The environment the commit runs in sets no billing variable to a value
that is not empty.

`billing.no-metered-variable-in-the-environment` · deterministic

> **Why.** An empty value is unset to the shell. `0` counts as set: a
> flag that looks disabled costs nothing to refuse and money to admit.

## No metered variable in a shell startup file

No line of a shell startup file assigns a billing variable, except a line
whose first non-blank character is `#`.

The shell startup files are `.bashrc`, `.bash_profile`, `.bash_login`,
`.profile`, `.zshrc`, `.zshenv`, and `.zprofile` in the home directory,
and every file in `.bashrc.d/`.

`billing.no-metered-variable-in-a-shell-startup-file` · deterministic

> **Why.** The next login exports an assignment here into every process
> after it. The dotfiles loader sources all of `.bashrc.d/`.

## No credential in a Claude settings file

No Claude settings file has the key `apiKeyHelper`, `awsAuthRefresh`, or
`awsCredentialExport`, or sets a billing variable in its `env` block.

The Claude settings files are `settings.json` and `settings.local.json`
under `~/.claude/` and under the repository's `.claude/`.

`billing.no-credential-in-a-claude-settings-file` · deterministic

> **Why.** Claude Code applies the `env` block to every run it starts. The
> machine's files and the repository's are both read, so a clean machine
> does not excuse a repository that ships a credential, and a clean
> repository does not excuse the machine.
