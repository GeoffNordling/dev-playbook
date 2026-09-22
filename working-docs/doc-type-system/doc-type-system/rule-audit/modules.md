---
type: General-Sheet
title: Modules Family Rule Audit
description: The rule audit over the standards/modules/ family — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---

# Modules Family Rule Audit

The family holds seven rules in one Standard,
Module Design Conventions, over the
population "a module in a governed repo's source". One trailer needs
reclassification: `modules.results-are-returned-not-written` is
decidable by an AST pass and moves to deterministic; nothing moves the
other way. No rule carries a detector — all seven verifier rows are
null and no code under `scripts/` or `src/` emits a `modules.` id — so
no rule is weakly checked and none is fully checked. Six of the seven
break against `src/dev_playbook/`: only
`modules.two-adapters-or-no-seam` holds, and it holds because its own
wording lets a test fake count as the second adapter. Two rules are low
value: `modules.two-adapters-or-no-seam`, which nothing in the repo
could break, and `modules.the-interface-is-the-test-surface`, whose
enforceable half is already `testing.access-only-public-names`. The
family's deeper fault is that three of its rules pull against each
other: a module with a dependency in another process cannot satisfy
`modules.dependencies-are-accepted-not-constructed`,
`modules.internal-seams-stay-inside`, and
`modules.two-adapters-or-no-seam` at the same time.

## Rules

| id | rule | kind | proposed | check | state | overlap | value | note |
|---|---|---|---|---|---|---|---|---|
| `modules.deep-not-shallow` | A module's interface is small against the behaviour behind it: what a caller or a test must learn to use the module is little against the amount of behaviour that use reaches. | stochastic | stochastic | none | breaks | `python.helper-justification` | high | "Small against" fixes no threshold, so depth needs judgment. `registry.kind_by_name` (registry.py:22) has no caller but its own test; `external.py` is one expression with one caller. |
| `modules.internal-seams-stay-inside` | A module's interface exposes no seam — a place where behaviour is altered without editing in that place — that exists only for the module's own tests. | stochastic | stochastic | none | breaks | `modules.two-adapters-or-no-seam` | high | Naming a seam needs judgment. `runner`, `render`, and `list_rules` sit on public signatures and no production caller passes any of them. The overlap contradicts rather than subsumes. |
| `modules.two-adapters-or-no-seam` | A seam a module presents carries at least two adapters, concrete things that satisfy the interface at that seam; a test's in-memory fake is one. | stochastic | stochastic | none | holds | `modules.internal-seams-stay-inside` | low | Every seam found carries two: `Kind.generate`, `runner`, `ListRules`. Counting a test fake as the second adapter means any seam with a test passes, so no member can break it. |
| `modules.dependencies-are-accepted-not-constructed` | A module takes each of its dependencies as a parameter and constructs none of them in its own body. | stochastic | stochastic | none | breaks | `modules.a-port-at-a-process-boundary` | high | Deciding which imported name is a dependency needs judgment. No module takes its collaborators as parameters; `refresh.refresh` reaches `registry.KINDS` by import. Subsumes the port rule's process-boundary case. |
| `modules.a-port-at-a-process-boundary` | A dependency a module reaches across a process boundary, a service the workspace owns or a third party it does not control, sits behind a port at the module's own interface: the module holds the logic, and the transport that carries the call out of the process satisfies that port. | stochastic | stochastic | none | breaks | `testing.double-at-the-port` | high | Which dependency crosses a process boundary needs judgment. Five modules run `git` inline with no port. The overlap is narrower: it binds a dependency reached over the network. |
| `modules.the-interface-is-the-test-surface` | Every behaviour of a module is reachable through its interface. | stochastic | stochastic | none | breaks | `testing.access-only-public-names` | low | What counts as a behaviour needs judgment. 36 `monkeypatch.setattr` calls reach behaviour no interface offers. The overlap states the test-side half, is deterministic, and is checked. |
| `modules.results-are-returned-not-written` | A module that computes a value returns it and does not mutate the caller's argument to deliver it. | stochastic | deterministic | none | breaks | none | high | Test over every `.py` under `src/`: a function that mutates a name bound by its own signature, `self` and `cls` aside. `_directory_node` fills the caller's `reached` set. |

## Escalations

### `modules.deep-not-shallow` — A module's interface is small against the behaviour behind it

The predicate measures the interface against the behaviour behind it, and
the rule's own why
(Deep, not shallow)
gives the deletion test: deleting a deep module pushes its complexity out
across its callers, where it reappears once per caller; deleting a
pass-through relocates the same code once.

Two members fail that test.

`src/dev_playbook/cloa_viewer/registry.py:22` declares
`kind_by_name(name)`, a four-line loop over `KINDS`, and lists it in
`__all__` at line 17. No module in `src/` or `scripts/` calls it. Its
only callers are `tests/dev_playbook/cloa_viewer/test_registry.py:12`,
`:18`, and `:25`. An interface entry with no caller reaches no behaviour
at all.

`src/dev_playbook/external.py` is 24 lines whose whole interface is
`is_verbatim_doc(frontmatter) -> bool` at line 20, a body of one
comparison. `src/dev_playbook/prose_lint.py:381` is its only caller. The
module's own docstring states the opposite — "the detectors share one
definition" — and
[Decision Record 0011](/docs/decisions/0011-one-registry-for-non-authored-content.md)
created it to hold two predicates read by four detectors. Decision Record
0026 retired the other predicate, `is_externally_managed`, and left one
expression with one caller behind.

Proposal: change the repo, narrowly. Delete `kind_by_name` and
`tests/dev_playbook/cloa_viewer/test_registry.py`, which is dead surface
kept alive by its own test and plainly an oversight rather than a design
choice — nothing outside the test tree has ever called it. Leave
`external.py` where it is: Decision Record 0011 makes that file the one
declared place the exclusion is written, and folding it back into
`prose_lint` would need a superseding record, so whether the predicate
should carve out a module that exists to hold one decision is a question
for the design pass, not a fix.

### `modules.internal-seams-stay-inside` — A module's interface exposes no seam that exists only for the module's own tests

The predicate forbids a seam on the interface that exists only for the
module's own tests. Three modules carry exactly such a seam, and carry it
on purpose.

`src/dev_playbook/transcript_export/client.py:60` takes
`runner: Callable = subprocess.run`, and the parameter is repeated on
every public entry point of the package: `session_list` (client.py:93),
`session_search` (client.py:133), `session_get` (client.py:148),
`session_messages` (client.py:156), `render_session`
(transcript.py:44), `select_session_ids` (cli.py:151), and `main`
(cli.py:171), which also takes `render: Callable = render_session` at
line 172. The one production caller,
`scripts/transcript-export:20`, calls `main(sys.argv[1:])` and passes
neither. The module docstring at client.py:7 states the intent plainly:
"tested with an injected fake runner".

`src/dev_playbook/verifier_table.py:320` and `:427` take
`list_rules: ListRules = list_rules_via_subprocess`. The production path
at verifier_table.py:497 passes the default; only
`tests/dev_playbook/test_verifier_table.py` passes anything else, through
`fake_list_rules` at line 53.

Proposal: rewrite the predicate. The repo lifts these seams onto the
interface deliberately, so that the logic around a call into another
process can be tested without that process, and the rule as written
condemns the practice while
`modules.two-adapters-or-no-seam` blesses it in the same Standard. The
new sentence: "A module's interface exposes a seam only where that seam
is the module's port at a process boundary; every other seam the module's
own tests reach stays inside the implementation." That keeps `runner` and
`list_rules` legal, keeps a test-only seam over pure computation illegal,
and ends the contradiction between the two rules.

### `modules.dependencies-are-accepted-not-constructed` — A module takes each of its dependencies as a parameter and constructs none of them in its own body

The predicate has two halves, and the first half is false of every module
in the source: no module takes its collaborators as parameters. Each
reaches them by import.

`src/dev_playbook/cloa_viewer/refresh.py:89`, `refresh(checkout)`, reads
the kinds from `registry.KINDS`, imported at refresh.py:23. There is no
parameter for them, which is why
`tests/dev_playbook/cloa_viewer/test_refresh.py:98`, `:117`, `:131`, and
`:143` must replace the module attribute to test a failing generator.
`src/dev_playbook/verifier_table.py` and
`src/dev_playbook/boundary_table.py` reach their roster the same way,
through a module-level `DETECTORS`, and
`tests/dev_playbook/test_verifier_table.py:87` and
`tests/dev_playbook/test_boundary_table.py:67` replace it the same way.
`src/dev_playbook/playbook_lint.py:46` and `:47` are a third instance.

The second half fails too. `src/dev_playbook/gitrepo.py:105`,
`src/dev_playbook/md.py:326`, and `src/dev_playbook/pyast.py:53` each
build the same `git ls-files --cached --others --exclude-standard -z`
call inside their own bodies, differing only in the filter applied to the
result.

Proposal: rewrite the predicate. Importing a collaborator that never
varies is what every module in the workspace does, and the fault the rule
means is `new StripeGateway()` inside a body, which is construction, not
import. The new sentence: "A module constructs none of
its dependencies in its own body: a dependency whose behaviour a caller
or a test must vary is a parameter, and one that never varies is
imported." That still condemns the three inline `git ls-files` calls and
the module-level rosters the tests have to patch, and stops condemning
`from dev_playbook import md`.

### `modules.a-port-at-a-process-boundary` — A dependency a module reaches across a process boundary sits behind a port at the module's own interface

The predicate binds any dependency reached across a process boundary,
"a service the workspace owns or a third party it does not control". The
`git` binary is a third party the workspace does not control, and every
call to it crosses a process boundary, so the predicate reaches five
modules that put no port on their interface:

- `src/dev_playbook/gitrepo.py:38`, `:78`, `:105`
- `src/dev_playbook/cloa_viewer/state.py:68`, reached by
  `head_commit` and `branch_name`
- `src/dev_playbook/cloa_viewer/discover.py:52`
- `src/dev_playbook/md.py:326`
- `src/dev_playbook/pyast.py:53`

`src/dev_playbook/playbook_lint.py:94` is the same shape over a different
third party: it spawns each detector as its own process with no port.
The source holds exactly one port, `ListRules` at
`src/dev_playbook/verifier_table.py:134`, and the tests for the git
modules use a real git checkout in `tmp_path` rather than a double.

Proposal: rewrite the predicate to name the network, not the process.
`testing.double-at-the-port` already binds only a dependency the code
"reaches over the network", so the two Standards disagree today about
where a port is required, and the repo obeys the narrower one on
purpose — running real git in a temporary checkout is cheap and
deterministic, which `testing.the-lightest-double` asks for. The new
sentence: "A dependency a module reaches over the network, a service the
workspace owns or a third party it does not control, sits behind a port
at the module's own interface: the module holds the logic, and the
transport that carries the call out of the process satisfies that port."
Under that sentence the only remaining member is the `agentsview` CLI,
which `transcript_export.client` already fronts.

### `modules.the-interface-is-the-test-surface` — Every behaviour of a module is reachable through its interface

The predicate says every behaviour is reachable through the interface,
and the remedy it implies is that the interface is redrawn until the
behaviour is reachable. The test tree holds 36 `monkeypatch.setattr` calls, and each
one names a behaviour the interface does not offer:

- `tests/dev_playbook/cloa_viewer/test_refresh.py:98` replaces
  `registry.KINDS`, because `refresh.refresh` offers no way to choose the
  kinds.
- `tests/dev_playbook/test_boundary_table.py:67`, `:68`, `:69` replace
  `DETECTORS`, `UNGATED_AUDITS`, and `DEPENDENCY_RULES`.
- `tests/dev_playbook/test_playbook_lint.py:46` and `:47` replace
  `SCRIPTS_DIR` and `DETECTORS`.
- `tests/dev_playbook/test_label_scheme.py:136` replaces `SCHEME_PATH`.
- `tests/dev_playbook/test_bump_pin.py:84` replaces `GATE`.
- `tests/test_transcript_export_subagent.py:336` replaces
  `transcript._render_body`, a private name, which
  `testing.access-only-public-names` forbids; the detector misses it
  because the name is a string argument rather than an attribute access,
  so `src/dev_playbook/testing_lint.py:187` never sees it.

Proposal: delete the predicate. Its value is low: the module-side half is
near-tautological, since a behaviour no interface reaches is by
definition dead, and the half that can be acted on is already
`testing.access-only-public-names`, which is deterministic, checked by
`scripts/testing-lint`, and gated at commit, push, and ci. What the
deletion would lose is the instruction to redraw the interface rather
than reach past it, and that sentence belongs in the why of
The interface is the test surface.

### `modules.results-are-returned-not-written` — A module that computes a value returns it and does not mutate the caller's argument to deliver it

`src/dev_playbook/cloa_viewer/kinds/index_tree.py:121` declares
`_directory_node(checkout, identity, tracked, reached, repo)`. It returns
the directory node, and it delivers a second result by filling the
caller's set: `reached.add(index)` at line 142 and `reached.add(child)`
at line 156. Its own docstring at line 127 states the arrangement —
"`reached` collects every identity the walk touches" — and the caller
reads the result back: `generate` creates the set at line 173, passes it
at line 175, and computes `left_over = sorted(tracked - reached)` at line
177. The set is the caller's argument, and the mutation is how the value
is delivered.

`src/dev_playbook/cloa_viewer/server.py:186`, `rescan(app)`, is the
second instance and the plainer one: line 218 writes
`app.state.checkouts = found` and line 219 returns the same list, so one
value leaves by both routes. Lines 210 and 214 fill and drain
`app.state.watchers` in the same way.

The kind is wrong as well. The predicate is decidable by a script that
reads only repo files: parse each `.py` under `src/`, and for each
function flag a mutating method call, an item assignment, or an attribute
assignment whose target is a name bound by that function's own
signature, with `self` and `cls` excluded. The second sentence's
carve-out — a module that writes a file, sends a message, or stores a
record — touches nothing bound by the signature, so it costs the script
no judgment. A 40-line scan of that shape over `src/dev_playbook/` found
the `index_tree` case and nothing else but `__init__` assignments to
`self`.

Proposal: change the repo. The predicate states something the repo
plainly wants, the rest of the source obeys it, and both breaches are
small and local: `_directory_node` returns `(node, reached)` and
`generate` unions the sets, and `rescan` drops the assignment at
server.py:218, since `_lifespan` and `checkout_list` can take the
returned list. Reclassify the trailer to deterministic at the same time
and give the id a row in `standards/verifiers.yaml` pointing at
`scripts/python-lint`, which already owns the AST pass over `src/`.

## Detectors

No detector decides any rule of this family. Every `modules.` row of
`standards/verifiers.yaml` is null, at lines 163 to 169, and no code
under `scripts/` or `src/dev_playbook/` emits a string beginning
`modules.`. Two neighbouring detectors were read because the family's
rules overlap theirs:

- `scripts/testing-lint`, a thin shim over
  `src/dev_playbook/testing_lint.py`, decides
  `testing.access-only-public-names`, the checked half of
  `modules.the-interface-is-the-test-surface`. `check_no_private_access`
  at testing_lint.py:89 walks each test file's AST and flags an import of
  a private name, a private segment of an imported module path, and an
  attribute access on an imported name whose attribute begins with one
  underscore. It sees no private name that reaches a module through a
  string, so `monkeypatch.setattr(transcript, "_render_body", ...)`
  passes it. Its tests are `tests/dev_playbook/test_testing_lint.py`.
- `scripts/python-lint` decides two rules,
  `python.no-future-annotations` (`check_no_future`, line 94) and
  `python.empty-init` (`check_empty_init`, line 108). It holds both
  checks in the script rather than in the package, and reaches
  `src/dev_playbook/pyast.py` only for the file list and the parsed AST.
  That AST pass over every `.py` file under `src/` is the surface a
  deterministic `modules.results-are-returned-not-written` would need.
  `python.helper-justification`, in the same Standard, is the
  function-scale case of `modules.deep-not-shallow`.

`standards/boundaries.yaml` names no address for this family, which
follows: an address appears there only once the verifier table names it.

## Acronyms

- **AST** — Abstract Syntax Tree.
- **CLI** — Command-Line Interface.
