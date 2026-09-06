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
  declarative present tense, one concern per document, current-state only,
  none of the named slop tics

## Audit

- [prose-lint](/scripts/prose-lint) — the prose detector; three rules:
  `prose.judgment-spelling`, flagging the British `judgement`/`judgements`
  form in all authored Markdown outside code spans; `prose.banned-word`,
  flagging the banned actor noun (Terminology: the person is the user) in
  every tracked file this workspace authors, of any type, with no code-span or
  fence escape; and `prose.agent-facing-voice`, flagging the first person in
  a harness-loaded agent instruction file (Imperative and second person).
  Verbatim `type: Reference` mirrors and the paths a repo declares in its
  root `.prose-lint-exempt` are outside the scan for every one of the three

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — the **commit gate**, where prose-lint blocks every commit by way of
  the published `playbook-lint` hook
- [document-remove-tics](/dotfiles/dot-claude/skills/document-remove-tics/SKILL.md)
  — **on demand**, rewrites one document to remove the named tics through
  the tics-remover agent, content unchanged, nothing committed

## Adopt

- none
