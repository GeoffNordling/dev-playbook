# ADR-001: Adopt OpenFastTrace for Spec Traceability

**Date:** 2026-04-09
**Status:** Accepted
**Issue:** [#9](https://github.com/GeoffNordling/dev-playbook/issues/9)

## Context

This workspace uses spec-driven development (SDD). Specs live in `/specs/` in each project repo, written in markdown using EARS sentence templates and RFC 2119 modal verbs.

The existing `sdd-trace` CLI tool performed two categories of checks:

1. **Structural linting** — well-formed requirement IDs, backtick-wrapped obligation keywords, no mixed obligation levels
2. **Traceability** — every requirement in `functional_requirements.md` appears in `design.md`, and every requirement referenced in tests maps back to a defined requirement

`sdd-trace` used a custom `REQ-AREA-NNN` ID format and custom tracing logic. As the workspace grew to multiple projects with larger spec files, several limitations became apparent:

- The flat ID scheme had no notion of artifact types, coverage chains, or revision tracking
- Traceability logic was hand-written and incomplete compared to established tools
- The CLI was a standalone tool that agents had to remember to call — it was not part of the test suite

Before building a replacement, we conducted competitive research to determine whether an established standard existed for markdown-native requirement tracing.

## Decision

We adopt **OpenFastTrace (OFT)** as the foundation of our spec system, replacing the custom `sdd-trace` tool and `REQ-AREA-NNN` ID format.

OFT is an open-source requirement tracing suite with over 8 years of active development (v4.2.2 at time of adoption). It defines a spec format called Requirement-Enhanced Markdown — a superset of standard Markdown that any renderer can display, but OFT-aware tools can parse for structured tracing.

We adopt:

- **OFT's `type~name~revision` ID format** — replaces `REQ-AREA-NNN`. Artifact types (`req`, `dsn`, `utest`, etc.) make the coverage chain explicit. Revision numbers force downstream documents to acknowledge upstream changes.
- **OFT's `Needs:`/`Covers:` link model** — each spec item declares what downstream artifact types must cover it, and each downstream item declares what it covers upstream. OFT walks this directed graph and fails if any link is missing.
- **OFT's JAR for traceability checks** — we delegate tracing to OFT via subprocess rather than reimplementing its graph-walk logic in Python. OFT represents 8 years of tracing logic; there is no value in reimplementing it.

We wrap OFT in a **pytest plugin (`pytest-sdd`)** so spec checks run as part of every project's normal test suite, not as something an agent has to remember to invoke.

### Bridging pytest markers to OFT

OFT's tracing model is self-contained within markdown files. When a spec item declares `Needs: utest`, OFT expects to find a `utest~` spec item with a `Covers:` link back to it — in markdown. But our projects express test coverage through `@pytest.mark.req` and `@pytest.mark.dsn` markers on Python test functions, which OFT cannot see.

Rather than maintain hand-written `utest` spec items that duplicate what the markers already express, `pytest-sdd` bridges this gap automatically. At trace time, it scans collected pytest items for markers matching OFT artifact types, generates a temporary markdown file with `utest~` items containing the appropriate `Covers:` links, passes it to OFT alongside the real spec directories, and deletes it after OFT returns.

This keeps OFT as the single source of truth for trace logic while letting projects express test coverage naturally through pytest markers.

## Alternatives Considered

The following tools were evaluated and rejected because they are not markdown-native:

| Tool | Format | Why rejected |
|------|--------|-------------|
| Doorstop | YAML (one file per requirement) | Not markdown-native |
| StrictDoc | `.sdoc` format | Not markdown-native |
| Sphinx-Needs | RST directives | Not markdown-native |
| Cucumber/Gherkin | BDD test format | Not requirements management |
| TLA+/Alloy | Formal methods | System design verification, not spec document structure |
| pytreqt | Markdown | Pre-alpha, abandoned, no structural linting or cross-document tracing |

**Reimplementing tracing in pure Python** was considered but rejected. OFT's tracing logic is mature and covers edge cases (orphaned items, revision mismatches, forwarding) that would take significant effort to replicate correctly. The JAR dependency (Java on PATH) is an acceptable trade-off for correctness. If distribution requirements change in the future, a pure-Python reimplementation can be written using OFT's behavior as the reference spec.

## Consequences

- All spec files across the workspace use OFT's `type~name~revision` ID format
- Java must be installed on developer machines for traceability checks (lint checks are pure Python and have no Java dependency)
- The OFT JAR (v4.2.2) is vendored once in `dev-playbook/tools/lib/` (gitignored) and referenced by all projects via relative path
- `sdd-trace` is removed; `pytest-sdd` replaces it
- Spec checks run automatically as part of `pytest` — no separate invocation needed
- The `<!-- oft:off -->` / `<!-- oft:on -->` markers can exclude sections from both OFT and pytest-sdd parsing
