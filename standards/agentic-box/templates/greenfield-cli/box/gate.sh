#!/usr/bin/env bash
set -euo pipefail

# agent's own suite: must exist and pass
# (pytest exits nonzero when no tests are collected, so an empty
#  suite fails the gate by itself)
pytest tools/sessionxml/tests -q

# frozen boundary suite
pytest box/tests/acceptance -q

# emissions present and non-empty
for f in DEVIATIONS.md UPSTREAM.md; do
	test -s "tools/sessionxml/$f" || {
		echo "missing emission: $f"
		exit 1
	}
done

echo "GATE PASS"
