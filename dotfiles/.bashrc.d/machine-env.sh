# shellcheck shell=bash
# Machine-specific environment. What differs and why: ~/workspace/dev-playbook/docs/machines.md
#
# Detection is duplicated here rather than calling dev_playbook.dotfiles.machine:
# a sourced fragment runs on every interactive shell and cannot afford a Python
# subprocess to learn one fact. A new machine has to touch both anyway.
if grep -qi microsoft /proc/version 2>/dev/null; then
	# playbook check announces the skip on every run, so it never goes silent.
	export SKIP="${SKIP:+$SKIP,}workspace"
fi
