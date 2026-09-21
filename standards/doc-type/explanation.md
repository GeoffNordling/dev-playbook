---
type: Explanation
title: Doc-Type Explanation
description: The thinking behind the doc-type Standards — the reasons behind the rules a Standard's, a runbook's, and a loop's file each obey; Doc-Type's own rules carry their why beside them
---

# Doc-Type Explanation

The reasoning behind the four Standards in this directory:
[Doc-Type](/standards/doc-type/doc-type.md), which every doc-type is
held to, and the three that bind the files typed by a doc-type,
[Standard Conventions](/standards/doc-type/standard-conventions.md),
[Runbook Conventions](/standards/doc-type/runbook-conventions.md), and
[Loop Conventions](/standards/doc-type/loop-conventions.md). Where a
file sits is the family's Standard's, not these: the `standards/` tree
is [The Standards Tree](/standards/standard/tree.md), a runbook's roots
are [Claude Code Files](/standards/harness/files.md#location), and a
typed document's home is
[Document Types](/standards/knowledge-organization/document-types.md).

## A Standard's file

The rule id's trailer is what the verifier table reads
([The verifier table](/standards/standard/detectors.md#the-verifier-table)),
so a rule without one is a rule no table row can name. The population
is one frontmatter phrase because a verifier, and a reader, must know
the class before the first rule. A predicate that compares two
members, or asks for taste, is one no verifier, script or judge,
returns one value for, which is why each is decidable of one member at
one moment.

### The rule shape

The first paragraph is the predicate every member is held to; the
block or table is the target state it compares against. An H2 without
a trailer is a condition: it names which members the rules under it
bind
([The rule shape](/standards/doc-type/standard-conventions.md#the-rule-shape)).

### What a rule may state

The principles a rule is admitted or refused by. A rule audit reads
them beside the rules they explain.

**A predicate is a test over state.** It is decided from the bytes of
the repo at one commit, by reading them or by a pure function of them
such as a formatter. It is not a test over run-time behaviour, what a
script exits or prints; not an instruction to an author, where a
helper sits or which double a test uses; not a fact held outside the
files, the day a decision was made, the latest upstream release, a
GitHub setting, git history, another repo; and not a definition that
scopes other rules. Behaviour and instruction go to a Guide; the why
goes to an Explanation; a scoping definition is an H2 with no trailer.

**Kind is judged from the sentence, not the trailer.** A sentence a
script decides from the files with no judgment call is deterministic;
a sentence with a judgment word, "describes", "names the concept",
"small against", is stochastic. Where a sentence mixes the two, the
mechanical part stays deterministic and the judgment moves to the
Explanation. Whether a check exists is a separate question: an
unchecked predicate of either kind is allowed, and the check follows
the rule.

**A scoping heading is not a rule.** An H2 with no trailer names which
members the H3 rules under it bind. It is one shape whether it has one
child or eleven, and its definition is never repeated in the children.

**Three working policies** hold for any audit of the rules. A repo
change is the expensive way out: a rule the repo breaks is rewritten
or deleted before the repo is fixed to meet it. There is no credit for
rule count: delete is the default for a rule that restates another or
binds something too small to matter. And keeping a rule because a
detector emits its id is backwards: the detector follows the rule.

## A runbook's file

A runbook is the one built doc-type whose file carries no OKF
frontmatter and whose reader is a program, the Claude Code harness,
before it is a model. Its rules still sit here and not under Harness
Files, because the Runbook doc-type's contract shape claims the keys,
`name`, `description`, `model`, `effort`, and a skill's
`disable-model-invocation` and `arguments`: what the file declares is
the doc-type's, and where the harness finds it is the harness's
([Location](/standards/harness/files.md#location)). The reasons below
are therefore about what each part of the file means to the program
that loads it.

### The front matter

The vocabulary is exact
([Front matter](/standards/doc-type/runbook-conventions.md#front-matter)),
since the harness reads a closed set of keys. An agent declares no
`arguments`, since its input is the launching prompt, whole.

### What the fields do

**`description`.** For an agent, or a skill the model may invoke, the
first sentence states what the runbook does and the second, opening
`Use when`, names the keywords, contexts, or file types under which it
is invoked; that second sentence is what the model matches on. For a
skill only the user invokes, the description is the one-sentence
summary the user reads in the slash-command list
([Description](/standards/doc-type/runbook-conventions.md#description)).

**`disable-model-invocation`.** Under `false` the model fires the skill
on its own and other skills reach it; under `true` only the user typing
its name invokes it
([Model invocation flag](/standards/doc-type/runbook-conventions.md#model-invocation-flag)).

**`model`.** A pinned model governs only the turn that loads the skill.
A skill that runs several turns with the user carries `inherit`.

**`allowed-tools` and `disallowed-tools`.** `allowed-tools`
pre-approves the listed calls to run without prompting;
`disallowed-tools` denies outright, and restates no denial a
`settings.json` already makes
([Tool fields](/standards/doc-type/runbook-conventions.md#tool-fields)).

**An agent's `tools`.** The launched agent's toolset is exactly that
list, and an agent without the field has the full toolset
([tools](/standards/doc-type/runbook-conventions.md#tools)). `tools` is
no cognate of a skill's `allowed-tools`: that pre-approves calls inside
the caller's permission flow, while a tool absent from `tools` does not
exist for the agent.

### How arguments reach a skill

The harness appends the input after the body as `ARGUMENTS: <text>`,
whole and unsplit, and the executing agent never sees the argument's
name. Every argument is a string. This is why the body carries no
`$ARGUMENTS` or `$0` placeholder: there is nothing for one to expand to
([Arguments](/standards/doc-type/runbook-conventions.md#arguments)).
In the contract shape this is the `accept` edge, drawn at the root: the
runbook accepts one string and nothing else.

### An agent's body is its system prompt

An agent's body is the launched subagent's system prompt, set at spawn:
it addresses the agent that runs it, and nothing else reaches that
agent except the launching prompt. The report travels back as the
subagent's final message, the `report` edge. A runbook's steps
therefore end on a completion criterion, the condition that tells the
agent the work is done, because nothing else will.

## A loop's file

A loop's file is checked by `scripts/loop-lint`, which reads it the way
the encoding cuts it: one paragraph, one fenced `mermaid` flowchart,
then three H2s. The graph is the source of truth; the paragraph says
what state the loop drives and toward what. The detector stops at a
file's first disagreement, since each rule reads the cut the one before
it made, and goes on to the next file. A repo with no `loops/` tree is
clean by construction. The edge rule,
[Edges follow the shape](/standards/doc-type/loop-conventions.md#edges-follow-the-shape),
is the shape the Loop doc-type draws: steps in iteration order, a
programmed exit where its author put it, and control coming back.
