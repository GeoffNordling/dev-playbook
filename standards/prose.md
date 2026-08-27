---
type: Standard-Card
title: Prose
description: Governs how prose is written in every workspace document — voice, structure, and brevity
---

# Prose

Governs how prose is written in every workspace document — voice,
structure, and brevity.

## Define

- [prose/conventions.md](/standards/prose/conventions.md) — the contract:
  declarative present tense, one concern per document, current-state only

## Audit

- [prose-lint](/scripts/prose-lint) — the prose detector; two rules:
  `prose.judgment-spelling`, flagging the British `judgement`/`judgements`
  form in all authored Markdown outside code spans, and `prose.banned-word`,
  flagging the banned actor noun (Terminology: the person is the user) in
  every tracked file this workspace authors, of any type, with no code-span or
  fence escape — vendored `.agents/` trees, verbatim `type: Reference`
  mirrors, and the paths a repo declares in its root `.prose-lint-exempt` are
  outside the scan, as Terminology exempts them

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — the **commit gate**, where prose-lint blocks every commit by way of
  the published `playbook-lint` hook

## Adopt

- none
