"""Refuse any run that could bill the metered API instead of the subscription.

Run non-interactively, Claude prefers a configured API key over the
subscription login, and says nothing about it. So a misconfigured run succeeds
and quietly costs money. These checks are what stand between the two.

Pure functions over dicts: no subprocess, no container, nothing to observe. So
this is the one module with a test file.
"""

import json
from pathlib import Path

# Set any one of these and the run goes somewhere other than the subscription:
# a metered key, a different endpoint, or a cloud provider's billing.
BILLING_ENV_VARS = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_BASE_URL",
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
    "CLAUDE_CODE_USE_FOUNDRY",
    "ANTHROPIC_PROFILE",
    "ANTHROPIC_FEDERATION_RULE_ID",
    "ANTHROPIC_ORGANIZATION_ID",
)

# CLAUDE_CODE_OAUTH_TOKEN is missing from that list on purpose. It is a
# subscription credential, so it is safe.

# Settings keys that mint a credential or point at a different one.
CREDENTIAL_SETTINGS_KEYS = (
    "apiKeyHelper",
    "awsAuthRefresh",
    "awsCredentialExport",
)


class MeteredBilling(Exception):
    """The run as configured could bill the metered API."""


def metered_env_vars(env: dict[str, str]) -> list[str]:
    """The billing variables that are set in env.

    An empty value counts as unset, which is how the shell treats it. Any
    other value counts as set, even "0" — refusing a disabled-looking flag is
    the safe direction to be wrong in.
    """
    return [name for name in BILLING_ENV_VARS if env.get(name)]


def metered_settings_keys(settings: dict) -> list[str]:
    """The credential keys present in a settings dict."""
    return [key for key in CREDENTIAL_SETTINGS_KEYS if key in settings]


def refuse_if_metered(env: dict[str, str], settings: dict) -> None:
    """Raise unless this run is certain to draw on the subscription.

    Called with the exact environment about to be handed to the container and
    the settings that will exist inside it — not the host's. The container
    gets only what container_argv puts there.
    """
    problems = metered_env_vars(env) + metered_settings_keys(settings)
    if problems:
        raise MeteredBilling(
            "these would route the run to the metered API: " + ", ".join(problems)
        )


def read_settings(path: Path) -> dict:
    """A settings file as a dict, or empty if there is no such file."""
    if not path.exists():
        return {}
    return json.loads(path.read_text())
