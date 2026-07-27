# shellcheck shell=bash
# Machine-specific environment — sourced by ~/.bashrc via the ~/.bashrc.d/* loader.
#
# One file, not one per machine: the differences are few enough that a runtime
# branch is easier to follow than a generated file, and this way both machines
# read the same source.

# Cross-repo citations (`~/workspace/<repo>/...`) resolve only where that repo
# is cloned. Fedora is the primary dev machine and has them all; WSL
# deliberately does not, so ref-lint there would report absent repos as broken
# documents — a claim about the environment dressed up as a claim about the
# docs. Skip it. playbook-lint announces `ref-lint skipped (SKIP)` on stderr
# every run, so this never becomes a silent hole, and the same reasoning holds
# for every repo on this machine, not just dev-playbook.
#
# The judgments cache-gate has the same shape. Its seen-set lives in
# ~/.cache/skipcache and is filled by a run-judgments fleet run, so it is
# machine-local by construction and empty on any machine that has never run
# the fleet. Judgments are a Fedora activity and are neither installed nor ever
# expected to run on WSL; there the gate would fail every judgment as an
# uncached miss. SKIP_JUDGMENTS turns each into a named pytest skip, so the
# suite still reports exactly what went unchecked.
if grep -qi microsoft /proc/version 2>/dev/null; then
	export SKIP="${SKIP:+$SKIP,}ref-lint"
	export SKIP_JUDGMENTS=1
fi
