---
type: Instrument-Spec
title: The File Graph
description: The file graph — a total, typed map of every file in a repository and the references connecting them
---

# The File Graph

A file graph is a typed graph over one repository: every file is a node in
exactly one bucket, and every detected reference between files is a typed
edge. It exists to answer connectivity questions — which files a reader
starting from a given entry point can reach and at what distance, which
files are orphaned, and how the documented core relates to the code and
configuration around it.

The graph is **total**: pointed at any repository, it accounts for every
file, throwaway included. Totality is the invariant that makes absence
meaningful — a file missing from every connected view is a finding, not a
gap in the instrument.

## Inputs

The caller supplies the repository root. Optionally:

- a **seed set** for the reachability query; the default is the
  `harness-session` bucket.
- a set of **exclusion prefixes** — path prefixes whose in-scope files, and
  every edge touching them, are dropped before the queries run. Exclusions
  remove scaffolding that would only add noise: a vendored bundle that spawns
  hundreds of spurious `code-ref` edges, or the graph's own prior output. The
  dropped files are counted per prefix — an `excluded` tally beside the
  ignored census — so a narrowed graph still reports what it left out and
  totality survives the filter.

## Node accounting

Two grains:

- **Ignored files** — everything `.gitignore` excludes — are accounted in
  aggregate: a count per ignore pattern, no individual nodes. They are
  throwaway by declaration; the graph proves they were seen, not what they
  contain.
- **In-scope files** — everything `git ls-files --cached --others
  --exclude-standard` returns — are individual nodes, each assigned one
  bucket by the first matching test:

| Bucket | Test |
|---|---|
| `concept` | prose `.md` carrying OKF frontmatter — the type-lint set ([bundle.md](/standards/docs/bundle.md)) |
| `index` | an `index.md` directory listing |
| `harness-session` | markdown injected into agent context at session start: `CLAUDE.md` at any level, `rules/*.md` |
| `harness-skill-authored` | a first-party skill bundle member — `SKILL.md` plus everything in its skill directory |
| `harness-skill-thirdparty` | anything under an externally-managed install tree (`.agents/`) |
| `reading` | an instrument's output artifact under `readings/` |
| `code` | a file run as code: `*.py`, `*.sh`, `*.js`, executables, hooks |
| `config` | a file read as configuration: settings, manifests, lockfiles, canonical templates |
| `unclassified` | the residual that guarantees totality; a nonzero count is a finding |

The three `harness-` buckets are one family — files the Claude Code
harness loads into agent context — subdivided by origin and load time:
injected every session, versus loaded on skill invocation from first-party
or third-party trees.

The bucket tests follow the concept/harness boundary
([bundle.md](/standards/docs/bundle.md)) and the harness-file registry
([files.md](/standards/claude-code/files.md)); the reference encoding is
`classify()` in [md.py](/src/dev_playbook/md.py).

## Edge accounting

A directed edge records source file, target, form, line, and status
(`ok`, `broken`, or `wrong-form`, per `ref-lint`). Targets outside the
repository (`~/workspace/<other-repo>/…`) become boundary nodes; URLs are
not edges.

| Form | Detection |
|---|---|
| `link` | root-absolute markdown link, per [cross-references.md](/standards/docs/cross-references.md) |
| `citation` | `~/workspace/…` reference, in-link or bare |
| `resource` | frontmatter `resource:` pointer ([document-types.md](/standards/docs/document-types.md)) |
| `relative` | relative markdown link — outside the reference grammar, still an edge |
| `prose-path` | a path-shaped token in markdown that the grammar treats as prose — inline code spans, fenced blocks — resolving to an in-scope file |
| `code-ref` | a path-shaped token in a non-markdown file that resolves to an in-scope file |
| `bundle` | structural containment: `SKILL.md` to each member of its skill directory |

Formal forms (`link`, `citation`, `resource`) follow the workspace
reference grammar exactly — fenced code blocks and inline code spans are
not scanned for them. `prose-path` and `code-ref` are heuristic by nature;
the spec requires only that a reported edge resolve to a real in-scope
file. `prose-path` exists because a reading agent follows a backticked
path as readily as a link — reachability without it misses real routes.

## Queries

The graph answers these; the artifact renders them:

- **Census** — node counts by bucket; edge counts by form and status.
- **Reachability** — breadth-first from the seed set along markdown edges:
  every reached file with its hop distance, and every unreached file by
  bucket. This is the instrument's motivating query: what can an agent
  reading only the injected context eventually reach?
- **Components** — connected components of the `concept` + `index`
  subgraph over formal edges; a fragmented bundle is a finding.
- **Orphans** — in-scope files with no edges at all, by bucket.
- **Defects** — every `broken` or `wrong-form` edge.

## Executor and artifact

The executor is deterministic code; no LLM judgment participates in graph
construction. The reference implementation is `dev_playbook.filegraph`
behind the [file-graph](/scripts/file-graph) script. The machine layer of
the artifact is one JSON document — nodes, edges, ignored-pattern counts,
and query results as separate keys — rebuilt in full each time the tool is
run, never patched incrementally and never hand-edited.

The user-facing layer over that JSON is an interactive visualization: a
force-directed graph coloring nodes by bucket or by reach distance from the
root `CLAUDE.md`, encoding each file's family as its shape, with search,
shortest-path tracing between two files, and in-place reading of any file's
source. Like the datasheet it is a single self-contained HTML file that
renders from `file://` with no external requests; unlike the datasheet its
form is not yet pinned to a normative example.

Both layers land under `readings/file-graph/<subject>.{json,html}`,
regenerated manually on demand — never hand-edited, and free to lag the
repository until someone rebuilds them.

## Employed by

[System Legibility](/standards/legibility.md) — the standard whose Define cell
claims the file graph as its answer to how a reader sees the connectivity of a
repository without crawling it in full. File graphs are rebuilt on demand;
System Legibility sets no cadence.
