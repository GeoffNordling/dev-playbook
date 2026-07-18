# Landing — the close-out procedure

Read this only when the batch has cleared the landing checkpoint and the human
has given the batched nod. Everything below writes to GitHub.

**Before authoring the first brief**, read
`~/workspace/dev-playbook/standards/tracking/issues.md` end-to-end — brief
format, vertical-slice rules, native relationships — and report
`READ: issues.md`.

On the nod, per issue:

- **Four-tuple** — hardcoded for this skill; no scheme lookup needed. Every
  landed issue gets exactly:
  - `category:maintenance` (maintains shipped state: fix, hygiene, polish) or
    `category:extension` (adds a capability the system lacks) — judge per
    issue.
  - `mode:*` — the question is: **are specs involved?** `mode:sdd` only when
    the repo uses spec-tools (a `specs/` directory at the repo root) **and**
    the issue's implementation involves those specs — then `tests:yes` +
    `phase:sdd-specs`. Otherwise `mode:direct`. (Same shape as the tests
    question below: build-vs-tdd asks "are tests involved?"; this asks "are
    specs involved?")
  - For `mode:direct`, the question is: **are tests involved?** `tests:yes` +
    `phase:tdd` if the work writes or modifies tests; `tests:no` +
    `phase:build` otherwise.
- **Body** — the brief, per issue conventions (read above): authored
  complete, no changelog, structured for an implementer who has only the
  issue and the repo. Fold in what investigation proved; cite tested claims
  plainly.
- **Edges** — native blocked-by relationships only where sequencing is real
  (single top-level `gh api` calls, one per edge):

  ```bash
  gh api repos/{owner}/{repo}/issues/<blocker#> --jq .id > /tmp/claude-1000/blocker_id
  blocker_id=$(cat /tmp/claude-1000/blocker_id)
  gh api --method POST repos/{owner}/{repo}/issues/<dependent#>/dependencies/blocked_by -F issue_id="$blocker_id"
  ```

- **Consolidations / closes** — absorbed or dissolved issues get a closing
  comment naming what happened and where the work went, then close.
- Update each ledger entry to `landed`, commit, and report one line per
  issue: `<repo>#<n> · <verdict> · landed at <node>` (or `closed` /
  `merged into #X`).

Then stop. Launch nothing further; the factory takes it from here.
