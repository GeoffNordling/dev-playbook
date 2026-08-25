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
# at a steady pace across the time it's actually usable. expected% = (elapsed
# usable time / total usable time) * 100; deviation = used% - expected%, in
# whole percentage points. Positive means burning faster than the assumed
# pace. five_hour treats the whole window as usable — a session-scale window
# has no structural dead time. seven_day does not: nobody runs Claude Code
# around the clock, so treating all 168 hours as usable overstates expected
# usage overnight. seven_day instead assumes zero usage 22:00-08:00
# America/New_York (a fixed personal-schedule assumption, not geo-aware —
# if you're traveling or working odd hours, the glide number will read more
# anomalous than it really is). Hardcoded to America/New_York rather than the
# host's ambient TZ so the report means the same thing regardless of what
# timezone the machine running it happens to be set to.
#
# DST is handled per-instant, not by picking one offset for the whole week:
# `mktime(localtime(t)) - t` asks the system tzdata what UTC offset was
# actually in effect at instant t, so a DST transition inside the trailing
# 7 days resolves correctly on both sides. US Eastern transitions land at
# 02:00 local, outside the 08:00-22:00 active window, so a full 7-day span
# always nets exactly 98 active hours regardless of whether it crosses one —
# what per-instant handling actually buys is a correct *partial* elapsed-
# active figure when "now" falls after a transition inside the window.
TZ="America/New_York" jq -r '
  def fmtk:
    if . == null then "?"
    elif . >= 1000 then ((./1000*10|round)/10|tostring) + "k"
    else tostring
    end;
  def signed:
    if . > 0 then "+\(.)" elif . < 0 then "\(.)" else "0" end;

  # Exact UTC offset (seconds) in effect at instant `.`, per tzdata for the
  # process TZ. Not a fixed offset — evaluated per instant so it tracks DST.
  def local_offset: . as $t | ($t | localtime | mktime) - $t;

  # Seconds of local 08:00-22:00 "active" time between t1 and t2 (t1 <= t2).
  # Sums the active window ([local 08:00, local 22:00), converted to real
  # epoch via the local_offset for that day) over each spanned calendar day,
  # clamped to [t1, t2]. Day bucketing uses one seed offset with a 1-day margin on
  # each side; that only affects which days get iterated, not the per-day
  # math, and spurious days clamp to a zero contribution.
  def active_seconds($t1; $t2):
    if $t2 <= $t1 then 0
    else
      ($t1 | local_offset) as $seed
      | (($t1 + $seed) / 86400 | floor) as $day0
      | (($t2 + $seed) / 86400 | floor) as $day1
      | reduce range($day0 - 1; $day1 + 2) as $d
          (0; . + (
            ($d * 86400 + 43200 - $seed) as $noon_guess
            | ($noon_guess | local_offset) as $off_d
            | ($d * 86400 + 28800 - $off_d) as $active_start
            | ($d * 86400 + 79200 - $off_d) as $active_end
            | ([$active_end, $t2] | min) as $hi
            | ([$active_start, $t1] | max) as $lo
            | ([$hi - $lo, 0] | max)
          ))
    end;

  # strflocaltime %Z/%z are unreliable on this jq build — %Z always prints
  # the standard-time abbreviation and %z always prints +0000, regardless of
  # the real offset at that instant (verified: a known-EDT epoch still
  # prints EST / +0000). The hour/date fields it produces ARE correctly
  # localized, so format without a zone directive and append a fixed "ET"
  # label instead of trusting a broken one.
  def win(w; tag; fmt; dur):
    if w == null then "\(tag)  ABSENT"
    else
      (w.resets_at - dur) as $start
      | ((now - $start) / dur) as $frac
      | if $frac < 0 or $frac > 1 then
          "\(tag)  \(w.used_percentage | round)%  glide UNKNOWN (window boundary stale)  resets \(w.resets_at | strflocaltime(fmt)) ET"
        else
          (if tag == "seven_day"
           then (active_seconds($start; now) / active_seconds($start; w.resets_at) * 100)
           else ($frac * 100)
           end) as $expected
          | ((w.used_percentage - $expected) | round) as $dev
          | "\(tag)  \(w.used_percentage | round)%  glide \($dev|signed)pp (limit \($expected|round)%)  resets \(w.resets_at | strflocaltime(fmt)) ET"
        end
    end;
  (if .context_window == null then "context    ABSENT"
   else
     ((.context_window.total_input_tokens // 0) + (.context_window.total_output_tokens // 0)) as $used
     | "context    \(.context_window.used_percentage | round)%  \($used|fmtk)/\(.context_window.context_window_size|fmtk) tokens"
   end),
  win(.rate_limits.five_hour; "five_hour"; "%H:%M"; 18000),
  win(.rate_limits.seven_day; "seven_day"; "%b %-d %H:%M"; 604800)
' "$cache"
