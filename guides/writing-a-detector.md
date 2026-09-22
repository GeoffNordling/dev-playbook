---
type: Guide
title: Writing a Detector
description: The command-line contract of a first-party detector — the order main runs in, what it answers to --list-rules, the line it prints for a finding, and the codes it exits on; read before writing one
---

# Writing a Detector

A first-party detector is a script the audited repo hosts at
`scripts/<name>`
([A first-party detector](/standards/standard/detectors.md#a-first-party-detector)).
This guide is the contract that script meets at the command line: the
order `main` runs in, the line it prints for a finding, and the code it
leaves behind. Where the detector is published, which rule it decides,
and which gate runs it are
[Detectors](/standards/standard/detectors.md).

## The order `main` runs in

Write `main` to do these in order:

1. **Answer `--list-rules` and exit.** Under `--list-rules`, print every
   rule id the detector can emit, one per line, and exit 0. The flag
   needs no repository, so it answers before anything is read.
2. **Take the surface, and stand down where it is absent.** Where the
   surface is optional — a `skills/`, `standards/`, or `loops/` tree —
   report no finding and exit 0 in a repo that has no such surface.
3. **Print each finding as one line.** One line per finding, in the
   shape [The finding line](#the-finding-line) gives.
4. **Exit 0, 1, or 2.** 0 when the run is clean, 1 when it has findings,
   and 2 when it cannot run.

## The finding line

A finding takes one line:

```text
location:line: <rule id> message
```

A colon follows the location, and the separators are single spaces. Use
a repo-relative path for the location, or the member's name where the
member is not a file. Omit `:line` for a finding on the whole member.

## Why an absent surface is clean

The alternative, dropping the detector from the repos that lack the
surface, would make the hook set differ from repo to repo and would
leave a repo unpoliced the day it grows the surface. The gap closes
inside the detector, so the wiring stays the same everywhere.

## The gate does not write

A detector inspects and emits findings; by itself it blocks nothing, and
its run at a gate is the audit stationed there. Leave everything git
tracks as you found it
([Read-only](/standards/standard/detectors.md#read-only)).
