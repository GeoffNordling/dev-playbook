---
name: usage-report
description: Report the five_hour and seven_day subscription rate-limit usage from the status-line cache. Use when the user asks about rate-limit usage, remaining quota, or how much of the subscription window is spent.
disable-model-invocation: false
model: sonnet
effort: low
allowed-tools: Bash(bash *usage-report/scripts/report.sh)
---

# Usage Report

Run [report.sh](scripts/report.sh) from this skill's base directory.
