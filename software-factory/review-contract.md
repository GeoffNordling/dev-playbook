---
type: Guide
title: Review Contract
description: The contract the three reviews run under — the two severities, the thread model, the cycle header, delta re-review, and the escalation boundary
---

# Review Contract

What a review does once it is launched: the gate it runs before reading
anything, the threads it leaves behind, and the line between a finding and an
escalation. Every clause binds all three reviews — bug, code, and doc alike.
Each review supplies two values and inherits everything else:

- **Review name** — `code review`, for instance. It opens the cycle header and
  it is what the cycle count counts.
- **What counts as Blocking** — one line, and it differs by review.

Which reviews run at a cycle is
[factory-operations.md](/software-factory/factory-operations.md#the-review-stop);
how a pull request's existing feedback is read is
[pr-feedback.md](/software-factory/pr-feedback.md).

What happens to a Suggestion after it is posted is not here. The Adjudicator
dispositions open Suggestion threads at each verdict point, and its rules —
the routing, the reason vocabulary, the deferral stubs — arrive with
[issue #442](https://github.com/GeoffNordling/dev-playbook/issues/442).

## The stance

A review is an **audit only**. It never modifies the work under review, and the
verdict on its findings is not its to take — it posts them and stops. Defects
route back to the authoring node through the script-computed verdict, never
through the reviewer's hand.

The audit runs hands-off: finding problems is its output, not a reason to stop.

## The green gate

The review opens by running the gate — `make -C <subproject> check`, or
`make check` when the `Makefile` is at the repo root. Green: the audit
proceeds. Red: the build node opened a PR over a red tree, which is an
escalation rather than a review of broken work.

The gate is the whole of what the review runs; individual lint tools are never
run on their own. Where there is no `make check` to run, the audit proceeds.

## The two severities

- **Blocking** — the problem disqualifies the pull request from merging as it
  stands. It drives a rework lap, and convergence requires its thread
  resolved.
- **Suggestion** — an improvement the pull request is mergeable without. It
  never drives a lap by itself.

**The citeability rule.** A finding is Blocking only when it names a breach of
one of three sources. Everything else is a Suggestion at most:

1. **A binding section of the issue brief** — `Acceptance criteria`,
   `Desired behavior`, `Out of scope`, `Prohibited surfaces`, and `Artifacts`
   in a brief that carries one
   ([the section binds when present](/standards/tracking/issue-authoring.md#the-artifacts-section);
   the lint never requires the heading). `Key interfaces` is advisory and
   `User intent` guides micro-decisions — neither feeds Blocking.
2. **A named rule of a standard the review was required to read** — each
   review's own read-first table picks those standards. The PR-body presence
   check is an instance of this source: the mandatory sections of
   [the merge-message recipe](/software-factory/factory-operations.md#the-merge-message-recipe)
   are checkable by absence, so a missing one is mechanical.
3. **A concrete failure scenario** — a specific input or state the system can
   actually reach, and the wrong output, crash, or data loss it produces. A
   bug that can be shown failing is Blocking; a plausible but unverified
   concern is a Suggestion.

## Findings are threads

A finding is a resolvable thread on the pull request, never a paragraph in an
essay. One run posts **one GitHub review, verdict `COMMENT`** — the only
verdict a single account may give its own pull request. The review body carries
the cycle header and the clean dimensions, bare; the inline comments are the
findings.

- **The first word is the severity** — `Blocking` or `Suggestion` — and the
  last line is the attribution `— <node> · <session id>`, which is what joins
  the comment to the run that wrote it, since every factory writer shares one
  GitHub account. The session id is in `CLAUDE_CODE_SESSION_ID`
  (`printenv CLAUDE_CODE_SESSION_ID`).
- **Every finding is a problem plus its fix.** Nothing unactionable is written
  — no "acceptable as written", "no action needed", "just noting", and no
  explaining why a clean thing is clean. Genuine uncertainty is still
  surfaced, as a question or risk naming the decision the user faces.
- **A finding with no diff line to anchor to** rides a file-level comment on
  the nearest file in the diff, its first line naming the real subject. That
  fallback is the last resort and the only one: a finding written into the
  review body opens no thread, so the verdict would be blind to it.
- **A real problem outside the work's scope** is highlighted with a recommended
  follow-up issue; the review never opens one itself.
- **The clean dimensions are enumerated bare** — names only, no per-dimension
  justification. Where the whole diff is clean, the review body says so
  plainly and posts no threads: a clean review is a real outcome.

### Worked examples

A well-formed finding: severity first, one problem, the action it calls for,
the rule it breaches, attribution last. The thread's own `path` and `line` are
the anchor, so the text names no location.

```markdown
Blocking — `read_scheme()` falls back silently.

Returning `{}` when the scheme file is missing means a mistyped path reads as
an empty scheme and every caller sees zero labels instead of an error. Raise on
the missing file — python style's fail-loud rule forbids the defensive guard.

— code review · 0198a1b2-7c3d-4e5f-8a9b-0c1d2e3f4a5b
```

The same observation, malformed. It opens on no severity, hedges instead of
asserting, names no action, cites no rule, and spends its last sentence
explaining that a clean thing is clean — so a reader can do nothing with it but
read it again.

```markdown
The missing-file handling looks a bit defensive here, might be worth a look at
some point. Otherwise this file is clean and well-organized.
```

## The cycle header

The first line of every review body, four fields:

```
<review name> · <short sha> · cycle <n> · <session id>
```

For example `bug review · 8dba022 · cycle 2 · 0198a1b2-…`. This is the loop's
durable state, living where the threads live: the script parses the pull
request's review headers, and the highest `n` is the cycle count while the
newest header's sha is the last-reviewed sha. A comment carrying neither a
cycle header nor an attribution line is the user's.

## Delta re-review

Cycle 1 reads the whole diff. From cycle 2 the review reads its own open
threads plus the delta since the last-reviewed sha, which its prompt carries —
nothing more.

A rebase, or a delta that rewrites most of the diff, earns a full re-read
instead; that call is the reviewer's own. After a rebase the delta comes from
local `git diff <last-reviewed-sha>..HEAD` only. The REST compare endpoint uses
merge-base semantics and reports a force-pushed branch as diverged across every
file while the true content delta is empty (measured,
[issue #412](https://github.com/GeoffNordling/dev-playbook/issues/412)).

## Resolution ownership

No thread is ever resolved silently.

- The **builder** replies `Fixed in <sha>` on a thread it addressed, and never
  resolves one.
- The **next cycle's reviewer** reads each fix against the delta and resolves
  the threads it verifies — the same bar as any acceptance criterion.

A fix that edits the anchored line itself flips that thread to
`isOutdated: true` with `line: null`, so exactly the threads a cycle must
verify are the ones that lose their live anchor. Verification keys on `path`
plus `originalLine` and the comment text, never on a live `line` (measured,
issue #412).

## The verdict and the cap

The verdict is the traverse script's, computed from thread state; no agent
takes it. Any open Blocking thread is a rework lap; a cycle ending with zero
open Blocking threads is converged. Blocking threads still open after **four
autonomous cycles past the newest baseline** end the traverse as an escalation.
A review reports what it posted and stops — it never counts cycles toward the
cap or declares convergence.

## The `gh` mechanics

Every command names its repository outright, so none of them depends on the
directory it runs in. The reviewer resolves the pair once:

    gh repo view --json nameWithOwner --jq .nameWithOwner

`gh api` has no `-R` flag: owner and repo are spelled into the path
(`repos/<owner>/<repo>/…`) and into every GraphQL argument
(`repository(owner:"<owner>", name:"<repo>")`). The `gh pr` family does take
`-R <owner>/<repo>`, and carries it.

**Post the cycle's review** — one call. The body goes in on standard input,
because a review's `comments[]` array cannot be expressed with `-f` field
flags:

```bash
gh api repos/<owner>/<repo>/pulls/<pr>/reviews --input - <<'JSON'
{
  "commit_id": "<git rev-parse HEAD>",
  "event": "COMMENT",
  "body": "<cycle header>\n\n<clean dimensions>",
  "comments": [
    {"path": "<file>", "line": 41, "side": "RIGHT",
     "body": "Blocking — <problem, fix, and rule>\n\n— <node> · <session id>"}
  ]
}
JSON
```

**Post a file-level finding** — the standalone endpoint. A review's
`comments[]` rejects `subject_type` with HTTP 422, so this finding cannot ride
the call above; GitHub wraps it in an implicit review of its own, and the
thread it opens is resolvable like any other:

```bash
gh api repos/<owner>/<repo>/pulls/<pr>/comments \
  -f commit_id=<sha> -f path=<file> -f subject_type=file \
  -f body='Blocking — <subject named first> …'
```

**Read the threads** — the one query behind verification:

```bash
gh api graphql -f query='query { repository(owner:"<owner>", name:"<repo>") {
  pullRequest(number:<pr>) { reviewThreads(first:100) { nodes {
    id isResolved isOutdated path line originalLine subjectType
    comments(first:10) { nodes { databaseId body } }
  } } } } }'
```

**Resolve a verified thread** — GraphQL only; REST has no resolve, and the
mutation takes the thread's `PRRT_…` node id, not the `databaseId` a reply
takes:

```bash
gh api graphql -f query='mutation { resolveReviewThread(
  input:{threadId:"<PRRT_… id>"}) { thread { id isResolved } } }'
```

Every command above ran live on
[issue #412](https://github.com/GeoffNordling/dev-playbook/issues/412)'s
prototype.

## Escalation

Where the review cannot be produced at all, it surfaces the block and stops,
ending on the report envelope with `outcome` `"escalated"` and the reason in
`gist`. Two blocks recur — a red green gate, and a missing pull request or
diff — and each review states its own full list. Nothing about an escalation is
written to GitHub; the run's report is the record.

### Findings are not escalations

A problem the review can describe belongs in a thread. Escalation is reserved
for something stopping the review from being produced at all.
