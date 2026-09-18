---
type: Standard-Ruleset
title: Billing Credentials
description: The credentials that would meter a Claude run — the variables and settings keys that carry one, and the four surfaces checked for them
population: "a machine that runs Claude, and every repository worked on it"
---

# Billing Credentials

Work is billed to the subscription. A metered credential — an API key, a
different endpoint, or a cloud provider's billing — routes a run somewhere
else, and Claude run non-interactively prefers a configured credential over
the subscription login without saying so. The run then succeeds and the cost
arrives later, which is why this is a Standard rather than a habit: there is
no loud failure to notice.

Every rule here is checked by `scripts/billing-lint`, and a rule names the
`billing.*` id that checks it. `CLAUDE_CODE_OAUTH_TOKEN` is not a metered
credential; it is a subscription credential and is permitted everywhere.

## No metered variable in the environment

The environment a run starts in sets none of the billing variables
(`billing.no-metered-env`).

The variables are `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`,
`ANTHROPIC_BASE_URL`, `CLAUDE_CODE_USE_BEDROCK`, `CLAUDE_CODE_USE_VERTEX`,
`CLAUDE_CODE_USE_FOUNDRY`, `ANTHROPIC_PROFILE`,
`ANTHROPIC_FEDERATION_RULE_ID`, and `ANTHROPIC_ORGANIZATION_ID`.

An empty value counts as unset, the way the shell treats it. Any other value
counts as set, `0` included: a flag that looks disabled is refused, because
refusing one is cheap and admitting one is not.

## No metered variable in a shell startup file

No shell startup file assigns a billing variable
(`billing.no-metered-shell-config`).

The files are `.bashrc`, `.bash_profile`, `.bash_login`, `.profile`,
`.zshrc`, `.zshenv`, and `.zprofile` in the home directory, plus every file
in `.bashrc.d/`, which the dotfiles loader sources in full.

An assignment here is the same defect as the variable being set, one shell
away: the next login exports it into every process started after. A line
whose first non-blank character is `#` is a comment and is not an
assignment, so a note recording a removed key does not fail the rule.

## No credential in a Claude settings file

No Claude settings file mints a credential, redirects to one, or sets a
billing variable in its `env` block (`billing.no-credential-settings`).

The keys that mint or redirect are `apiKeyHelper`, `awsAuthRefresh`, and
`awsCredentialExport`. The `env` block is checked against the same variable
list as the environment, because Claude Code applies that block to every run
it starts — a credential placed there reaches the model exactly as an
exported one does, and nothing else reports it.

Four files are read: `settings.json` and `settings.local.json` under the
machine's `~/.claude/`, and the same two under the repository's `.claude/`.
The machine's files and the repository's are both checked, so neither a
clean machine nor a clean repository excuses the other.

## A surface that cannot be read is a tool error

A settings file that exists and does not parse, a home directory that
`HOME` does not name, or a file the detector cannot open ends the run with
exit 2 rather than a pass.

A credential the detector could not read is the case the detector exists to
prevent, so an unreadable surface never reports clean. This is
[fail loud](/standards/python/style.md) applied to the detector itself.

## Acronyms

None.
