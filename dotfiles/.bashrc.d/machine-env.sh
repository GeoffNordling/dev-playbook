# shellcheck shell=bash
# Machine-specific environment. What differs and why: ~/workspace/dev-playbook/docs/machines.md
#
# Detection is duplicated here rather than calling dev_playbook.dotfiles.machine:
# a sourced fragment runs on every interactive shell and cannot afford a Python
# subprocess to learn one fact. A new machine has to touch both anyway.
if grep -qi microsoft /proc/version 2>/dev/null; then
	# Both detectors announce the skip on every run, so neither goes silent.
	export SKIP="${SKIP:+$SKIP,}ref-lint"
	export SKIP_JUDGMENTS=1
	# There is no judgment cache here. SKIP_JUDGMENTS handles a plain pytest
	# run; NO_JUDGMENT_CACHE handles the push gate.
	export NO_JUDGMENT_CACHE=1
fi
