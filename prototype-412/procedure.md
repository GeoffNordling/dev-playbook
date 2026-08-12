---
type: Guide
title: Thread-model review mechanics — the verified command sequence
description: "The exact command sequence for the #409 thread-based review loop, verified live on PR #414 — reviews, threads, replies, resolution, delta re-review, rebase behavior, and the merge-gate query"
---

# Thread-model review mechanics — the verified command sequence

The prototype artifact for [wayfinder ticket #412](https://github.com/GeoffNordling/dev-playbook/issues/412).
Every command below ran live against [PR #414](https://github.com/GeoffNordling/dev-playbook/pull/414)
on 2026-08-12, single account, `gh` authenticated with the repo PAT. `{o}/{r}`
abbreviates `GeoffNordling/dev-playbook`; `$N` is the PR number. The findings
report — where live behavior deviates from the #409 design — is the resolution
comment on #412; this file is the how, not the verdict.

## 0. Assumption probes

`REQUEST_CHANGES` on one's own PR is refused, as the design assumes
(`APPROVE` is refused the same way; the verdict is always `COMMENT`):

    gh api repos/{o}/{r}/pulls/$N/reviews -f event=REQUEST_CHANGES -f body="..."
    # → HTTP 422 "Review Can not request changes on your own pull request"

## 1. One review per cycle, with line-anchored findings

A cycle's review is a single REST create-review call. Inline comments ride the
`comments[]` array; each opens a resolvable thread; severity is the first word
of the comment body (plain text — nothing to configure). The JSON goes through
`--input` because `gh -f` cannot express arrays.

    gh api repos/{o}/{r}/pulls/$N/reviews --input review.json

```json
{
  "commit_id": "<head sha being reviewed>",
  "event": "COMMENT",
  "body": "bug review · <short sha> · cycle <n>\n\n<clean dimensions>\n\n## Unanchored findings\n\n<body-borne findings, if any>",
  "comments": [
    {"path": "<file>", "line": <n>, "side": "RIGHT", "body": "Blocking: <finding>"}
  ]
}
```

A body-only review (no `comments[]`) is valid — cycle 3's converging review
was one.

## 2. File-level findings — standalone endpoint, not the review array

The create-review `comments[]` array **rejects** `subject_type`
(`Field is not defined on DraftPullRequestReviewComment`), so a file-level
finding cannot ride the cycle's review submission. It goes through the
standalone comments endpoint, and GitHub wraps it in its own implicit review
object:

    gh api repos/{o}/{r}/pulls/$N/comments \
      -f commit_id=<head sha> -f path=<file> -f subject_type=file \
      -f body="Blocking: <subject named in first line> ..."

The resulting thread is resolvable like any other and reports
`subjectType: FILE`.

## 3. Reading the threads

The one query behind verification, disposition, and the merge gate. The
`databaseId` of a thread's first comment is the key for REST replies.

    gh api graphql -f query='query { repository(owner:"{o}", name:"{r}") {
      pullRequest(number:$N) { reviewThreads(first:100) { nodes {
        id isResolved isOutdated path line originalLine subjectType
        comments(first:10) { nodes { databaseId body author { login } } }
      } } } } }'

## 4. The builder's lap

Push the fix commits, then reply on each addressed thread — never resolve:

    gh api repos/{o}/{r}/pulls/$N/comments/<first-comment-databaseId>/replies \
      -f body="Fixed in <sha>."

## 5. The reviewer's next cycle

Delta since the last-reviewed sha is plain git; the compare API is **not**
equivalent (see §7):

    git diff <last-reviewed-sha>..HEAD

Verify each open thread's fix against the delta, then resolve it (GraphQL
only — REST has no resolve):

    gh api graphql -f query='mutation { resolveReviewThread(
      input:{threadId:"<PRRT_… id>"}) { thread { id isResolved } } }'

New findings on the delta: a fresh §1 review at the new `commit_id`.

Anchor caveat measured live: a fix that edits the anchored line itself flips
that thread to `isOutdated: true` with `line: null` — only `originalLine`
survives. Verify fixed threads against the delta and `originalLine`, never a
live `line`. A thread anchored *below* an insertion drifts cleanly
(`line` 15 → 16, not outdated).

## 6. Manager dispositions

Reply first, citing the standardized reason, then resolve (same mutation as
§5), then record the disposition line in the PR body's
`## Suggestion dispositions` via §8.

    gh api repos/{o}/{r}/pulls/$N/comments/<databaseId>/replies \
      -f body="Declined (no-consequence). <one line why>"

## 7. Rebase / force-push behavior

    git rebase --force-rebase origin/main && git push --force-with-lease

Measured on a content-identical rewrite (shas changed, trees identical):
every thread survived — resolved stayed resolved, the open thread kept its
anchor, nothing new went outdated. But the last-reviewed sha leaves the
branch, and the REST compare endpoint against it
(`gh api repos/{o}/{r}/compare/<old>...<head>`) uses merge-base semantics —
it reported `diverged` listing **all** files while the true content delta was
empty. Local `git diff <old>..<head>` stays truthful while the object exists.
The design's "full re-read after a rebase" is therefore not just prudent but
necessary whenever the manager reads deltas through the API.

## 8. The four-section body across edits

`gh pr edit $N --body` replaces the whole body — maintenance is
read-modify-write of the entire text, same as issue bodies. All four `## `
sections survived verbatim; there is no merging behavior to lean on.

    gh pr view $N --json body --jq .body   # read
    gh pr edit $N --body "$(cat <<'EOF' … EOF)"   # write back entire

## 9. The soft merge gate

Zero unresolved threads, read in one query:

    gh api graphql -f query='…reviewThreads(first:100) { nodes { isResolved } }…' \
      --jq '[.data.repository.pullRequest.reviewThreads.nodes[]
             | select(.isResolved | not)] | length'
    # → 0 ⇒ gate passes
