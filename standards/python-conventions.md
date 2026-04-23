# Python Conventions

The key words "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in [RFC 2119](~/workspace/dev-playbook/sdd-standards/rfc2119.md),
following the vocabulary conventions in
[sdd-standards/extensions.md](~/workspace/dev-playbook/sdd-standards/extensions.md).

These are default Python conventions. Individual projects may supercede.

## Package Initialization

`__init__.py` files SHALL be empty.

Imports, re-exports, `__all__` declarations, and any other code SHALL live in
named modules, not in `__init__.py`. Callers SHALL import from the specific
submodule (`from pkg.sub import thing`), not from the package root.

Rationale: a blank `__init__.py` has no import-time side effects, surfaces the
true source of every name to readers and tooling, and avoids the circular-import
traps that grow with populated package initializers.
