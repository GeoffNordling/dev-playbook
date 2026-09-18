---
type: Standard-Card
title: Billing
description: Governs how work is billed to Claude — the subscription as the only route, the credentials that would meter a run, and the four surfaces that carry one
---

# Billing

Governs how work is billed to Claude — the subscription as the only route,
the credentials that would meter a run, and the four surfaces that carry
one.

## Define

- [Billing Credentials](/standards/billing/credentials.md)

## Audit

- [billing-lint](/scripts/billing-lint) — three rules over the machine and
  the repository: the live environment (`billing.no-metered-env`), the shell
  startup files (`billing.no-metered-shell-config`), and the Claude settings
  files (`billing.no-credential-settings`)

This is the one detector that reads the machine as well as the repository.
A metered credential is configuration of the machine an agent runs on, so a
detector confined to the repository would pass on a machine that bills every
run.

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — the **commit gate**, where billing-lint blocks every commit by way of
  the published `playbook-lint` hook

The detector is not skipped at the CI gate, though
[Gates](/standards/standard/gates.md#skips) would permit it as a
machine-local input. A runner that exposes a metered credential to the job
is the same defect on a machine nobody watches, and the check costs nothing
where there is none.

## Adopt

- none
