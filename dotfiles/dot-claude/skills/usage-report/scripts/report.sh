#!/usr/bin/env bash
# Prints context-window and subscription rate-limit usage from the cache that
# statusline.sh writes on every status-line render. Exits non-zero with a
# diagnosis rather than reporting a number it cannot stand behind.
set -euo pipefail

cache="${XDG_CACHE_HOME:-$HOME/.cache}/claude-code/usage.json"
# There is no on-demand data source: rate_limits/context_window exist only in
# the JSON the harness pipes to statusline.sh, and the harness — not this
# script — decides when that runs (after each assistant message). This bound
# is how "stale" gets caught rather than silently served as current; it is
# not, and cannot be, a guarantee of real-time data.
max_age=120

if [ ! -f "$cache" ]; then
	echo "ERROR: no cache at $cache" >&2
	echo "The status line writes it on every render, so its absence means statusLine is not configured or not loading." >&2
	exit 1
fi

age=$(jq -r 'now - .captured_at | floor' "$cache")
if [ "$age" -gt "$max_age" ]; then
	echo "ERROR: cache is ${age}s old (max ${max_age}s) — the status line has stopped updating it." >&2
	echo "These numbers would be stale; refusing to report them as current." >&2
	exit 1
fi

if [ "$(jq -r 'if .rate_limits == null and .context_window == null then "yes" else "no" end' "$cache")" = "yes" ]; then
	echo "ERROR: cache present (captured $(jq -r '.captured_at | todate' "$cache")) but both rate_limits and context_window are null." >&2
	echo "Both populate only after the first API response of a session." >&2
	exit 1
fi

# context_window, five_hour, and seven_day can each be absent independently —
# say so per line rather than printing a hole or failing the whole report.
# five_hour resets within the day, so time alone is unambiguous; seven_day can
# land on the same weekday as today, so it needs the date.
#
# glide-path deviation: each rate-limit window is assumed to consume its quota
# linearly from window start (resets_at - duration) to window end (resets_at).
# expected% = elapsed_fraction * 100; deviation = used% - expected%, in whole
# percentage points. Positive means burning faster than linear pace.
jq -r '
  def fmtk:
    if . == null then "?"
    elif . >= 1000 then ((./1000*10|round)/10|tostring) + "k"
    else tostring
    end;
  def signed:
    if . > 0 then "+\(.)" elif . < 0 then "\(.)" else "0" end;
  def win(w; tag; fmt; dur):
    if w == null then "\(tag)  ABSENT"
    else
      (w.resets_at - dur) as $start
      | ((now - $start) / dur) as $frac
      | if $frac < 0 or $frac > 1 then
          "\(tag)  \(w.used_percentage | round)%  glide UNKNOWN (window boundary stale)  resets \(w.resets_at | strflocaltime(fmt))"
        else
          ($frac * 100) as $expected
          | ((w.used_percentage - $expected) | round) as $dev
          | "\(tag)  \(w.used_percentage | round)%  glide \($dev|signed)pp (limit \($expected|round)%)  resets \(w.resets_at | strflocaltime(fmt))"
        end
    end;
  (if .context_window == null then "context    ABSENT"
   else
     ((.context_window.total_input_tokens // 0) + (.context_window.total_output_tokens // 0)) as $used
     | "context    \(.context_window.used_percentage | round)%  \($used|fmtk)/\(.context_window.context_window_size|fmtk) tokens"
   end),
  win(.rate_limits.five_hour; "five_hour"; "%H:%M %Z"; 18000),
  win(.rate_limits.seven_day; "seven_day"; "%b %-d %H:%M %Z"; 604800)
' "$cache"
