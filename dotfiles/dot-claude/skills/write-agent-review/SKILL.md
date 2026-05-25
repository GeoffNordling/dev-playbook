---
name: write-agent-review
description: Author an agent-review assertion that focuses the LLM judge on one semantic question about prose. Use when adding or updating a test under `tests/agent_review/`, when converting an agent-review stub to a real verifier, or when annotating a spec node with `agent-review` as a needs value.
disable-model-invocation: false
model: opus
effort: xhigh
---

# Write Agent Review

An agent-review test hands the judge three things: subject document(s), standard document(s), and an assertion. The judge sees nothing else — not the runner, not the test code, not any code at all. Everything you want the judge to verify must be visible in what you hand it.

The assertion is the load-bearing input. Write it so the judge has a clear semantic question to answer.

## Five rules

1. **Only assert what's verifiable from the subjects and standards you hand the judge.** Think like the judge — it sees only what you show it. If a claim relies on data outside that view (code behavior, runtime state, external systems), the agent review can't reach it.

2. **Name the specific normative element being audited.** Never just "the subject." Always something like "the X defined by `<id>`" — pin the judge to a specific element, not the whole subject.

3. **Match the assertion's shape to what's falsifiable in the subject.** Identify what specific change to the subject (or its reference) would make it wrong in a way a reader could see. Phrase the assertion to ask about that change. If the subject contains an enumeration with citations, the falsifiable surface is incompleteness or wrong citations — ask about those. If the subject contains a single citation amid unverifiable behavioral commitments, the only falsifiable surface is citation accuracy — narrow to that.

4. **Sparse subjects warrant narrow assertions.** When the subject mostly defers to behavior or implementation, the prose surface is thin — narrow to what is actually checkable.

5. **State scope explicitly only when it is narrower than the subject's own description implies.** Most assertions do not need an explicit scope clause.

## One semantic focus per assertion

Aim for one semantic question, not one literal claim. The judge's reasoning works best when its attention sits on a single idea — even if executing that idea means cross-checking many items.

- ✅ "Every section citation in this enumeration is accurate" — one semantic focus (citation accuracy), N items.
- ✅ "The field set and each field's type correspond to the standard's keyword shape" — one semantic focus (correspondence), several fields.
- ❌ "The field set corresponds to the standard *and* the function's signature is sufficient for §X conformance" — two semantic foci jammed together; the judge's attention gets split.

If you are unsure whether two questions belong together or apart, ask the user.

## Assertion grammar

Canonical shape:

```
The <specific element> [defined | enumerated | cited | committed]
by `<subject-id>` in <subject-file> faithfully implements
<prescription, with section reference if applicable> of <standard-file>.
[Optional: scoped to <constraint>.]
```

For pure citation-accuracy reviews:

```
The <section> citation in `<subject-id>` (<subject-file>) is accurate:
<section> of <standard-file> <still says what the subject draws from it>.
```

## Worked examples

**Enumeration faithfulness.** The subject enumerates rule ids each tied to a standard section:

> The `rule_violated` enumeration defined by `dsn~deserialize.parse-error~0` in specs/design/deserialize.md faithfully implements §2 of spec-standard.md, scoped to rules detectable by inspecting a single spec file's syntax.

The falsifiable surface is the enumeration's completeness and each entry's citation. One semantic focus (enumeration-vs-standard faithfulness), many items.

**Citation accuracy.** The subject's content is mostly a behavioral commitment ("render produces conformant markdown") and one citation:

> The §2 keyword-order citation in `dsn~serialize.render~0` (specs/design/serialize.md) is accurate: §2 of spec-standard.md defines a canonical keyword order.

The behavioral claim is not verifiable from prose alone — it would require seeing the implementation. The only prose-checkable surface is the citation. Narrow to it.

## Pitfalls

- "Subject is a faithful implementation of §X.X" without naming a specific element — the judge picks the easiest interpretation, often the wrong one.
- Asserting wholesale conformance for sparse subjects — the judge defaults to whichever surface is concretely checkable (often the subject's own form), not what you meant.
- Spelling out a procedure for the judge in the assertion — the auditor template carries the procedure; the assertion carries the claim.
- Stacking two semantic questions in one assertion — the judge's attention splits and one tends to drift.
