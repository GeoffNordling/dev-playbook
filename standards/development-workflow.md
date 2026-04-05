# Development Workflow Standard

The key words "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in RFC 2119, following the vocabulary
conventions in the [spec-driven-development standard](spec-driven-development.md).

## Purpose

Define the lifecycle of a unit of work — from issue to merged PR — so that any
human or agent can pick up where the last session left off, without relying on
memory or verbal handoff.

This standard governs how work is tracked and handed off. It does not govern how
code is developed. Projects that follow spec-driven development use the
[spec-driven-development standard](spec-driven-development.md) and its
associated skills for that.

## Mental Model

Every artifact answers one question. Together they give full context with no
prior knowledge required.

| Question | Where to look |
|----------|---------------|
| What's the goal? | GitHub Issue |
| What are we building? | `specs/functional_requirements.md` (SDD projects) |
| How is it structured? | `specs/design.md` or `docs/adr/` (SDD projects) |
| What's been done? | `git log main..HEAD` |
| What's the current approach and what remains? | Draft PR description |
| Why did we change course? | Issue comments (sparse) |
| What's the specific diff? | PR diff |

## Issue

All non-trivial work SHALL start as a GitHub Issue. The issue describes the
goal — what needs to happen and why. It is the authoritative statement of intent
for a piece of work.

Trivial changes (typo fixes, single-line corrections) MAY skip issue creation.

## Branch and Draft PR

When work begins on an issue, a branch SHALL be created and a draft PR SHALL be
opened in the first session, before significant code is written.

The draft PR SHALL link to the issue it addresses. The purpose of the early
draft PR is not to signal "ready for review." It is to create a living artifact
that tracks progress. In SDD projects, spec updates are typically the first
commits on the branch.

## PR Description

The PR description is the primary progress-tracking artifact. It SHALL be
updated incrementally as work progresses — it is not written once at the end.

The PR description SHOULD contain:

- A summary of the approach being taken
- What has been completed so far
- What remains to be done
- Any blockers or open questions

In SDD projects, the spec carries the detailed requirements. The PR description
SHOULD focus on progress, approach, and decisions rather than restating what the
spec already covers.

When meaningful progress is made in a session, the PR description SHALL be
updated before the session ends.

## Session Handoff

This is the core mechanism that makes multi-session work reliable. Context SHALL
be reconstructed from durable artifacts, not from memory or conversation
history.

When a new session begins on in-progress work, the reconstruction sequence is:

1. **Read the issue** — what's the goal?
2. **Read the specs** (SDD projects) — what are the requirements and design?
3. **Read `git log main..HEAD`** — what's been done?
4. **Read the PR description** — what's the current approach, what remains?

This sequence gives a human or agent full context without any prior knowledge of
the work. Every other artifact in this workflow exists, in part, to make this
sequence work: the issue states the goal, the specs capture decisions, the
commits record progress, and the PR description synthesizes the current state.

The quality of a session handoff is the quality of these artifacts. If
reconstructing context from them is difficult, the artifacts are incomplete —
not the process.

## Issue Comments

Issue comments SHOULD be used sparingly — only for significant events:

- A change in approach ("tried X, hit Y, switching to Z")
- A blocker that pauses work
- A decision that affects scope

Issue comments SHALL NOT be used for routine progress updates. The PR
description and commit history carry that information.
