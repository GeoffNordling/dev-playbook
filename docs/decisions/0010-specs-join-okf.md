---
type: Decision-Record
title: Specs Join OKF — Reversing the specs/ Carve-Out
description: Reverse the planned specs/ carve-out from the OKF bundle — SDD spec items gain OKF frontmatter and per-folder indexes instead of being exempted
date: 2026-07-13
---

# Specs Join OKF — Reversing the specs/ Carve-Out

Issue #189 originally proposed carving `specs/` out of the OKF bundle
entirely, exempting SDD spec items from frontmatter and index-freshness
rules. That direction is reversed: SDD spec items join OKF instead — each
spec file gains simple YAML frontmatter (`type: Spec-Item`, navigation-only,
never duplicating the body's title/statement) and each spec folder gains an
`index.md`, implemented on the spec-tools side in
[GeoffNordling/spec-tools#54](https://github.com/GeoffNordling/spec-tools/issues/54).
The carve-out was hasty — `specs/` should conform to the bundle boundary
like any other concept-doc tree, not be exempted from it. `classify()`
already buckets `specs/**.md` as concept docs and `specs/**/index.md` as
indexes, so this needs no dev-playbook code change; only the type registry
gains one `Spec-Item` row (one row for all three item kinds — `feat`/`req`/
`dsn` — since the kind lives in the SDD body, never duplicated into the
type) and `skeleton.md`'s `specs/` row is rewritten to state the new rule.
