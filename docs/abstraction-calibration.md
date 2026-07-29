---
type: Survey
title: Abstraction Calibration
description: Where the human should live in an AI-written repo — the slop trench, the pandas standard, and the bet on invented, deterministically-enforced primitives
---

# Abstraction Calibration

A conversation-derived survey (2026-07-25) of a central problem in
AI-assisted development: once an AI writes most of the code, the human's
understanding of the system stops accumulating for free — it used to be a
byproduct of typing, and now it has to be engineered deliberately. The fix is
neither "read more code" nor "trust the AI more"; it is choosing, on purpose,
the abstraction level the human operates at, and enforcing it by mechanism.
The material here is an analysis and a bet, not a decision — nothing below
commits us to building anything.

## The problem: the slop trench

The workspace repos (dev-playbook, story-forge, mission-control, spec-tools
itself) are a mix of code and Markdown — and the Markdown is English code: it
instructs agents, so it executes. The AI reads all of it; no human reads all
of it. Left unmanaged, that asymmetry has a known failure mode: the AI
surfaces summaries and escalates decisions framed below the human's operating
level, and the human either rubber-stamps or slows to a crawl. That's the slop trench —
nominal ownership of a system whose details have outpaced inspection. This
survey is about the mechanisms that keep a workspace out of it.

Human understanding is naturally strongest at the surface and thins toward
implementation detail — for dev-playbook, script names and roles are readily
at hand while internals are AI-owned. That distribution is not itself the
problem; it's exactly how we intended to operate in an AI-first world and it worked well in the pre-AI era, with humans writing high-level code against low-level APIs. The gap is that deterministic software has
a deliberately designed API surface to be fluent *in*, while AI repos don't.

The full componentization of the original notes:

1. **The problem** — the slop trench, as above.
2. **The thought experiment** — if the human had hand-typed everything in dev-playbook, including all the Python and all the English text, they'd understand the APIs, the objects, and their ownership
   intuitively. That kind of knowledge is the target.
3. **Current-state assessment** — the operating level has drifted high
   without a designed surface beneath it; the mental model is thinner than
   the pandas standard demands.
4. **The proposed artifact** — an intermediary layer: precise enough to carry
   intent to the AI, small enough for the human to hold and grep all of it,
   and bidirectional — both parties read and write it.
5. **The enforcement requirement** — the layer must be deterministically
   lintable: claims made at that layer are proven against the code by
   tooling, not by trust.
6. **The spec-tools question** — wrapping everything in spec-tools feels
   wrong; is that a real defect, or just appetite for greenfield invention?
   (Both answers appear below: a real ratio defect *for this use*, and a
   restraint rule to keep the appetite honest.)
7. **Scope discipline** — don't bite it all off at once; dev-playbook is the
   worked example, but the problem spans every repo.

## The pandas standard

Before AI, the human operated pandas for years without ever (or rarely)
reading inside a pandas method. Yet they knew the API like the back of their
hand: which objects exist, which methods and functions fit which task, how
they compose, which patterns are idiomatic. DataFrame, then Index, then
groupby, concat, aggregation — understanding each later primitive required
holding the earlier ones.

That is the target state for the workspace's own repos: fluency in a surface
of nouns, contracts, and patterns, with the internals owned by the AI the way
pandas internals were owned by the pandas maintainers.

Two mechanics made pandas fluency happen, and both matter for reproducing it:

- **The human was the caller, daily.** Fluency was the residue of thousands
  of invocations, not of reading documentation. Every layer the human is
  fluent in today (pandas, git, the software factory) was learned by
  operating through it; every layer they're not fluent in (the script
  internals) is one they never call — pre-commit calls it.
- **The interface was a forcing function.** Pandas and git *impose* their
  abstractions. A malformed mental model of git doesn't survive contact:
  wrong command, error; wrong model of branches, an inexplicable merge
  conflict. The product pushes back until the model is correct.

## The axis, and the diagnosis

There is a latent optimal point on the abstraction/detail axis, and neither
party knows it a priori:

- **Too low** (low abstraction, high detail): the human either wastes time
  doing things the AI could do, or — more realistically — stops paying
  attention entirely and the session becomes slop anyway.
- **Too high** (high abstraction, low detail): the human cannot understand
  what's happening, and it's slop no matter how hard they try to pay
  attention.

The diagnosis for why everyone lands badly on this axis: **AI removed the
forcing function.** Natural language is the first interface in computing that
imposes no abstraction level at all. It meets the user wherever they are —
including at an incoherent, drifting level — and never pushes back. Nothing
rejects a malformed mental model; the model just gets quietly worked around.
So the default operating point is non-principled — not by anyone's choice,
but because nothing constrains it. That is where slop is born.

The human knows git branches, worktrees, and the filesystem not from reading
but because the products they consume (Claude Code, computers in general, etc.) compel living
in those abstractions. The repos' internals stopped compelling anything the
day the AI started typing the code.

Corollary: the layer proposed below is not documentation. It is a
*replacement forcing function*, self-imposed because the interface no longer
provides one. This is the repo's own epigraph ([README](/README.md)) applied
to this problem: good intentions don't work, mechanisms do. "Pay closer
attention" is an intention; "the AI may only escalate in layer nouns, and
layer claims fail the gate when they drift" is a mechanism.

## The bet: invented, enforced primitives

Unlike pandas — where someone else built the primitives and the human learned
them — here we are free to invent our own. And "skills/markdown can be
literally anything" is an upper bound, not an obligation: we are allowed to
constrain ourselves.

The bet: build intermediary layers out of invented primitives that are

1. **human-graspable** — a small noun-set the human can hold and grep
   entirely, and
2. **deterministically validated to the maximum practical extent** — with
   the proven/unproven boundary kept explicitly visible.

Validation will never reach 100% (it doesn't for
[Standards](/standards/standard/format.md) today). Whatever is not
deterministically validated is AI judgment with a residual slop risk —
unavoidable and acceptable, *provided it is labeled*. Labeled means the
artifact itself records, where the claim is read, whether a gate or only
judgment stands behind it. The [Python Testing card](/standards/testing.md)
is the working example: its Audit cell names exactly three rules that
testing-lint checks (no private-name access, mirror placement, no `if`/`try`
in a test body), and its Enforce cell names the commit gate they ride. Every
other convention in the same Define doc — behavioral focus, test doubles,
humble objects — is prose the AI follows by discipline. All of it reads as
equally authoritative prose; the card cells are what tell you the three rules
cannot silently drift while the rest can.

The labeling happens at authoring time, in the artifact — not in
conversation. Relying on the AI to mention the trust category each time it
cites a rule would be an intention; the card is the mechanism, and the label
is itself linted (standards-lint fails the gate when an Enforce cell
disagrees with the actual hook surface). Whether the AI should *also* cite
the label when escalating a decision that leans on an unproven claim is an
open question, left to the escalation-discipline rule below.
Unproven-but-labeled is fine; unproven-and-unlabeled is where slop breeds.

### Relation to spec-tools and SDD

Spec-driven development, as [spec-tools](~/workspace/spec-tools/README.md)
implements it, is a legitimate methodology with its own purpose:
deterministically verified functional and design requirements, expressed
without looking inside the system. Nothing here condemns it.

The narrower question this survey asks is whether spec-tools is the right
vehicle for *this* problem — the inhabitable human layer — and the answer is:
not convinced. Full spec-tools items are walls of normative text; the human
cannot live at that layer and would fall asleep if they tried.
For this use, the surface-to-formality ratio is wrong: everything is the
formal layer.

One element of its design does transfer directly: the pinned `Interface:`
declaration — a thin, byte-for-byte-checked formal line embedded in
surrounding prose (checked by griffe against the real source, no imports).
That's the skeleton-in-flesh ratio this survey keeps returning to: a skeleton
of pinned, deterministically-checked claims inside flesh that stays readable.

## Worked examples from dev-playbook

Five artifacts, examined for where their correct layer sits and whether it's
already inhabited and/or proven.

### ref-lint (a script) — the layer works

Two levels fail:

- Too high (the README one-liner): "ref-lint checks cross-references."
  Can't answer "should this file use a Link or a Citation?" or "why did my
  commit fail?"
- Too low (where the AI lives): regexes over non-fenced spans,
  `ROOTLESS_SEGMENTS` exemptions, worktree-vs-main-checkout resolution.

The pandas-level in between is a handful of nouns plus one contract:

- **Reference** — exactly two species: **Link** (`[text](/path)`,
  root-absolute, must resolve inside the same repo) and **Citation**
  (`~/workspace/<repo>/…`, points across repos).
- **Scanned surface** — authored Markdown *minus* fenced code and inline code
  spans. (A boundary fact used constantly, like knowing what `concat` does
  with indexes.)
- **Finding** — `file:line: rule-id message`. One line, one defect.
- **Contract** — ref-lint is a **detector**: repo root in, findings out,
  exit 0/1/2, targets discovered via `git ls-files`. It enforces exactly two
  rules: `broken-reference` and `wrong-form-citation`.

Hold those five sentences and you can predict every behavior that matters,
argue about design, and diagnose any gate failure — without ever seeing the
regex.

Why it scales: pandas is graspable not because it's small but because a few
shapes recur everywhere (everything takes and returns a DataFrame). All ten
detectors in the [playbook-lint roster](/scripts/README.md) are
detector-shaped with Finding-shaped output. Learn the contract once; each new
detector costs only its nouns (testing-lint: mirror-placement and privacy;
okf-lint: concept-doc and index freshness).

Lintability hook: the layer is partly *derivable*. Every detector already
answers `--list-rules` machine-readably. A per-script contract card (surface,
nouns, rules) could be checked against the code — rules listed must equal
`--list-rules` output, roster membership must match
[playbook_lint.py](/src/dev_playbook/playbook_lint.py). The card lies, the
gate fails.

### OKF — the control case, closed

"We use OKF on all our non-harness-injected Markdown." One sentence; both
parties understand it; fully linted (okf-lint). The human understands it
because they read the spec when it came out and directed the implementation.
Nothing to build. This is what a *solved* artifact looks like: trivial
noun-set, full enforcement.

### Standard — the full pattern, already built

This was a deliberate earlier attempt to operate at the correct level, and it
worked. The human holds four role-primitives — **define** (markdown),
**audit** (a detector: linter or judgment), **enforce** (the pre-commit
gate), **adopt** (markdown) — and knows what each is made of, without having
memorized the rule prose, the scripts, or the judges.

The piece doing the heavy lifting sits just below the surface: the
**card↔rule matrix**, which
[standards-lint](/standards/standard/format.md) checks — card layout, matrix
integrity, and agreement between every Enforce cell and the actual hook
surface. "This rule is enforced" is not a belief; it's a linted claim. (In
conversation the matrix "rang a bell but hadn't been thought about in a long
time" — which is correct: it's below the public API, like logic inside a
pandas method. Consulted, not memorized. Things below the public API are
*expected* to fall out of the human's head; the layer is what's kept.)

Verdict: the division of ownership — human holds the primitives and the
coverage boundary; AI holds the rule prose, scripts, and judgments — is
correct. Standard is the template: the only artifact so far with both
inhabitation *and* proof.

The test that keeps the division honest: every decision the AI escalates must
be expressible at the layer. "Should this rule be a linter or a judgment?" —
layer-level; the human rules on it. "Should `ROOTLESS_SEGMENTS` exempt this
path?" — below the layer; the correct move is not to descend but to force the
question up: either it restates in layer terms ("should Decision Records be
exempt from the citation-form rule?") or the layer is missing a noun.

### Software factory — inhabited, unproven

The human understands the factory through four primitives: the **mermaid
graph** (the state machine), the **four-tuple labels**, the **skills**
attached to each node, and the **git procedures** as it runs. This is not
vibes — it's real fluency, earned the same way pandas fluency was: they
designed it at that level and operate it daily
([software-factory/](/software-factory/index.md)).

Two lessons the factory teaches:

- **Correct layer size is a property of design quality, not system size.**
  The factory spans dozens of files, and file count says nothing about how
  hard it is to hold — that's an AI-centric metric (how much must be read to
  verify a claim). By the human's metric — do named primitives predict
  behavior? — the factory is easy. Pandas is enormous and compresses to a
  few shapes; the factory compresses to four primitives. An artifact whose
  layer won't compress is a smell about the artifact.
- The factory is the **existence proof** that the layer approach works — and
  simultaneously the demonstration of the missing half: the skill bodies are
  AI-authored English the human doesn't read, and nothing lints that the
  graph matches what the skills actually do. Graph-in-head and prose-in-repo
  stay in sync only by discipline. Inhabited, unproven — the mirror image of
  a hypothetical fully-linted layer nobody lives in.

A candidate primitive surfaced here — "skill-driven, git-supported state
machine" — and was shelved by the n≥2 rule below: with one instance it's
taxonomy, not tooling. Revive it if mission-control or story-forge grows a
second one.

### Skills — the signature idea, shelved

Skills are the closest non-code thing to code: English that executes. Their
problem is that they can be literally anything, so the human reads the title,
develops an intuition from watching sessions, and everything beneath operates
below the surface. Their advantage: the human lives in them all day, so
intuition does accumulate.

The idea worth recording: **give skills a signature.** A pandas method is a
signature (typed, enforced at every call) plus a docstring (freeform prose);
skills today are all docstring. A skill could carry a small set of declared,
machine-checkable claims — gates it runs, scope it may touch, stops where it
waits for a human — with the prose staying prose around them. Two things make
this more than wishful:

- **Declarations can bind at runtime, not just describe.** Statically linting
  freeform English is a losing battle —
  [skill-lint](/standards/claude-code/skill-conventions.md) checking format
  is necessary but cosmetic. But hooks exist: a skill declaring
  `scope: docs/**` can have an edit outside that scope *blocked*, which
  checks a path against a manifest rather than parsing English. Same trick
  as the detectors: don't understand the prose, verify the claims.
- **The primitives should be discovered, not legislated.** Read the ~30
  existing skills and extract what shapes actually recur (gate, stop,
  artifact-produced, delegation, scope). If most skills decompose cleanly,
  the grammar is real; if every skill demands a new primitive, it's fiction.
  And tier the constraint by risk, not by category. Skills that run
  unattended and write durable state — commits, PRs, labels that downstream
  consumers read — are where undetected drift compounds, and their regular
  shape (gates, stops, transitions, artifacts) makes them the easiest to
  constrain: strict grammar there (today, the factory-node skills — intake,
  tdd, the reviews). Skills the human watches at every invocation, where a
  bad run costs one conversational turn, stay free (orient, usage-report). "Can
  be anything" remains available; it stops being the default for
  load-bearing skills.

Shelved deliberately: the human understands their skills today (designed
them all, uses them routinely), so this is not where effort goes now. It's
recorded because it's the clearest articulation of the general mechanism.

## The meta-pattern

Extracted from the examples — not invented:

1. **A small noun-set** — the domain's primitives, one page, greppable.
   (Factory: graph / labels / skills / git. Standard: define / audit /
   enforce / adopt. ref-lint: Link / Citation / surface / Finding.)
2. **A recurring contract** — everything is X-shaped; learn it once. (All
   ten detectors share one shape.)
3. **Binding claims** — assertions at the layer that deterministic code
   checks. (The card↔rule matrix; `--list-rules` equality; hook-enforced
   scope.)
4. **A visible coverage boundary** — what's proven vs. what's prose-only.
   The human need not know rule internals, but must know which side of the
   line a claim sits on, because that's what says how much to trust it.

## Cross-repo generalization

Pandas worked as one vocabulary because it's one domain: tabular data. The
repos are heterogeneous domains, so there will be no single noun-set covering
them. What generalizes:

- **The meta-pattern** above, applied per domain.
- **A universal core** that already recurs workspace-wide because
  dev-playbook forces it: detector, finding, rule-id, gate, index,
  vocabulary doc, label-tuple. A dozen-ish nouns.
- **Per-repo domain nouns**, each declared in that repo's `CONTEXT.md` —
  which is exactly what [CONTEXT.md](/CONTEXT.md) already is for this repo.

Total surface the human would hold: roughly a pandas cheat sheet. That is the
feasibility argument — the size is right.

## The two hard parts (neither is tooling)

**Inhabitation.** Every layer the human actually knows, they know from
operating through it daily, not from reading it. So the layer must become the
language of the human↔AI interface itself: decisions, issues, gate failures,
and the AI's questions all expressed in layer nouns. The human is the caller
again — that's what made pandas stick. And the human is *always* working;
no version of this system has them walking away to the beach. The design goal
is never absence — it is the correct altitude, held by mechanism.

**Restraint.** This is the original spec-tools question (component 6)
wearing a new hat: appetite for greenfield invention is itself a slop
vector. The guard: **extraction over invention.** Nearly every primitive
named in this survey already exists in the repos; the work is compressing
them onto one page and wiring their claims into gates that already run. No
new primitive without a second use case (the n≥2 rule that shelved
"skill-driven git-supported state machine"). The moment we're inventing
primitives with no second instance, we're decorating, not building.

## Operating rules

Two rules fall out that change day-to-day behavior immediately, before any
tooling exists:

1. **Escalation discipline.** The AI is never allowed to escalate a question
   to the human from below the layer. Either the question restates in layer
   nouns, or the AI proposes a new noun for the layer. The slop trench, in
   one sentence, is the AI asking questions from below the human's layer and
   the human trying to answer down there. The human gets stuck in the mud.
2. **Extraction over invention.** As above: primitives are named from what
   recurs, never legislated a priori; n≥2 or it's shelved.

## Where this leaves it

No decision is taken by this document. The candidate moves, in rough order of
cheapness, all deliberately unscheduled:

- Practice escalation discipline immediately (costs nothing; needs no code).
- Per-repo noun pages: compress each repo's layer onto one greppable page
  (`CONTEXT.md` is the natural home) — extraction, not authorship.
- Contract cards for detectors, checked against `--list-rules` and the
  roster — the cheapest new *proof*, since the machinery half-exists.
- The skill-shape study (empirical grammar over the ~30 skills) — only if
  and when skills stop being well-understood by their author.
- Factory graph↔skill correspondence checking — highest value among proofs,
  hardest to make deterministic; no approach chosen.
