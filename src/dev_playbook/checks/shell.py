"""The shell family: the rules of ``standards/shell/``.

Two of its rules are decided by tools, and are registered by hook name.
"""

from dev_playbook.check_registry import tool_check

tool_check("shell.shellcheck-clean", hook="shellcheck", module=__name__)
tool_check("shell.formatted-by-shfmt", hook="shfmt", module=__name__)
