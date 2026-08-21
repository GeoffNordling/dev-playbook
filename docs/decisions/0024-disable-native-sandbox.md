---
type: Decision-Record
title: Disable the Native Sandbox
description: Turn off Anthropic's native sandbox workspace-wide, temporarily — months of false positives with no real catch to show for them, and fixing it is not a priority right now
date: 2026-08-21
status: accepted
---

# Disable the Native Sandbox

The native sandbox (`sandbox` in `dotfiles/settings/fedora.json`) never once
blocked an agent from doing something unwanted, but tripped false positives
routinely over the past few months — and every trip an agent simply worked
around, since a permission prompt or a workaround was always available. That
cost outweighs the protection, and fixing it is not a priority right now, so
**the sandbox is disabled (`sandbox.enabled: false`) rather than left
half-trusted.** The removal is temporary: #261 tracks redesigning a tighter,
trustworthy surface and reintroducing it.
