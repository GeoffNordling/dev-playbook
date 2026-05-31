---
name: sdd-tdd
description: Implements an SDD issue via vertical-slice TDD against the committed `Interface:` declarations, removes the work-in-progress markers as verifiers land, then opens the PR and advances the issue to code review. Use when the agents dashboard launches the build phase.
disable-model-invocation: false
model: opus
effort: xhigh
allowed-tools: Bash(gh issue *) Bash(gh pr *) Bash(git *) Edit Write Skill(commit)
argument-hint: "<issue-number> [scope]"
---

# SDD TDD

Implement an SDD issue with vertical-slice TDD against its committed specs — every `feat`, `req`, and `dsn`, down to the `Interface:` lines the design pins — remove the `WIP:` markers as each region's verifiers land, then open the PR and hand the issue off to code review. Implementation proceeds in **chunks** — each runs an inner red/green/refactor loop per slice and closes with a whole-chunk refactor pass.

Work without waiting for approval: plan, implement, refactor, and commit on your own, pausing only to escalate on the §5 triggers. The human reviews the finished work separately, not mid-build.

## Read first

Before doing anything else, read end-to-end:

- [spec standard](~/workspace/spec-tools/sdd-standards/spec-standard.md) — keyword reference, coverage chain, ID format, the `WIP:` marker (§2.10).
- [testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md) — pytest structure, naming, fixtures, behavioral focus.
- [python conventions](~/workspace/dev-playbook/standards/python-conventions.md) — docstring rules, fail-loudly, annotation style.

Then report: `READ: spec-standard.md, testing-conventions.md, python-conventions.md`. Proceed only after.

When modifying the spec comes into play (§6), also read [lessons](~/workspace/spec-tools/sdd-standards/lessons.md) at that point.

## 1. Load context

`$ARGUMENTS` is the issue number, optionally followed by a scope restriction; below, `<issue>` is that number. Work happens on the issue's branch.

- `gh issue view <issue>` — the body is the contract.
- The specs under `specs/functional_requirements/` and `specs/design/`.
- Existing code under `src/` and tests under `tests/` — there may be partial work or stubs from a prior cycle.
- Run the test suite to see the current state.

**Scope.** With no restriction, implement the whole issue. With one (specific `dsn`s or `req`s), implement exactly that — no more, no less: the human has split a large issue across sessions and handed you one slice. You never decide scope; that decision was made before you were launched, and you neither widen nor narrow it.

## 2. Plan the chunk

A **chunk** is a coherent piece of implementation work — typically the slices covering one `dsn`, or a small cluster of tightly related `dsn`s. Implementation proceeds one chunk at a time.

Before each chunk, state your plan — to anchor the work and keep it visible to the watching human:

- **Scope.** Which `dsn`(s) and behaviors the chunk covers.
- **Slice ordering.** The sequence of red/green/refactor slices you'll drive.
- **Ambiguities.** Anything in the spec you expect to resolve; if one blocks the next slice, escalate per §5.

The plan is your map, not a gate — proceed without waiting for approval.

## 3. The chunk loop (outer)

For each chunk:

1. Run the inner slice loop until every behavior in the chunk's scope is covered with passing tests.
2. **Whole-chunk refactor pass.** With the suite green, review every module the chunk touched for refactor candidates not visible inside a single slice — cross-module duplication, deeper-module opportunities now that several call sites exist, abstraction misalignments, primitive obsession. Run the suite after each step. A refactor that would change a committed `Interface:`, or surface a structural problem beyond one module's seam, is an escalation — see §5.
3. Run lint, format, and typecheck (per `CLAUDE.md` / `Makefile`). Resolve failures.
4. Commit the chunk with /commit.
5. Move to the next chunk, or to §7 once the issue's scope is fully implemented.

## 4. The slice loop (inner)

Each slice is one test, one implementation, then a brief refactor.

**Red.** Pick one observable behavior under one `req~…` or `dsn~…`. Write a single failing test exercising it through the public surface declared by the relevant `dsn`'s `Interface:`. Mark every test with `@pytest.mark.covers("<id>")` naming the closest upstream item — typically the `dsn` whose `Needs: utest` / `Needs: itest` declared the obligation. Run the suite; confirm it fails for the expected reason.

**Never modify a written test.** Once you've written a test, make it pass by changing code, not the test. If you feel the need to change the test, escalate (§5) — don't edit it yourself.

**Stub on first contact.** When a test imports a symbol with no stub yet, create the stub matching its `Interface:` declaration verbatim — same parameter names, kinds, annotations, return annotation. Body is `raise NotImplementedError` for functions and methods, `pass` for `__init__`. Don't pre-stub symbols not yet under test.

**Green.** Write the minimal implementation that makes the failing test pass. Don't add code for behaviors not yet tested. Run the suite; confirm green.

**Refactor.** With the suite green, look for refactor candidates inside the module: extract duplication, deepen modules, simplify primitives. Run the suite after each step. A refactor that would change a committed `Interface:` is an escalation — see §5.

Refactor candidate catalogue:

- **Duplication** → Extract function/class
- **Long methods** → Break into private helpers (keep tests on the public interface)
- **Shallow modules** → Combine or deepen
- **Feature envy** → Move logic to where data lives
- **Primitive obsession** → Introduce value objects
- **Existing code** the new code reveals as problematic

For test-quality patterns and mocking guidance, see [testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md).

## 5. Escalations

You work without approval, but stop, surface the situation, and wait for the human's call whenever something falls outside the plan — anything unexpected, or any wish to deviate. In particular:

- **Stuck test.** A slice's test won't pass after two implementation attempts.
- **A written test looks wrong.** You want to change a test you already wrote — surface why; the human decides whether you mis-encoded it or the spec needs to change.
- **The spec needs to change.** A committed `Interface:` no longer fits — refactor pressure or a bug fix would change it, or a structural problem won't sit behind one module's seam — or the spec underdetermines the next slice's behavior, so you can't write the assertion.
- **The spec could be better.** You see a spec change that would improve the design, even though nothing is blocking you.

The last two put a spec change on the table — handle it per §6.

## 6. Modifying the spec

The implementation never edits the spec on its own. With a change on the table, describe which item is affected, the proposed change, and what motivated it. The human decides to:

- **Apply here** — edit the spec (update `Interface:` lines; on revision follow [spec-standard §2.2.3](~/workspace/spec-tools/sdd-standards/spec-standard.md#223-revision)). Then continue stub → test → implementation. During initial greenfield implementation no pinned consumers exist — edit in place at revision `0`, don't bump.
- **Defer to a fresh `sdd-design` pass** — don't edit the spec; the issue routes back to design.
- **Reject** and direct another approach.

Never edit the spec without an explicit approval gesture in the same turn. A bug found during implementation is a spec gap: surface it, propose the change that closes it, and wait for the routing call before touching code.

## 7. Close the phase

When your scope is fully implemented:

1. **Remove the work-in-progress markers.** Delete the `WIP: true` line from each `feat` whose cone is now fully covered by verifiers (spec-standard §2.10). Leave it on any `feat` whose cone is still unbuilt — including work outside your scope.
2. **Leave the tree green.** Run the full test suite, lint, format, and typecheck (per `CLAUDE.md` / `Makefile`), including the spec-graph gate. Feats still carrying `WIP:` stay exempt from completeness; the gate enforces it only over the cones you just un-marked, so a failure there means a missing verifier — fix it and re-run. Don't commit a red tree.
3. **Commit** the remaining changes (marker removals included) with /commit.

Now read the `WIP:` markers to tell whether the whole issue is done.

**Issue complete** — no `feat` carries `WIP:`:

1. **Push, then open the PR.** `git push` needs the human's YubiKey — hand them `git push -u origin <branch>` and wait for it to land. Then open the long-lived PR: `gh pr create --body "Closes #<issue> …"`. The `Closes #<issue>` token is mandatory — merging the PR closes the issue.
2. **Advance to code review:**
   ```bash
   gh issue edit <issue> --remove-label "phase:sdd-tdd" --add-label "phase:sdd-agent-code-review"
   ```
3. Emit the terminal line, then stop:
   ```
   DONE: implemented #<issue>, PR open, issue at phase:sdd-agent-code-review
   ```
   Do not begin the review — the human launches /sdd-agent-code-review separately.

**Issue incomplete** — some `feat` still carries `WIP:`: your scope was one slice of a larger issue and more remains. Do not push, open a PR, or change the label. Instead:

1. Comment the state on the issue (`gh issue comment <issue>`): what you implemented, which `feat`s remain `WIP:`, decisions made.
2. Emit the terminal line, then stop:
   ```
   STOPPED: built <scope> for #<issue>, issue stays at phase:sdd-tdd, WIP feats remain
   ```
   The human relaunches with the next scope.
