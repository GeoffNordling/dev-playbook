---
type: Workstream
title: BAML Workstream
description: The head file of the BAML child workstream — a minimal, inactive line of thought on whether BAML, BoundaryML's language for typed LLM calls, is a wheel this system reinvents; its two versions, where they overlap the system and where they do not, and the question still to think through
---

# BAML Workstream

The child workstream that keeps one question in view: is this system
reinventing BAML? This workstream is speculative. It does not advance
actively; it holds an evaluation and a question to keep thinking about.

## Goal

Know whether [BAML](https://boundaryml.com/) solves what the System
workstream sets out to build, so that the system imports it where it
fits and builds its own only where it does not.

## Terms

- **v0** — BAML's stable language, now called legacy. `.baml` files
  declare types and functions whose body is a prompt template; a
  generator writes a client for the host language, which in Python
  returns Pydantic models. It calls models over web APIs with a
  credential.
- **v1** — BAML's new language, in public beta: a full programming
  language with LLM functions, a standard library, and an agent runner
  built in. Its standard library includes `ClaudeCodeClient`, which
  runs the `claude` command as a subprocess.
- **schema-aligned parsing** — BAML's parser, which repairs a model's
  almost-valid output into the declared return type instead of
  rejecting it. It is what BAML adds over Pydantic.

## Settled

Evaluated 2026-09-26 against BAML commit `e215c3de`, v0 0.226.2 and v1
0.20.1.

- **Not adopted.** The overlap is one leaf of the system, and there
  `claude -p --json-schema` with a Pydantic class gives the same typed
  output with no second toolchain. v1 is also pre-1.0.
- **Billing.** v0 cannot bill to the subscription. v1 can, through
  `ClaudeCodeClient`, only when the environment holds no credential.
- **The disconnect.** BAML types one model call, from outside the
  model. This system types the markdown documents that instruct agent
  sessions running inside Claude Code. BAML moves prompts into code;
  this system keeps markdown and embeds deterministic structure in it.
- **The overlap.** A stochastic judge that returns typed findings is
  exactly a BAML function. So is an agent that stands in for an
  extractor not yet coded and returns typed rows.
- **No overlap.** The doc-types, the fact base and its deterministic
  extractors, the ontology and its solver, Standards and gates, loops
  and stints, and the viewer.
- **Ideas worth borrowing.** Quorum runs, where a stochastic rule
  passes when m of n judge runs pass; an assert that fails a value
  apart from a check that records a pass or fail; and rendering,
  sending, and parsing as three separate steps, so the two
  deterministic ones test without a model.

## Planned

- **Test the disconnect.** The claim that the two go in opposite
  directions may be wrong. The user's ultimate goal could perhaps be
  rethought to fit inside BAML, in which case this system reinvents
  the wheel from the outside in, where BAML builds it from the inside
  out.
