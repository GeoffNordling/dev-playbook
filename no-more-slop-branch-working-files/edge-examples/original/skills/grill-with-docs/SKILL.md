---
name: grill-with-docs
description: Front door onto a /grilling session run with the /domain-modeling skill. Use when the user wants to stress-test a plan against their project's language and documented decisions, or when intake, design, or ralph-setup reaches its interview beat.
disable-model-invocation: false
model: inherit
effort: xhigh
---

# Grill with Docs

Run a /grilling session, using the /domain-modeling skill throughout. Everything else applies as written.

Where /domain-modeling says `docs/adr/` and "ADR", this workspace writes **Decision Records** to `docs/decisions/`, in the form given by [Decision Record conventions](~/workspace/dev-playbook/standards/decisions/records.md). Its `CONTEXT.md` format applies as written.
