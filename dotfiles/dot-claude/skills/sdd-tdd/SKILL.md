---
name: sdd-tdd
description: Implements an SDD issue via vertical-slice TDD against the committed `Interface:` declarations, removes the work-in-progress markers as verifiers land, then advances the issue to code review. Use when the agents dashboard launches the build phase.
disable-model-invocation: false
model: opus
effort: xhigh
disallowed-tools: AskUserQuestion
argument-hint: "<issue-number>"
---

# SDD TDD

Implement an SDD issue with vertical-slice TDD against its committed specs — every `feat`, `req`, and `dsn`, down to the `Interface:` lines the design pins — remove the `WIP:` markers as each region's verifiers land, then hand the issue off to code review. Implementation proceeds in **chunks** — each runs an inner red/green/refactor loop per slice and closes with a whole-chunk refactor pass.

Work without waiting for approval: plan, implement, refactor, and commit on your own, pausing only to escalate on the §5 triggers. The user reviews the finished work separately, not mid-build.

## Read first

Before doing anything else, read end-to-end:

- [spec standard](~/workspace/spec-tools/sdd-standards/spec-standard.md) — keyword reference, coverage chain, ID format, the `WIP:` marker.
- [testing conventions](~/workspace/dev-playbook/standards/testing/conventions.md) — pytest structure, naming, fixtures, behavioral focus.

Then report: `READ: spec-standard.md, testing-conventions.md`. Proceed only after.

When modifying the spec comes into play (§6), also read [lessons](~/workspace/spec-tools/sdd-standards/lessons.md) at that point.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number.

**Be in the issue's worktree.** The session is normally already there (cwd `.claude/worktrees/issue-<issue>`, carried across `/clear`); if not, re-enter it with `EnterWorktree(path=.claude/worktrees/issue-<issue>)`. If the worktree is gone, escalate (§5) — don't start a fresh tree.

- `gh issue view <issue> --comments` — the body is the contract; comments may carry context the body doesn't.
- **Rework re-entry.** Check for an existing PR (`gh pr view`). If one exists, code review already ran — read **every** comment surface on the PR: its body, top-level conversation comments, review summary bodies, and inline/line-level diff comments alike, from both user and agent reviewers. (`gh pr view --comments` shows the body and conversation but omits the inline diff comments, which live at `gh api repos/{owner}/{repo}/pulls/<pr>/comments`; review summaries are at `.../pulls/<pr>/reviews` — these endpoints are a non-binding hint.) Build the rework work list from that complete feedback. If `gh pr view` finds none, this is first implementation; work from the spec alone. The committed spec is authoritative — a finding that conflicts with it yields to it; one that requires changing it routes through §6.
- The specs under `specs/functional_requirements/` and `specs/design/`.
- Existing tests under `tests/` and code under `src/` — there may be partial work or stubs from a prior cycle.
- Run the test suite to see the current state: `make test`. Run all `make` commands from the Python sub-project the issue lives in (`make -C <subproject> …`); when the `Makefile` is at the repo root, run them there.
- **Inherited stale references.** Consult the project's reported **stale references** (`SpecGraph.stale_references()`) and any `WIP:`-marked bumped nodes for markers a prior cycle's revision bump left naming a superseded revision — reported, not raised, and distinct from a **dangling reference**, whose `(type, name)` is absent entirely and still raises. Reconcile each per §2 before building new slices on the bumped item.

## 2. Plan the chunk

A **chunk** is a coherent piece of implementation work — typically the slices covering one `dsn`, or a small cluster of tightly related `dsn`s. Implementation proceeds one chunk at a time.

Before each chunk, state your plan — to anchor the work and keep it visible to the watching user:

- **Scope.** Which `dsn`(s) and behaviors the chunk covers.
- **Slice ordering.** The sequence of red/green/refactor slices you'll drive.
- **Ambiguities.** Anything in the spec you expect to resolve; if one stalls the next slice, escalate per §5.
- **Stale-reference reconciliation.** For each inherited stale reference (§1), re-evaluate the marked test against the bumped item's new meaning: rework the test where the new meaning demands it, then re-point its `@pytest.mark.covers` marker to the current revision — the covers-string only; the test's logic changes only through that rework. The bumped node is then covered again, so the existing §7 `WIP:` removal closes it. (A rework that would change a committed `Interface:`, or a bumped meaning the spec underdetermines, is a spec change — route it through §6.)

The plan is your map, not a gate — proceed without waiting for approval.

## 3. The chunk loop (outer)

For each chunk:

1. Run the inner slice loop until every behavior in the chunk's scope is covered with passing tests.
2. **Whole-chunk refactor pass.** With the suite green, review every module the chunk touched for refactor candidates not visible inside a single slice — cross-module duplication, deeper-module opportunities now that several call sites exist, abstraction misalignments, primitive obsession. Run `make test` after each step. A refactor that would change a committed `Interface:`, or surface a structural problem beyond one module's seam, is an escalation — see §5.
3. Run the gate — `make check`. Resolve failures.
4. Commit the chunk with /commit.
5. Move to the next chunk, or to §7 once the issue's scope is fully implemented.

## 4. The slice loop (inner)

Each slice is one test, one implementation, then a brief refactor.

**Red.** Pick one observable behavior under one `req~…` or `dsn~…`. Write a single failing test exercising it through the public surface declared by the relevant `dsn`'s `Interface:`. Mark every test with `@pytest.mark.covers("<id>")` naming the closest upstream item — typically the `dsn` whose `Needs: utest` / `Needs: itest` declared the obligation. Run `make test`; confirm it fails for the expected reason.

**Never modify a written test.** Once you've written a test, make it pass by changing code, not the test. If you feel the need to change the test, escalate (§5) — don't edit it yourself.

**Exception — inherited stale markers.** Re-pointing or reworking a *stale* marker inherited from a prior cycle's revision bump (§1, §2) is reconciliation, not editing a fresh slice's test: re-point its covers-string to the current revision, and rework the test only where the bumped meaning demands it (route to §6 if that rework would change a committed `Interface:` or the new meaning is underdetermined). This exception covers inherited stale markers alone — a test you wrote in this build's slices is still never modified; escalate (§5) instead.

**Stub on first contact.** When a test imports a symbol with no stub yet, create the stub matching its `Interface:` declaration verbatim — same parameter names, kinds, annotations, return annotation. Body is `raise NotImplementedError` for functions and methods, `pass` for `__init__`. Don't pre-stub symbols not yet under test.

**Green.** Write the minimal implementation that makes the failing test pass. Don't add code for behaviors not yet tested. Run `make test`; confirm green.

**Refactor.** With the suite green, look for refactor candidates inside the module: extract duplication, deepen modules, simplify primitives. Run `make test` after each step. A refactor that would change a committed `Interface:` is an escalation — see §5.

Refactor candidate catalogue:

- **Duplication** → Extract function/class
- **Long methods** → Break into private helpers (keep tests on the public interface)
- **Shallow modules** → Combine or deepen
- **Feature envy** → Move logic to where data lives
- **Primitive obsession** → Introduce value objects
- **Existing code** the new code reveals as problematic

For test-quality patterns and mocking guidance, see [testing conventions](~/workspace/dev-playbook/standards/testing/conventions.md).

## 5. Escalations

You work without approval, but when something falls outside the plan — anything unexpected, or any wish to deviate — surface it and stop, emitting a terminal `ESCALATE:` line:

```
ESCALATE: <repo>#<issue> · current phase: sdd-tdd · <where you're stuck and the call you need>
```

The user reads it, decides, and relaunches; you don't push past the obstacle on your own. In particular:

- **Stuck test.** A slice's test won't pass after two implementation attempts.
- **A written test looks wrong.** You want to change a test you already wrote — surface why; the user decides whether you mis-encoded it or the spec needs to change.
- **The issue is too big for one session.** You can see the whole spec won't be implemented in this build before context runs low — a sizing miss. Surface it so the user re-splits it into smaller issues at intake; don't truncate the work silently.
- **The spec needs to change.** A committed `Interface:` no longer fits — refactor pressure or a bug fix would change it, or a structural problem won't sit behind one module's seam — or the spec underdetermines the next slice's behavior, so you can't write the assertion.
- **The spec could be better.** You see a spec change that would improve the design, even though nothing is stopping you.

The last two put a spec change on the table — handle it per §6.

## 6. Modifying the spec

The implementation never edits the spec on its own. With a change on the table, describe which item is affected, the proposed change, and what motivated it. The user decides to:

- **Apply here** — edit the spec (update `Interface:` lines; on revision follow the spec standard's [revision rules](~/workspace/spec-tools/sdd-standards/spec-standard.md)). Then continue stub → test → implementation. During initial greenfield implementation no pinned consumers exist — edit in place at revision `0`, don't bump.
- **Defer to a fresh `sdd-specs` pass** — don't edit the spec; the issue routes back to the spec phase.
- **Reject** and direct another approach.

Never edit the spec without an explicit approval gesture in the same turn. A bug found during implementation is a spec gap: surface it, propose the change that closes it, and wait for the routing call before touching code.

## 7. Close the phase

With the whole issue implemented:

1. **Remove the work-in-progress markers.** Delete the `WIP: true` line from every node that carries one. Each marked cone is now covered by verifiers. If a cone you couldn't complete would force you to leave one marked, that's an escalation (§5), not a close.
2. **Leave the tree green.** Run the gate — `make check`; with every `WIP:` removed, its `spec-tools validate .` step now enforces completeness over the whole spec graph: a red build means a missing verifier — add it and re-run. Don't commit a red tree.
3. **Commit** the remaining changes (marker removals included) with /commit.
4. **Advance to code review:**
   ```bash
   gh issue edit <issue> --remove-label "phase:sdd-tdd" --add-label "phase:sdd-code-pr-review"
   ```
5. Emit the terminal line, then stop:
   ```
   DONE: <repo>#<issue> · current phase: sdd-tdd · next phase: sdd-code-pr-review · commit <sha> · check green · unpushed
   ```
