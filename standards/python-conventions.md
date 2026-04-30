# Python Conventions

Default Python conventions for projects in this workspace. Individual
projects may supercede.

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
