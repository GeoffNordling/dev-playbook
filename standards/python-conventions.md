# Python Conventions

Default Python conventions for projects in this workspace. Individual
projects may supercede.

For build/task-runner conventions (Makefile targets, `make check`), see
[build-conventions.md](build-conventions.md).

## Package Initialization

`__init__.py` files are empty.

Imports, re-exports, `__all__` declarations, and any other code live in named
modules, not in `__init__.py`. Callers import from the specific submodule
(`from pkg.sub import thing`), not from the package root.

Rationale: a blank `__init__.py` has no import-time side effects, surfaces the
true source of every name to readers and tooling, and avoids the
circular-import traps that grow with populated package initializers.

## Docstrings

Every function, method, class, and module has a docstring. The docstring
explains in plain English what the thing does. One short sentence is fine
when the behavior is simple; longer when it isn't.

Rationale: a name tells you what something is called; a docstring tells you
what it does. Readers (human and agent) should not have to read the body to
learn the contract.

**Exception: tests.** Pytest test functions follow a `test_<behavior>` naming
convention literal enough that a docstring would just restate the name. Skip
docstrings on test functions. Test-module-level helpers (factories, fixtures
defined as plain functions) still need docstrings — their names are not
similarly load-bearing.

## Fail Loudly

When a value is required for the code to do its job, missing it is a bug —
the code raises rather than substituting a default. This applies to all the
usual shapes that quietly hide a missing value:

- `dict.get(key, default)` where `key` is always expected to be present —
  use `dict[key]` and let the `KeyError` surface.
- `if x is None: return default` (or `x or default`) guarding a value that
  should always exist.
- `try: ... except Exception: return default` swallowing errors into a
  sentinel.
- `getattr(obj, "attr", default)` for an attribute the object is required to
  have — use `obj.attr`.
- Default parameter values that paper over state the caller should always
  supply.

Some fallbacks are legitimate — the missing value is a real runtime state,
not a programming error. When that's the case, leave an inline comment
explaining *why* the fallback is intentional. The comment is the signal that
the author thought about it.

Rationale: a fallback that hides a bug delays the failure to a place far
from the cause, where it's much harder to diagnose. Failing at the point of
the missing value points straight at the defect.

## Module Layout

A module's top-level statements appear in this order:

1. The module docstring.
2. `import` and `from ... import` statements.
3. Plain-literal module constants (`UPPER_SNAKE_CASE` names whose values
   are literals, tuples of literals, or `re.compile(...)` patterns).
   Includes `_PRIVATE` constants.
4. Type aliases, dataclasses, classes, and functions, interleaved with
   *derived* constants — module-level `UPPER_SNAKE_CASE` names whose
   values depend on a class, function, or enum defined in the file.
   A derived constant goes immediately after the things it derives from,
   in a labeled section.

Don't define a constant next to its first user mid-file. Single-use
constants still go at the top (or, for derived ones, in their grouped
section near their dependencies) — never floating above one function.

Rationale: a reader scanning a new module wants to find its dependencies and
its tunable values without searching. Mixing constants into the body of the
file hides them — a reader who doesn't already know the constant exists
won't think to look for it past the first `def`. The cost of putting every
constant at the top is one scroll; the cost of hiding one is a bug that
slips past review because nobody saw it.

## Future Imports

Do not add `from __future__ import …` to a file without explicit human
approval. This applies to every name in `__future__`, including
`annotations`.

Most workspace projects target Python 3.11+, where the common future
imports either do nothing (`generator_stop`, `division`, etc.) or change
parse-time behavior in subtle ways (`annotations` → PEP 563 deferred
evaluation). Agents add them reflexively as boilerplate; the import then
costs one line forever and signals "this file relies on PEP-X" when it
usually doesn't.

Linters can't catch this. `F401` (unused-import) has a hardcoded
carve-out for `__future__`, and `UP010` only fires when the import is
*redundant for the target Python version* — not when it's defensible
but pointless for this specific file. The judgment is human.

If a future import is genuinely needed (e.g. a forward reference that
would be a runtime error without `annotations`), the author asks the
human and notes the reason at the import site.

## Helpers

A helper function earns its place by doing one of these:

- **Multi-use**: called from two or more sites. De-duplication is the
  clearest justification.
- **Substantial body**: the logic is long or intricate enough that lifting
  it out makes the caller readable. A 1–2 line helper called once is
  almost always pure relocation; inline it.
- **Distinct concern at a different abstraction level**: the helper's job
  belongs to a different layer than its caller (e.g., a regex-based
  enforcement check inside a high-level dispatch loop). The name then
  documents the layer boundary.
- **Architectural pluggability**: an entry in a dispatch table, registry,
  or strategy map. These look "single-use" by static call count but are
  pluggable by design.

A helper does **not** earn its place from:

- "Symmetry with siblings" alone — three functions of the same shape, where
  one is single-use and trivial, is not a reason to keep the trivial one.
  Justify each on its own merits.
- "It already existed" — the bar is the same for new helpers and for
  helpers inherited from earlier work.
- Speculative reuse — extract when the second caller appears, not in
  anticipation of one.

When a helper does earn its place, put it directly under the function that
uses it (or, for helpers shared by several functions, in a clearly labeled
section). Group related helpers into sections with a `# ---` banner so a
reader can navigate by concern, not by call graph.

Rationale: every helper costs the reader a jump. Helpers that genuinely
encapsulate a concept pay that cost back; helpers that just relocate a few
lines don't. Pinning the "earns its place" criteria explicitly keeps
review consistent — without them, "should this be extracted?" becomes a
matter of taste, and codebases drift toward over-factored or
under-factored extremes depending on who reviewed last.
