---
type: General-Sheet
title: Shell Family Rule Audit
description: The rule audit over the shell/ family — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---

# Shell Family Rule Audit

The family holds eleven rules, all in
[Shell Conventions](/standards/shell/conventions.md). No reclassification
is proposed in either direction: every trailer already carries the kind
the predicate earns. Four rules break. Two of them,
`shell.executable-scripts` and `shell.sourced-fragments`, are conditions
written as predicates, so read as rules they are false of most of the
population; `shell.glue-only` is false of two of the repo's five
executable scripts; and `shell.bounded-to-shell-integration` is false of
`dotfiles/.bashrc.d/machine-env.sh`, which exports an environment
variable the predicate's list does not admit. No rule is weakly checked,
because there is nothing in between: two rules,
`shell.shellcheck-clean` and `shell.formatting`, are checked in full by
the two pinned third-party hooks, and the other nine are checked by
nothing at all — every one of their verifier rows is null. One rule is
low value: `shell.dialect-directive`, which `shell.bash-declared` and
`shell.no-shebang-no-strict-mode` together already force.

| id | rule | kind | proposed | check | state | overlap | value | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `shell.bash-declared` | "Every shell file declares bash as its dialect, in a shebang that names bash or in a `# shellcheck shell=bash` directive." | deterministic | deterministic | none | holds | `shell.strict-mode` | high | Test: first line matches `#!.*bash`, or a line matches `# shellcheck shell=bash`. All nine shell files pass. strict-mode and dialect-directive each subsume it inside their condition; only this rule binds a file under neither. |
| `shell.shellcheck-clean` | "Every shell file passes shellcheck with no findings." | deterministic | deterministic | full | holds | none | high | The `shellcheck` hook is the predicate: `entry: shellcheck`, no `args`, `types: [shell]`. `make check` and CI run `pre-commit run --all-files`, so every member is checked, not only the staged ones. |
| `shell.disable-carries-a-reason` | "Every `# shellcheck disable=` directive in a shell file carries a same-line comment giving the reason the suppression is safe." | stochastic | stochastic | none | holds | none | high | Vacuous today: no shell file carries a disable directive. The presence of a same-line comment is mechanical, but "giving the reason the suppression is safe" judges the text, so the rule stays stochastic. |
| `shell.formatting` | "A shell file's bytes are what `shfmt` writes from that file with its default options." | deterministic | deterministic | full | holds | none | high | The `shfmt` hook runs `shfmt -w` with no other option, so a file that differs is rewritten and the hook fails. Default options are the bar because the config sets no `args:` override. |
| `shell.executable-scripts` | "The shell file has the executable bit set." | deterministic | deterministic | none | breaks | none | high | A condition written as a predicate. False of all three `.bashrc.d/` fragments (mode 644) and of `dotfiles/dot-claude/skills/diagnosing-bugs/scripts/hitl-loop.template.sh`. |
| `shell.glue-only` | "An executable script wires tools together and nothing more: it defines no function, declares no array, and reads no positional parameter." | deterministic | deterministic | none | breaks | none | high | `dotfiles/dot-claude/hooks/session-start-stale-base:27` defines `note()`; `dotfiles/dot-claude/hooks/play-sound:13` reads `"${1:-}"`. Two of five executable scripts. No array anywhere. |
| `shell.strict-mode` | "An executable script opens with the shebang `#!/usr/bin/env bash`, and its first command is `set -euo pipefail`." | deterministic | deterministic | none | holds | `shell.bash-declared` | high | Test: line 1 equals the shebang; the first non-comment, non-blank line equals `set -euo pipefail`. All five executable scripts pass. Its shebang clause subsumes bash-declared under this condition. |
| `shell.sourced-fragments` | "The shell file is under `.bashrc.d/`." | deterministic | deterministic | none | breaks | none | high | A condition written as a predicate. False of all six shell files outside `dotfiles/.bashrc.d/`, among them every hook under `dotfiles/dot-claude/hooks/`. |
| `shell.no-shebang-no-strict-mode` | "A sourced fragment carries neither a shebang nor `set -euo pipefail`." | deterministic | deterministic | none | holds | none | high | Test: no line 1 `#!`, no `set -euo pipefail` anywhere. All three fragments pass. Nothing else states it, and the fault it forbids kills the parent shell. |
| `shell.dialect-directive` | "A sourced fragment opens with a `# shellcheck shell=bash` directive." | deterministic | deterministic | none | holds | `shell.bash-declared` | low | Derivable: bash-declared forces a shebang or the directive, no-shebang-no-strict-mode forbids the shebang. The only increment is "opens with", the line-1 position. |
| `shell.bounded-to-shell-integration` | "A sourced fragment holds only what mutates the parent shell: directory changes, aliases, and completions." | stochastic | stochastic | none | breaks | none | high | `dotfiles/.bashrc.d/machine-env.sh:9` exports `SKIP`. An export mutates the parent shell, but the list after the colon does not admit it. |

Two rows above are the family's conditions rather than its rules.
`shell.executable-scripts` is the condition `shell.glue-only` and
`shell.strict-mode` hang under; `shell.sourced-fragments` is the
condition the last three rows hang under. Both carry a trailer and hold
a verifier row, which is the house pattern —
[Skeleton](/standards/build/skeleton.md) does the same for
`build.python`, `build.python-package`, `build.python-source`, and
`build.javascript`, and `scripts/verifier-table` reads every trailer
whatever its heading level. What is not the house pattern is their
wording; see the escalations.

The population read for this audit is the nine files pre-commit's
`types: [shell]` identifies in this repo: the three fragments under
`dotfiles/.bashrc.d/`, the three bash hooks under
`dotfiles/dot-claude/hooks/`, `dotfiles/dot-claude/statusline.sh`,
`dotfiles/dot-claude/skills/usage-report/scripts/report.sh`, and
`dotfiles/dot-claude/skills/diagnosing-bugs/scripts/hitl-loop.template.sh`.
Every `scripts/` entry point is Python behind a
`#!/usr/bin/env -S uv run --script` shebang and is no member.

## Escalations

### `shell.executable-scripts` — "The shell file has the executable bit set."

The heading is a condition: it has H3s beneath it, and
[Population and Rules Encoding](/doc-types/standard/encoding.md#conditions)
says an H2 with H3s beneath it is a condition whose first paragraph
"states the membership test". But the sentence is written as a
declarative predicate over the whole population, and read that way it is
false of four of the repo's nine shell files:
`dotfiles/.bashrc.d/aliases.sh`, `dotfiles/.bashrc.d/machine-env.sh`,
`dotfiles/.bashrc.d/worktree.sh`, and
`dotfiles/dot-claude/skills/diagnosing-bugs/scripts/hitl-loop.template.sh`
are all mode 644.

The contrast is
[Skeleton](/standards/build/skeleton.md#python), whose conditions are
noun phrases that cannot be read as predicates: "A repo in which
`pyproject.toml` exists at the root", "A Python repo in which `src/`
exists", "A repo in which `package.json` exists at the root". The shell
family's two conditions are the only ones in the tree written as
sentences with a verb.

The mode bit is also a fragile membership test. `identify`, the library
behind `types: [shell]`, reads a shebang only for a file the extension
does not already tag, so
`dotfiles/dot-claude/skills/diagnosing-bugs/scripts/hitl-loop.template.sh`
enters the population on its `.sh` extension but leaves this condition on
its mode. Its header says "Copy this file, edit the steps below, and run
it", so it is an executable script in intent; it defines `step()` and
`capture()` at lines 20 and 25 and escapes `shell.glue-only` on a mode
bit alone.

Proposal: rewrite. Make the sentence a noun phrase, "A shell file with
the executable bit set.", which matches Skeleton's form and stops a
reader and a future lint from reading a condition as a rule. This is the
cheap way out — one sentence, no repo change — and it changes no
member's classification, because the mode bit is already the test the
H3s below assume.

### `shell.sourced-fragments` — "The shell file is under `.bashrc.d/`."

The same fault as the row above. The heading has three H3s beneath it,
so it is a condition, but the sentence reads as a predicate over every
shell file and is false of six of the nine: the three hooks under
`dotfiles/dot-claude/hooks/`, `dotfiles/dot-claude/statusline.sh`,
`dotfiles/dot-claude/skills/usage-report/scripts/report.sh`, and
`dotfiles/dot-claude/skills/diagnosing-bugs/scripts/hitl-loop.template.sh`.

The path is also written bare. Every fragment in the repo is under
`dotfiles/.bashrc.d/`, a stow source directory that lands at
`~/.bashrc.d/` at runtime, so "under `.bashrc.d/`" names neither a
repo-relative path nor a home-relative one exactly.

Proposal: rewrite. "A shell file in a `.bashrc.d/` directory." This
keeps the noun-phrase form the rest of the tree uses, and the indefinite
"a `.bashrc.d/` directory" covers both the `dotfiles/.bashrc.d/` source
in this repo and the `~/.bashrc.d/` the loader reads, which is what the
rule has always meant.

### `shell.glue-only` — "An executable script wires tools together and nothing more: it defines no function, declares no array, and reads no positional parameter."

The predicate names three faults. One, "declares no array", is true of
every executable script in the repo. The other two are each false of one
script.

`dotfiles/dot-claude/hooks/session-start-stale-base:27` defines a
function:

```bash
note() {
	mkdir -p "${log%/*}"
	printf '%s source=%-8s %-24s %s\n' \
		"$(date -Is)" "$source_event" "${PWD##*/}" "$1" >>"$log"
}
```

The hook calls it on all five of its exit paths (lines 38, 42, 49, 58,
62).
The file's header says the log "is the only evidence a silent-by-design
hook is alive", so the helper exists to make every path log, which is
the opposite of a script that has outgrown shell.

`dotfiles/dot-claude/hooks/play-sound:13` reads a positional parameter:

```bash
case "${1:-}" in
stop)
```

That parameter is wired, not parsed. `dotfiles/dot-claude/settings.json`
invokes the same script twice, at line 123 as `play-sound stop` and at
line 187 as `play-sound notification`. One script serves two events on a
two-word dispatch.

The rule's own why
([Glue only](/standards/shell/conventions.md#glue-only))
states the intent: "A script that reaches for a function, an array, or
argument parsing has outgrown shell: the same work as a Python `scripts/`
shim over `src/` is testable and typed." Neither file has outgrown shell.
Both are
Claude Code hooks stowed into `~/.claude/`, not repo runnables, so the
remedy the explanation names does not reach them: `scripts/` ships uv
entry points that a stowed dotfile cannot import. The repo does write a
hook in Python where the job earns it —
`dotfiles/dot-claude/hooks/measure-event` is stdlib Python 3 for exactly
that reason — so the choice of shell in these two is deliberate, not an
oversight.

Proposal: rewrite. Drop the two clauses the repo contradicts and keep
the one it obeys plus the fault the explanation truly names: "An
executable script wires tools together and nothing more: it declares no
array and parses no options." Two of five executable scripts break the
rule as written, which is too many to call an oversight, and the repo
change — splitting `play-sound` into two scripts, re-wiring two
`settings.json` entries, and rewriting a `git`/`gh`/`jq` wrapper in
Python — costs real clarity and fixes no defect.

### `shell.bounded-to-shell-integration` — "A sourced fragment holds only what mutates the parent shell: directory changes, aliases, and completions."

The predicate lists three kinds of content after its colon, and the list
reads as closed. `dotfiles/.bashrc.d/machine-env.sh` holds none of the
three. Its whole body is lines 7 to 10:

```bash
if grep -qi microsoft /proc/version 2>/dev/null; then
	# The detector announces the skip on every run, so it never goes silent.
	export SKIP="${SKIP:+$SKIP,}ref-lint"
fi
```

An `export` does mutate the parent shell, so the fragment obeys the
clause before the colon and fails the list after it. The file is also
deliberate, and says so at lines 4 to 6: "Detection is duplicated here
rather than calling `dev_playbook.dotfiles.machine`: a sourced fragment
runs on every interactive shell and cannot afford a Python subprocess to
learn one fact." An exported variable is the one thing a child process
cannot hand back to the parent, so it belongs in a fragment for the same
reason `cd` does.

The other two fragments pass. `dotfiles/.bashrc.d/aliases.sh` is eight
aliases. `dotfiles/.bashrc.d/worktree.sh` is `cdwt()`, a directory
change, and `_cdwt()` with its `complete -F` registration, a completion.

Proposal: rewrite. Add the missing kind to the list: "A sourced fragment
holds only what mutates the parent shell: directory changes, aliases,
completions, and exported environment variables." The repo has wanted
this since `machine-env.sh` was written, the list was simply drawn from
`worktree.sh` and `aliases.sh` alone, and an export is as plainly a
parent-shell mutation as the three already named. Changing the repo is
not open here: the export cannot move to a child process, which is the
whole reason the file is a fragment.

## Detectors

No first-party detector decides any rule of this family. Nine of the
eleven verifier rows are null, and the two that are not name pinned
third-party hooks.

**`shellcheck`** decides `shell.shellcheck-clean`. It is the
`shellcheck-py` hook pinned at `v0.11.0.1` in
`.pre-commit-config.yaml`; its manifest gives `entry: shellcheck` with
no `args` and `types: [shell]`, so it runs the tool at its default
severity over every file the population phrase names. The predicate and
the tool are the same thing, which is why the check is full rather than
weak.

**`shfmt`** decides `shell.formatting`. It is the `shfmt-py` hook pinned
at `v4.0.0`; its manifest gives `entry: shfmt` with `args: [-w]` and no
option that changes the format, so the bytes it compares against are the
ones shfmt writes with its defaults, as the predicate says. `-w`
rewrites the file in place, so a file that differs both changes and
fails the hook.

**`scripts/verifier-table`** decides no shell rule but is the only
first-party code that names one. `DEPENDENCY_RULES` in
`src/dev_playbook/verifier_table.py:88-90` maps `shellcheck` to
`shell.shellcheck-clean` and `shfmt` to `shell.formatting`, and
`standard.an-address-exists` makes it fail if either hook id leaves
`.pre-commit-config.yaml`. It also reads every trailer in the family
with `_TRAILER`, whatever the heading level, which is why the two
conditions hold verifier rows beside the nine rules.

Both hooks sit at `commit`, `push`, and `ci` in
`standards/boundaries.yaml`. `make check` and the CI workflow both run
`pre-commit run --all-files`, so at push and in CI the two checked rules
are decided over the whole population, not over the staged files alone.
