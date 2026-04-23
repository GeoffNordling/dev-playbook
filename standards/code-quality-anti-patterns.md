# Code Quality Anti-Patterns

Claude naturally loves these anti-patterns. We catalog the anti-patterns here and run a proactive
agentic sweep against the catalog as part of the PR workflow, so each pattern
is caught before it accumulates.

The authoritative tool is
`~/workspace/dev-playbook/dotfiles/.claude/skills/code-quality-sweep/SKILL.md`.

Each entry below names the anti-pattern, describes what to look for, and states
the rule the sweep enforces. Entries SHOULD stay small and specific — one
pattern per entry.

## Non-blank `__init__.py`

**Pattern.** A Python package's `__init__.py` contains any non-whitespace
content — module docstring, imports, re-exports, `__all__`, anything.

**Why it's wrong.** See
`~/workspace/dev-playbook/standards/python-conventions.md`. Blank
`__init__.py` files have no import-time side effects, surface the true source
of every name, and avoid circular-import traps.

**Rule.** Any `__init__.py` with non-whitespace content is a defect.

## Unjustified defensive fallback

**Pattern.** Code handles a missing, absent, or failed value by silently
substituting a default, rather than failing loudly. Typical shapes:

- `dict.get(key, default)` where `key` is always expected to be present
- `if x is None: return default` (or `x or default`) guarding a value that
  should always exist
- `try: ... except Exception: return default` swallowing errors into a
  sentinel
- `getattr(obj, "attr", default)` for an attribute the object is required to
  have
- Default parameter values that paper over state the caller should always
  supply

**Why it's wrong.** A fallback is only appropriate when the missing value is
a legitimate runtime state, not a programming error. If the thing is required
and always expected to be there, the code SHALL fail fast and loud, not
substitute a default.

Some fallbacks *are* intentional. The anti-pattern is not
defensive code in general; the anti-pattern is defensive code that Claude
added as a reflex, without deciding whether the missing state is legitimate.

**Rule.** Every defensive fallback SHALL have an inline comment explaining
*why* the fallback is intentional — specifically, what condition makes the
missing value a legitimate runtime state rather than a code smell. A
defensive fallback without such a comment is a defect.

**Sweep behavior.** The sweep flags defensive fallbacks without an
explanatory inline comment. It does NOT add comments to justify the
fallbacks. That judgment — remove the fallback or justify it — belongs to a
human. Silent comment-adding would destroy the signal the rule is designed
to create.
