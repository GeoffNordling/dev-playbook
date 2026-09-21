---
type: General-Sheet
title: Rule Audit Prompt
description: The prompt one agent loads to audit one Standard family's rules — kind, detector coverage, repo state, and overlap, reported without edits or fixes
---

# Rule audit: one Standard family

You audit the rules of one Standard family in this repo. You report; you
do not fix. The only file you write is your report. You open no GitHub
issue and edit no other file, under `standards/`, `scripts/`, `src/`,
`tests/`, or anywhere.

Your launch message names the family directory, the report path, and
the report's title. Where it names one Standard file instead of a whole
family, audit only that file's rules, but read the whole family.

## What a rule is

A Standard is a markdown file under `standards/` with frontmatter
`type: Standard`. Each heading whose section ends in a trailer line is
one rule: a predicate over one member of the Standard's `population`,
then the trailer
`` `<dir>.<slug>` · deterministic|stochastic ``. The trailer id is the
rule id. `standards/verifiers.yaml` maps every rule id to the script
that decides it, or `null`. `standards/boundaries.yaml` maps each
script to the repos it runs in.

The kinds are defined in `standards/standard/detectors.md` and
`standards/doc-type/standard-conventions.md`. Read both first. In
short: a rule is deterministic when a script that reads only files in
the repo returns one value for a member with no judgment call. It is
stochastic when deciding it needs judgment.

## Read, in this order

1. `standards/standard/detectors.md`, `standards/doc-type/standard-conventions.md`.
2. The family: its `index.md`, every Standard in it, its `explanation.md`.
3. `standards/verifiers.yaml`, the rows for the family's rule ids.
4. For each script named in those rows: the script under `scripts/`,
   the module it imports under `src/dev_playbook/`, and its tests under
   `tests/`. Read the code that emits each rule id. The docs describe
   the detector; the code is the detector. Where they disagree, the
   code wins.
5. A sample of the population: enough real members to answer "does the
   repo obey this rule" for every rule. For a small population, all of
   it.

Do not read `working-docs/doc-type-system/doc-type-system/writing-predicates.md`.
It is unreviewed and not endorsed; decide for yourself.

Do not run the detectors. Every detector passes on this tree today, so
a run tells you nothing. Read the code that emits the rule id and judge
what it tests.

Pseudocode in `doc-types/*/contract-shape.md` is pseudocode, never
Python; do not parse or execute it.

## Answer five questions per rule

1. **Kind.** Could a script that reads only repo files decide this
   predicate with no judgment call? If yes, name the input files and
   the test in one line. If no, say what needs judgment. Answer this
   from the predicate, not from the trailer: a trailer can be wrong in
   either direction.
2. **Check.** Which code decides it today, if any, and does that code
   test the predicate as written?
   - `full`: the code tests what the predicate says.
   - `weak`: the code tests less than the predicate says. Name each
     thing the predicate states that the code does not test.
   - `none`: no code decides it (the verifier row is null, or the code
     under the named address never emits this id).
3. **State.** Does the repo obey the predicate? Check members yourself:
   grep, read, list. Do not assume it holds.
   - `holds`: every member you checked obeys it.
   - `breaks`: a member does not. Name the file and line, or the
     missing thing.
   - `unknown`: you could not decide from the repo. Say why.
   State and check are independent: a weakly checked rule can hold, and
   a fully checked rule can break only if the detector is wrong, which
   you then report.
4. **Overlap.** Does another rule, in this family or elsewhere under
   `standards/`, state the same thing or a superset of it? Name the id
   and say which subsumes which. `none` otherwise.
5. **Value.** Would the repo lose anything if this rule were deleted?
   `high` when a reader or a script needs it and nothing else states
   it. `low` when it restates another rule, forbids a fault nobody
   would commit, or binds something too small to matter. There is no
   credit for rule count: a weak rule costs a reader's attention and a
   verifier's row and returns nothing.

## Report format

Write the report as one markdown file at the path given. It opens
with this frontmatter, the family or Standard name filled in:

```
---
type: General-Sheet
title: <the title the launch message gives>
description: The rule audit over the <dir>/ family — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---
```

After the frontmatter the report has:

1. A one-paragraph summary: how many rules, how many you propose to
   reclassify in each direction, how many break, how many weak, how
   many low value.
2. One table, one row per rule, in file order, columns exactly:

   | id | rule | kind | proposed | check | state | overlap | value | note |

   `rule` is the predicate's first sentence, quoted verbatim from the
   Standard, so a reader who has not memorized the Standard knows what
   the row is about. `kind` is the trailer today. `proposed` is your answer to question 1,
   `deterministic` or `stochastic`. `check` is `full`, `weak`, or
   `none`. `state` is `holds`, `breaks`, or `unknown`. `overlap` is a
   rule id or `none`. `value` is `high` or `low`. `note` holds the specifics: the test a script
   would run, the things a weak check misses, the breaking file and
   line, the reason for `unknown`. Keep each note under 40 words; put
   anything longer in the section below.
3. A section `## Escalations` with one H3 per `breaks` row and per
   `weak` row. The H3 heading is the rule id followed by the predicate's
   first sentence, so the heading alone says what the rule asks. The
   body gives the evidence: the predicate's words, what the
   repo or the code does instead, and the file paths and lines. A
   `breaks` escalation ends with a `Proposal` paragraph: which of the
   three ways out you recommend and why, in two or three sentences.
   The three are: rewrite the predicate so it states what the repo
   does on purpose, change the repo to obey the predicate, or delete
   the predicate. For a rewrite, give the new sentence. For a repo
   change, name the files that change. For a delete, say what, if
   anything, still states the intent. The user decides; you recommend.
   Be wary of recommending a repo change: it is the expensive way out,
   and the repo's current state is usually deliberate. Recommend it
   only when the predicate states something the repo plainly wants and
   the state is an oversight, and say what makes you sure. Where the
   rule's value is `low`, delete is the default recommendation.
4. A section `## Detectors` naming each script you read and what its
   code decides, in two or three sentences each, so the design pass can
   see the family's checking surface in one place.

Use the rule ids exactly as the trailers spell them. Do not invent ids.
Make no fix yourself; a proposal is a recommendation, and the user
decides.
