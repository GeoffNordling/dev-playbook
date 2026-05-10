# Workflow

How an idea becomes a merged PR in a workspace repo. One path; the same skills and conventions apply to every repo.

## Issues are the unit of delivery

Every actionable change flows through GitHub issues. Issues say what work delivers a change; the spec (when SDD applies) says what must be true. They are distinct.

- [SDD specs](~/workspace/spec-tools/sdd-standards/spec-standard.md) — formal requirements with traceability.
- `CONTEXT.md` — domain glossary.
- `ROADMAP.md` — strategic goals.
- `BUSINESS_CONTEXT.md` — business problem and stakeholders.

Use the `gh` CLI for all issue operations; `gh` infers the repo from `git remote -v` automatically when run inside a clone.

## Label scheme

Three orthogonal label tracks plus a closing label:

| Track | Values | Meaning |
|---|---|---|
| Category | `bug`, `enhancement` | What kind of work it is |
| Mode | `sdd` (presence) | Whether SDD ceremony applies |
| Phase | `phase/requirements`, `phase/design`, `phase/build`, `phase/review` | Where in the journey |

Closing: `wontfix` (apply, then `gh issue close`).

The `phase/*` track is the visible state of the issue. An agent or human opening the issue sees the current phase without exploring the codebase.

## Bootstrapping labels

Run [bootstrap-labels](~/workspace/dev-playbook/tools/bin/bootstrap-labels) once per repo. It is closed-world and idempotent — canonical labels are created or corrected, anything else is deleted. `/intake` invokes it on every run, so labels are reconciled automatically the first time the workflow is used in a new repo.

```bash
python3 ~/workspace/dev-playbook/tools/bin/bootstrap-labels
```

## The flow

```
        IDEA
          │
          ▼
       /intake  ── if fuzzy → /grill-with-docs
          │
          ▼
   issue(s) born ready, labeled:
      bug | enhancement
      sdd? (presence)
      phase/requirements  (sdd) or phase/build (non-sdd)
          │
   ┌──────┴──────┐
   ▼             ▼
 [sdd]        [non-sdd]
   │             │
   ▼             ▼
 /sdd <N>    plain chat:
 dispatcher  "work on issue N, no sdd"
   │             │
   │   reads phase/* label,
   │   runs the matching skill,
   │   bumps the label on success
   │             │
   ├─ phase/requirements → sdd-requirements ─▶ phase/design
   ├─ phase/design → sdd-design ─▶ phase/build
   └─ phase/build  → sdd-tdd    ─▶ opens PR (phase/review)
                                     │
   ┌─────────────────────────────────┘
   ▼
   PR open: body "Closes #N"
   label: phase/review
   │
   ▼
   human review + merge
   │
   ▼
   issue auto-closes
   worktree-sweep
```

## Issue body format (the brief is the body)

The issue body IS the agent brief. Use this format:

```markdown
**Summary:** one-line description

**Current behavior:**
What happens now (or status quo for an enhancement).

**Desired behavior:**
What should happen after the work is complete. Be specific about edge cases and error conditions.

**Key interfaces:**
- `TypeName` — what changes and why
- `functionName()` — what it returns vs what it should return
- Config shape — any new options needed

**Acceptance criteria:**
- [ ] Specific, testable criterion 1
- [ ] Specific, testable criterion 2

**Out of scope:**
- Things that should NOT be changed
- Adjacent features that are separate

**Blocked by:** #N (or "None")
```

Brief principles, applied when writing or revising:

- **Durability over precision.** The issue may sit for days or weeks. Describe interfaces, types, and behavioural contracts. Do not reference file paths or line numbers — they go stale.
- **Behavioural, not procedural.** Describe what the system should do, not how to implement it. The agent will explore and decide.
- **Testable acceptance criteria.** Each criterion is independently verifiable.
- **Explicit out-of-scope.** Prevents gold-plating.

## Vertical-slice rules (when one idea becomes many issues)

Break a plan into **tracer bullet** issues. Each issue is a thin vertical slice cutting through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests).
- A completed slice is demoable or verifiable on its own.
- Prefer many thin slices over few thick ones.

Publish issues in dependency order so the `Blocked by` field can reference real issue numbers.

## /sdd dispatcher

`/sdd <issue>` reads the issue's `phase/*` label and invokes the matching phase skill. Each phase skill ends by bumping the label to the next phase.

| Label | Skill |
|---|---|
| `phase/requirements` | `sdd-requirements` |
| `phase/design` | `sdd-design` |
| `phase/build` | `sdd-tdd` |

The dispatcher refuses if the `sdd` label is absent; non-SDD work happens in plain chat ("work on issue N, no sdd").

## Branch and worktree

Branch name: `<issue#>-<slug>`. The slug is kebab-case from the issue title; drop tracker prefixes; keep it short.

The worktree lives at `.claude/worktrees/<issue#>-<slug>/`. The worktree directory and the branch share the same name.

The dispatcher resolves the worktree by glob `.claude/worktrees/<N>-*`:

- Exactly one match → enter (`cd`).
- Zero matches → create (`git worktree add .claude/worktrees/<N>-<slug> -b <N>-<slug>`).
- Multiple matches → error and ask the user.

Before creating, confirm local `main` matches `origin/main`:

```bash
git rev-parse main
gh api repos/{owner}/{repo}/branches/main --jq .commit.sha
```

If the SHAs differ, ask the user to `git pull` (the agent does not hold the SSH credential).

## In flight

- Commit on the branch with /commit.
- Push with `git push -u origin <name>` (user-driven; YubiKey tap required).
- Open the PR with `gh pr create --body "Closes #<N> …"`. The `Closes #<N>` token is mandatory — merging the PR closes the issue.
- The phase label flips to `phase/review` when the PR opens.

Sessions resume by `cd .claude/worktrees/<name>`; the worktree persists across sessions, agents, and terminals.

## Cleanup

After merge, run [worktree-sweep](~/workspace/dev-playbook/tools/bin/worktree-sweep) from inside the repo:

```bash
python3 ~/workspace/dev-playbook/tools/bin/worktree-sweep
```

It prunes worktrees whose PR is merged with no local divergence; ambiguous cases (rejected PRs, unpushed commits, missing PRs) are reported for case-by-case handling.

## Bootstrapping spec-tools

The SDD skills currently fall back to manual spec validation — `spec-tools` programmatic views are not yet available. Until they are, agents check by hand: `@pytest.mark.covers(...)` IDs exist in the spec, stub signatures match `Interface:` lines verbatim, every `Needs: utest` / `Needs: itest` is satisfied by at least one marker-bearing test.

## Open questions

- Where `/improve-codebase-architecture` fits in the SDD workflow beyond `sdd-design`'s explicit escape hatch is left to discover with use. Refactor pressure inside `sdd-tdd` that crosses a committed `Interface:` routes through spec amendment back to `sdd-design`, not direct architecture work.
