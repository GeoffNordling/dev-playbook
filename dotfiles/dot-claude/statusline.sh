#!/usr/bin/env bash
# Renders the status line and caches the subscription rate-limit payload.
#
# The statusline stdin JSON is the only surface in Claude Code that carries
# Claude.ai (Pro/Max) subscription rate limits, so this script doubles as the
# capture point: a session with no other way to see its own usage reads the
# cache this writes.
set -euo pipefail

input=$(cat)

cache_dir="${XDG_CACHE_HOME:-$HOME/.cache}/claude-code"
cache="$cache_dir/usage.json"
mkdir -p "$cache_dir"

# rate_limits and context_window are absent until the first API response of a
# session (rate_limits never appears under API-key auth). Record both
# explicitly as null with a timestamp so a reader can tell "captured, not yet
# populated" from "never captured".
#
# Only replace the cache when jq actually produced a record. On unparseable
# stdin jq exits 0 with no output, and writing that through would destroy the
# last good reading. Leaving it untouched is safe: the reader refuses anything
# older than its staleness bound, so a wedged writer surfaces there.
if payload=$(jq -c --argjson at "$(date +%s)" \
	'{captured_at: $at, session_id: .session_id, rate_limits: (.rate_limits // null), context_window: (.context_window // null)}' \
	<<<"$input" 2>/dev/null) && [ -n "$payload" ]; then
	printf '%s\n' "$payload" >"$cache.tmp" && mv "$cache.tmp" "$cache"
fi

model=$(jq -r '.model.display_name // "?"' <<<"$input")
ctx=$(jq -r '.context_window.used_percentage // empty' <<<"$input")
five_h=$(jq -r '.rate_limits.five_hour.used_percentage // empty' <<<"$input")
five_h_reset=$(jq -r '.rate_limits.five_hour.resets_at as $r | if $r == null then empty else ($r | strflocaltime("%H:%M")) end' <<<"$input")
week=$(jq -r '.rate_limits.seven_day.used_percentage // empty' <<<"$input")
week_reset=$(jq -r '.rate_limits.seven_day.resets_at as $r | if $r == null then empty else ($r | strflocaltime("%b %-d %H:%M")) end' <<<"$input")

out="[$model]"
[ -n "$ctx" ] && out="$out | ctx $(printf '%.0f' "$ctx")%"
if [ -n "$five_h" ]; then
	out="$out | 5h $(printf '%.0f' "$five_h")%"
	[ -n "$five_h_reset" ] && out="$out ($five_h_reset)"
fi
if [ -n "$week" ]; then
	out="$out | 7d $(printf '%.0f' "$week")%"
	[ -n "$week_reset" ] && out="$out ($week_reset)"
fi
echo "$out"
