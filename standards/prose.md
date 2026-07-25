---
type: Standard-Card
title: Prose
description: Card for the prose standard — how workspace prose is written
---

# Prose

Governs how prose is written — voice, structure, and brevity in every
workspace document.

## Define

- [prose/conventions.md](/standards/prose/conventions.md) — the contract:
  declarative present tense, one concern per document, current-state only

## Audit

- [prose-lint](/scripts/prose-lint) — the prose detector; one rule,
  `prose.judgment-spelling`, flagging the British `judgement`/`judgements`
  form in all authored Markdown outside code spans

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — the **commit gate**, where prose-lint blocks every commit by way of
  the published `playbook-lint` hook

## Adopt

- none
