# Landing — the close-out procedure

Read this only when the batch has cleared the landing checkpoint and the user has given
the batched nod. Everything below writes to GitHub.

**Before authoring the first brief**, read
[issue authoring](~/workspace/dev-playbook/standards/tracking/issue-authoring.md) end-to-end —
brief format, vertical-slice rules, native relationships — and report `READ: issue-authoring.md`.

## Blind-implementer certification — the per-issue gate

Implementers read the issue **blind**: only the issue body and the repo, with no access
to this conversation, the ledger, or `tmp/`. Before each GitHub write, certify the brief
is self-contained, and fix it if not:

- **No investigation jargon** — no worker ids, probe/wave/checkpoint numbers, bucket
  names, or ledger vocabulary. Those are private to the run.
- **Every referenced artifact is repo-resident** — a path, file, or command the
  implementer can open. Nothing points into `tmp/`, the ledger, or the chat.
- **Findings are folded in as flat claims**, not citations to private evidence. "The
  `--refuted` flag has no caller" — not "probe P4 refuted the caller hypothesis."
- **Acceptance criteria are runnable blind** — each is a check the implementer can
  perform with only the repo in front of them.
- **Cross-references are GitHub-native** — blocked-by edges and issue links, never "as
  discussed" or "see the map."

## On the nod, per issue

- **Four-tuple** — hardcoded for this skill; no scheme lookup needed. Every landed issue
  gets exactly:
  - `category:maintenance` (maintains shipped state: fix, hygiene, polish) or
    `category:extension` (adds a capability the system lacks) — judge per issue.
  - `mode:*` — the question is **are specs involved?** `mode:sdd` only when the repo uses
    spec-tools (a top-level `specs/` directory) **and** the issue's implementation
    involves those specs — then `tests:yes` + `phase:sdd-specs`. Otherwise `mode:direct`.
  - For `mode:direct`, the question is **are tests involved?** `tests:yes` + `phase:tdd`
    if the work writes or modifies tests; `tests:no` + `phase:build` otherwise. No issue
    lands at `phase:design` — design-shaped questions were resolved with the user during
    grooming and are already encoded in the brief.
- **Body** — the brief, per the issue authoring standard read above: authored complete, no
  changelog, structured for the blind implementer. Fold in what investigation proved;
  state tested claims plainly.
- **Edges** — native blocked-by relationships only where sequencing is real. The
  endpoint takes the blocker's internal `id`, not its number, so resolve that first.
  `gh`/`git` must lead the line and cannot see `$TMPDIR`, so capture to a **literal**
  scratchpad path (substitute your session's scratchpad directory), one top-level call
  per edge:

  ```bash
  gh api repos/{owner}/{repo}/issues/<blocker#> --jq .id > /abs/scratchpad/blocker_id
  blocker_id=$(cat /abs/scratchpad/blocker_id)
  gh api --method POST repos/{owner}/{repo}/issues/<dependent#>/dependencies/blocked_by -F issue_id="$blocker_id"
  ```

  Read the edge back with a GET to confirm it wrote.
- **Consolidations / closes** — absorbed or dissolved issues get a closing comment naming
  what happened and where the work went, then close.
- Update each ledger entry to `landed`, commit, and report one line per issue:
  `<repo>#<n> · <verdict> · landed at <node>` (or `closed` / `merged into #X`).

Then stop. Launch nothing further; the factory takes it from here.
