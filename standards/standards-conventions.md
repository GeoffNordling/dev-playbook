# Standards Conventions

How standards files in `standards/` are written.

## Voice

Playbook voice: declarative present tense, like "The symlink is relative."

## Structure

Each rule lives in the lead sentence of its section. If the lead carries the rule, the section can stop there. Section size matches topic size — concepts get sections.

Lead with the edge case in scope when a rule has surprising reach: "These conventions apply to every Python sub-project, including script-only ones with no `src/`."

## Point at canonical artifacts

If a real file IS the standard, the doc directs the reader to it. The canonical pre-commit hook set is `.pre-commit-config.yaml`; `build-conventions.md` says so and points there.

## Trust the reader

Write for someone careful enough to follow a single sentence. State each rule once, in one place, and let it stand.

## Brevity

Choose brevity over completeness. A doc that's read beats a doc that's complete. Trim further than your instinct says.
