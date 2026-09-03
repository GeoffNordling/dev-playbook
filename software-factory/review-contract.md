---
type: Guide
title: Review Contract
description: The contract the three reviews run under — the two severities, the thread model, the cycle header, delta re-review, suggestion dispositions, the report envelope, and the escalation boundary
---

# Review Contract

What a review does once it is launched: the gate it runs before reading
anything, the threads it leaves behind, and the line between a finding and an
escalation. Every clause binds every review — bug, code, and doc alike.
Each review supplies its own values and inherits everything else:

- **Review name** — `code review`, for instance. It opens the cycle header and
  it is what the cycle count counts.
- **What counts as Blocking** — one line, and it differs by review.

Which reviews run at a cycle is
[factory-operations.md](/software-factory/factory-operations.md#the-review-stop);
how a pull request's existing feedback is read is
[pr-feedback.md](/software-factory/pr-feedback.md).

What happens to a Suggestion after it is posted is
[Suggestion dispositions](#suggestion-dispositions) below. It binds the
Adjudicator rather than a review, and it is stated here because it is what
the Suggestion severity means.

## The stance

A review is an **audit only**, hands-off: it never modifies the work under
review, and the verdict on its findings is not its to take — it posts them
and stops. Defects route back to the authoring node through the
script-computed verdict.

Finding problems is its output, not a reason to stop.

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
one of these sources. Everything else is a Suggestion at most:

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

A finding is a resolvable thread on the pull request. One run posts **one
GitHub review, verdict `COMMENT`** — the only verdict a single account may
give its own pull request. The review body carries the cycle header and the
clean dimensions, bare; the inline comments are the findings.

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
explaining that a clean thing is clean.

```markdown
The missing-file handling looks a bit defensive here, might be worth a look at
some point. Otherwise this file is clean and well-organized.
```

## The cycle header

The first line of every review body:

```
<review name> · <short sha> · cycle <n> · <session id>
```

For example `bug review · 8dba022 · cycle 2 · 0198a1b2-…`. This is the loop's
durable state, living where the threads live: the script parses the pull
request's review headers, and the highest `n` is the cycle count while the
newest header's sha is the last-reviewed sha. A comment carrying neither a
cycle header nor an attribution line is the user's.

**Where the writer gets `n`.** The review counts it, and counts its own name
alone: the prior review bodies on the pull request whose header opens with
this review's name, plus one, read from

    gh api --paginate repos/<owner>/<repo>/pulls/<pr>/reviews

That endpoint returns each body byte-identical and ordered by ascending `id`,
so `n` is read rather than guessed — and a review that stands down for a cycle
leaves its own count where it was.

`--paginate` is not optional. The endpoint returns 30 reviews per page,
oldest first, so an unpaginated read drops the *newest* headers — exactly the
ones the count depends on. A traverse busy enough to approach the cap is the
one whose count would silently reset, leaving the cap unable to trip.

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

**Open threads are scope.** From cycle 2 an empty delta is an ordinary cycle,
not a block: a lap that fixed nothing this review owns still leaves it threads
to verify and resolve. Only cycle 1 finding no diff at all stops the review,
because then there is nothing to read from either source.

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

## Suggestion dispositions

A Suggestion does not sit on the pull request until someone gets to it. The
**Adjudicator** — launched at each verdict point, once the cycle's reviews have
reported — settles every open Suggestion thread into one of these outcomes:
**fix now**, **defer**, or **decline**. No review dispositions a finding, its
own included.

Worth is not weighed here. The routing below is checkable questions, and whether
a suggestion is worth doing is the user's — at the triage of a deferral stub, or
at the merge read.

### The disposition dimensions

Each is checkable by inspection, save the one marked.

- **Contradicts the record** — the suggestion conflicts with a named standard,
  conflicts with a recorded ruling, or re-litigates a decision already taken
  this traverse.
- **No consequence** — it cannot name what gets worse if it is ignored: a
  consequence for behavior, correctness, performance, security, or a named
  convention. Pure preference fails this.
- **Bad idea** — the Adjudicator is confident the change would make the work
  worse, or its premise is false. This is the one judgment dimension, and not
  checkable by inspection: the confidence is gated by
  [the routing test](/software-factory/deviation-contract.md#the-pr-callout-lane),
  and doubt still defers.
- **Needs design decisions** — the stated fix leaves a significant design choice
  open, so carrying it out would have an autonomous agent take a design
  decision. It does not take them.
- **Touches new files** — the stated fix would modify at least one file the pull
  request's diff does not already modify (`gh pr diff --name-only`).
- **Entangled or independent** — where the *problem* lives, as against where the
  fix would land: entangled when the suggestion's subject — the code the finding
  is about, not merely where its comment anchors — lies inside the diff;
  independent otherwise.

### The routing

Ordered, first hit wins, and doubt defers.

| Order | Condition | Outcome |
|---|---|---|
| 1 | Contradicts the record | **Decline** (`contradicts-standard` / `contradicts-ruling` / `re-litigates`) |
| 2 | No consequence | **Decline** (`no-consequence`) |
| 3 | Bad idea | **Decline** (`bad-idea`) |
| 4 | Needs design decisions | **Defer** (`needs-design`) |
| 5 | Touches new files | **Defer** (`outside-diff`) |
| 6 | Entangled, fix fully specified, inside the diff's files | **Fix now** |
| 7 | Independent — everything remaining | **Defer** (`independent`) |
| — | Any answer in doubt | the doubted branch resolves toward **Defer** (`doubt-defers`) |

**The reason vocabulary** is these names and no others:
`contradicts-standard`, `contradicts-ruling`, `re-litigates`, `no-consequence`,
`bad-idea`, `needs-design`, `outside-diff`, `independent`, `no-remaining-laps`,
`doubt-defers`. Each is written verbatim wherever a disposition is mentioned —
`Declined (no-consequence)`, `Deferred (needs-design) → #512` — so one query
finds every disposition of a kind.

### The outcomes

- **Fix now** — the item joins a rework lap that open Blocking threads already
  necessitate; a suggestion fix never causes a lap of its own. Its thread
  stays open, and the next cycle's reviewer reads and resolves it like any
  other fix. A fix now with no lap left to ride **downgrades to
  defer**, reason `no-remaining-laps`, and is then reported exactly like every
  other deferral — which is what a converged verdict does to every fix now, and
  what the next verdict point does to a fix-now thread a reviewer left open on a
  cycle that has since converged. It stays a Suggestion throughout: it never
  gates convergence and it never escalates.
- **Defer** — a real tracker stub at `phase:intake`, labeled `origin:deferral`
  ([Label Scheme](/standards/tracking/label-scheme.md#valid-labels)), so
  every issue born of a factory deferral is one query away. Doubt lands here: a
  stub is reversible, and information a decline drops is gone.
- **Decline** — a one-line reply naming its reason from the vocabulary, and no
  stub.

**Reply, then resolve.** A declined thread and a deferred thread are both
resolved by the Adjudicator, and never before its reply is on them: the reply
is the record of why. A fix-now thread is resolved by nobody here — it
belongs to the next cycle's reviewer, under
[resolution ownership](#resolution-ownership).

**Where a settled suggestion is listed.** Every fixed and declined suggestion
takes one line in the pull request's `## Suggestion dispositions` section, and
every deferral's stub is linked under `## Deferred`
([the merge-message recipe](/software-factory/factory-operations.md#the-merge-message-recipe)).
A declined line carries the vocabulary reason it was declined for; a fixed one
carries none, because `fix now` is where the routing lands when no decline and
no defer condition hit, and the vocabulary has no name for that. It names the
commit the fix landed in instead. Both sections are brought up to date on every
Adjudicator run, and the run at convergence always happens, so they are complete
at the merge read.

**A fixed suggestion is recovered from its own thread.** A decline and a
deferral each leave the Adjudicator's reply standing on the thread, so their
record outlives the run that made it. A fix-now ruling leaves none: the ruling
is written only in a report nothing reads back, and by the time the fix lands
the next cycle's reviewer has resolved the thread, which every later docket then
passes over. The thread still holds the proof, so that is where a later run
reads it: a **resolved** Suggestion thread whose replies carry a builder's
`Fixed in <sha>` and no reply signed `— adjudicator` was ruled fix now and got
fixed, and it takes its line from that.

## The `gh` mechanics

Every command names its repository outright, so none of them depends on the
directory it runs in. The reviewer resolves the repository, then the pull
request, in that order:

    gh repo view --json nameWithOwner --jq .nameWithOwner
    gh pr list -R <owner>/<repo> --head "$(git rev-parse --abbrev-ref HEAD)" \
      --json number,headRefOid

**The number comes before `-R`, because `-R` is what makes it mandatory.**
Naming the repository turns off branch inference, so a `gh pr` command that
would otherwise find its own pull request no longer can — bare
`gh pr view -R <owner>/<repo> --json number` exits on `argument required when
using the --repo flag`. `gh pr list` is the one command in the family that
takes a branch instead of a number, which is why it opens the sequence; every
later `gh pr` call carries `-R <owner>/<repo>` **and** the number it returned,
as in `gh pr diff -R <owner>/<repo> <pr>`. The branch comes from the local
checkout, the same place the delta's `git diff` reads from.

`gh api` has no `-R` flag at all: owner and repo are spelled into the path
(`repos/<owner>/<repo>/…`) and into every GraphQL argument
(`repository(owner:"<owner>", name:"<repo>")`).

**`headRefOid` is the `commit_id` for everything below.** It is the branch tip
GitHub itself holds, and the posting endpoints reject a sha that is not on the
pull request with HTTP 422. Local `HEAD` agrees with it only until it doesn't —
an unpushed commit, or a push that landed after the reviewer read the tree —
so the value resolved above is the one that is used, and local `HEAD` never is.

**Never write the JSON by hand.** Findings quote code, and code contains `"`,
`\`, and newlines. One quoted finding in a hand-written payload makes the whole
body invalid, the `reviews` call fails, and the cycle posts nothing at all —
which the loop then reads as the review never having run, because the cycle
header is the only record it has. So each body is written to a plain text file
and `jq` assembles the payload around it: escaping becomes the tool's job, and
no finding's content can break the call that carries it.

**Post the cycle's review** — one call. The payload goes in through `--input`,
because a review's `comments[]` array cannot be expressed with `-f` field
flags:

```bash
# review-body.txt holds the cycle header and the clean dimensions;
# finding-1.txt holds one finding, severity first and attribution last.
jq -n \
  --arg commit "<headRefOid>" \
  --rawfile body review-body.txt \
  --arg path1 '<file>' --argjson line1 41 --rawfile body1 finding-1.txt \
  '{commit_id: $commit, event: "COMMENT", body: $body,
    comments: [{path: $path1, line: $line1, side: "RIGHT", body: $body1}]}' \
  > payload.json

gh api repos/<owner>/<repo>/pulls/<pr>/reviews --input payload.json
```

One `--arg`/`--argjson`/`--rawfile` trio and one `comments[]` entry per
finding. `jq` fails loudly on a missing file, so a lost finding stops the call
rather than posting a review that quietly omits it.

**Post a file-level finding** — the standalone endpoint. A review's
`comments[]` rejects `subject_type` with HTTP 422, so this finding cannot ride
the call above; GitHub wraps it in an implicit review of its own, and the
thread it opens is resolvable like any other. It is assembled the same way, for
the same reason:

```bash
jq -n --arg commit "<headRefOid>" --arg path '<file>' \
      --rawfile body finding-file-level.txt \
  '{commit_id: $commit, path: $path, subject_type: "file", body: $body}' \
  > file-comment.json

gh api repos/<owner>/<repo>/pulls/<pr>/comments --input file-comment.json
```

**Read the threads** — the one query behind verification, and the same read a
committing node makes on a rework lap. It is stated once, in
[PR feedback](/software-factory/pr-feedback.md#the-comment-surfaces), paging and
all; read it there rather than from a second copy that drifts from it.

**Resolve a verified thread** — GraphQL only; REST has no resolve, and the
mutation takes the thread's `PRRT_…` node id, not the `databaseId` a reply
takes:

```bash
gh api graphql -f query='mutation { resolveReviewThread(
  input:{threadId:"<PRRT_… id>"}) { thread { id isResolved } } }'
```

Each endpoint above ran live on
[issue #412](https://github.com/GeoffNordling/dev-playbook/issues/412)'s
prototype, which is where the 422s and the GraphQL-only resolve were measured.
The `jq` assembly, the `--paginate` flag, the thread paging, and the `-R`
working order came later, on
[issue #457](https://github.com/GeoffNordling/dev-playbook/issues/457): the
`-R` failure and `jq`'s escaping of a finding carrying `"` and `\` were
measured there, the pagination limits are GitHub's documented page sizes.

## The report envelope

Every run ends on the report envelope — structured output, never a message
alone — and every field is always present:

| Field | Value |
|---|---|
| `outcome` | `"done"` when the review posted, `"escalated"` when it could not be produced |
| `gist` | the pull request and what the cycle found, or the reason the review stopped |
| `blocking_count` | the Blocking threads this run posted |
| `suggestion_count` | the Suggestion threads this run posted |

An escalation posts no threads, so it carries `0` for both counts — stated,
never left out. The envelope is read by its shape, so a field omitted is a
malformed report.

## Escalation

Where the review cannot be produced at all, it surfaces the block and stops,
ending on the envelope with `outcome` `"escalated"` and the reason in `gist`.
The blocks that recur are a red green gate and a missing pull request or
diff; each review states its own full list. Nothing about an escalation is
written to GitHub; the run's report is the record.

### Findings are not escalations

A problem the review can describe belongs in a thread. Escalation is reserved
for something stopping the review from being produced at all.
