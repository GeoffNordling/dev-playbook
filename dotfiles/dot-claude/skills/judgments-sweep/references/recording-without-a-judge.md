# Recording a pass without a judge

You run the `record` commands, but you never choose what goes in them — the
workflow builds each from the ids its judges actually passed, and you copy them
verbatim. There are exactly two exceptions where you name an id yourself, both of
which require the user present in the loop, and both done with one command that
runs from anywhere:

```
uv run judgments-run --root <root> record <id>
```

## The two cases

- **A false positive the user concurs is wrong.** The artifact is correct, the judge
  tripped anyway, and the user agrees. Record the pass on the unchanged content
  rather than re-running a judge that will trip again. This is the deliberate
  "no need to rerun the judge" path.
- **A small edit the user watched you make.** They asked for it, or they saw the
  wording and agreed. A second opinion on a clause the user just approved buys
  nothing they have not already supplied, and the round trip costs a full judge run.

## The limits

Scope this tightly. It is for **minor** edits — a reworded clause, a tightened table
cell, a corrected name — where the fix is obvious and the judge's own `opinion` named
it. A new section, a changed rule, or a claim that now asserts something different
goes back through a judge.

**An autonomous run never does either of these.** With no user present there is no
concurrence to rely on, so a suspected false positive is set aside for the user
instead of self-cleared, and any edit made without the user watching is re-judged.

Whenever you take this path, say so plainly in your report: name the judgment, name
the edit, and state that the judgment was marked passing on content no judge has
read.
