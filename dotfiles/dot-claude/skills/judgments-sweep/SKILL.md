---
name: judgments-sweep
description: Sweep judgment declarations across one, several, or all judgment-bearing repos — plan one docket, judge it in one fan-out, record the passes, weigh the refutations. Use when the user asks to run, sweep, or refresh the judgments, whether or not they name repos.
disable-model-invocation: false
model: opus
effort: xhigh
arguments: [roots]
---

# Judgments Sweep

A **judgment** is a specific yes/no question about specific files, ruled on by an
LLM judge, declared as YAML and keyed by content: editing a claim or a file it
puts on trial re-keys it, and a machine-shared cache remembers what has been
judged-and-passed. A sweep judges whatever has drifted out of that cache.
{Read [declaration format](~/workspace/dev-playbook/standards/semantic-validation/declarations.md)}.

Steps 1–3 below are mechanical: run a command, pass its output on untouched, run
the commands you get back. **Copy, never compose** — each hand-off is one opaque
string, and reading, summarizing, or editing it is how this goes wrong. Your
judgment is spent on step 4 and nowhere else: **weighing each refutation and
making the fixes it warrants.**

## The roots

The sweep is parameterized by repo roots — one repo, several, or all of them:

- **Roots named** (as arguments or in the user's ask): sweep exactly those.
  A worktree counts as its own root; if you are standing in one and the user
  means "this repo", that worktree is the root.
- **Bare invocation**: sweep every judgment-bearing repo on the machine. Discover
  them deterministically (one line):

  ```
  grep -l -s '^\[tool\.judgments\]' ~/workspace/*/pyproject.toml | xargs -n1 dirname
  ```

## The loop

### 1. Plan

{Run [judgments-run](/scripts/judgments-run) in `plan` mode}:

```
uv run judgments-run --root <root> [--root <root> …] plan
```

One `--root` per swept repo, each before the `plan` subcommand. It prints one line
of JSON: the workflow's complete argument payload for every root at once, keyed
against the shared cache, filtered, and ready. A bulk sweep is this same single
command — never a per-repo loop.

The one thing you read in it is `jobs`. **`"jobs": []` ends the loop** — every
judgment everywhere is either cached or set aside, and there is nothing to
dispatch. Otherwise the whole line goes to step 2 untouched.

### 2. Judge

```js
Workflow({ name: "judgments", args: <the JSON from step 1, verbatim> })
```

That JSON becomes the `args` value itself — an object in the tool call, not a
quoted string wrapping one. Change nothing inside it.

The result arrives inline in the workflow's task notification. If you instead open
the task's output file, that file is a wrapper — the workflow's own return value is
under its top-level **`result`** key, not at the top level.

```json
{ "record": ["/…/python -m … --root /…/repo-a record id-a"],
  "roots": { "/…/repo-a": {"cached": 25}, "/…/repo-b": {"cached": 16} },
  "ran": 3,
  "passed": [ {"id": "id-a", "root": "/…/repo-a"} ],
  "refuted": [ {"id": "id-b", "root": "/…/repo-b", "opinion": "…what to fix…"} ],
  "crashed": [], "skipped": [], "green": false }
```

### 3. Record

`record` is a list of complete shell commands, one per root with passes. {Write
the judgment cache; run each `record` command verbatim}. An empty list means
nothing passed — then there is nothing to run. If one fails, the copy was
mangled: each command records all or nothing, so copy it again exactly rather
than retyping it or dropping an id.

Do this before anything else. Until it runs, the verdicts exist only in that
result, and a re-plan will re-judge everything that passed.

### 4. Weigh each refutation, then act

`refuted` is the only field that needs a mind. `green` means nothing in this run
does. Each entry names its `root` — weigh it against that repo, and make any fix
there.

A **crash is not a verdict** — that judgment was never ruled on, stays uncached,
and is picked up by looping again; no fix, no attempt consumed. Twice
running is an environment problem: set it aside and say so.

**Investigate, don't comply.** A refuted verdict is *one low-intelligence,
stochastic judge's claim, not a proven defect*. We run these judges constantly and
will get false positives; you are the more careful reader. Weigh the `opinion`
from first principles against the repo's own rules and the adjacent artifacts,
with the standing default that **the artifact is correct as written** — overturning
it takes genuinely convincing evidence, and the burden is on the judge, not the
text. Then act on what you find:

- **the artifact is wrong** — one focused edit (a section, not a rewrite), guided by
  the `opinion`.
- **the claim overstates** — fix the claim to say what is true; never weaken, drop,
  or reword a judgment merely to pass.
- **the judge is wrong** — change *nothing*. Never pad a standard or doc with
  hedging, caveats, or filler to placate a tripped judge: that trades correct prose
  for slop, worse than a wasted judge run. Set it aside for the user.

Limits govern this, and you track them yourself as you loop:

- **Two fix attempts per judgment.** Still refuted after two fixes: set it aside.
- **Focused fixes only.** A refutation needing more than one focused edit is set
  aside, unfixed.

### 5. Loop

Back to step 1, with the same roots. Your edits re-key the judgments you touched,
so the next plan picks up exactly those plus anything that crashed. Name what you
have set aside so it is not re-judged — {Run [judgments-run](/scripts/judgments-run)
again, with a `--skip` per set-aside id} so it is set aside in every swept
root that declares it:

```
uv run judgments-run --root <root> […] plan --skip some-id --skip another-id
```

The loop ends at step 1, when the plan comes back with an empty `jobs`. With the
user present, narrow cases let you record a pass without a judge — a false
positive they concur is wrong, and a small edit they watched you make — both
governed by
[recording-without-a-judge.md](references/recording-without-a-judge.md); an
autonomous run does neither.

**The user is your escalation path — use it, with an example.** They sit at the main
loop for exactly the hard calls: a genuinely ambiguous artifact-vs-judge question, a
refutation you cannot confidently place, a fix larger than focused. Escalate rather
than guess or force a fix. Quote the specific thing at issue — the artifact line as
written, the claim's exact words, the precise mismatch alleged: the user is not
looking at the code, the doc, or the judgment.

## Report

{Report per root: already cached, judged, passed, fixed-then-passed (each
id + the edit made), set aside (each id + its `opinion` or crash history + why),
crashed-and-recovered}.

A repo that tripwires its judgments via pytest arms them with
`make check-judgments-cache` (also the canonical pre-push hook); that target goes
green only when **every** gated judgment is cached, so set-aside judgments keep
it red by design. Default `make check`/`make test` skip the cache check
(`SKIP_JUDGMENTS=1`).
