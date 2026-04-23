# EARS — Easy Approach to Requirements Syntax

EARS defines a small set of sentence templates that authors use to phrase
requirements unambiguously. This workspace adopts EARS unchanged — no
subset, no extensions, no constraints. [spec-format.md](spec-format.md)
shows how EARS combines with the other standards in a full spec file.

EARS covers sentence *structure* only. Obligation strength, identity,
rationale, and metadata are out of scope — obligation strength is handled
by RFC 2119 (see [rfc2119.md](rfc2119.md)), and the other concerns belong
to whatever document format the requirement lives in.

EARS targets high-level stakeholder requirements. The standard does not
claim universal applicability across every level of decomposition.

## Generic template

All EARS requirements are specializations of one generic form:

    <optional preconditions> <optional trigger> the <system name> shall <system response>.

Each of the five named patterns below fixes which slots are present and in
what order. The ordering (preconditions → trigger → subject → response)
reflects a temporal reading of the sentence.

## The five patterns

| Pattern | Template | Use when |
|---|---|---|
| **Ubiquitous** | The `<system>` shall `<response>`. | The requirement always holds, without precondition. |
| **Event-driven** | WHEN `<trigger>`, the `<system>` shall `<response>`. | The requirement fires in response to a discrete event. |
| **State-driven** | WHILE `<state>`, the `<system>` shall `<response>`. | The requirement holds during a continuous state or mode. |
| **Optional feature** | WHERE `<feature-is-included>`, the `<system>` shall `<response>`. | The requirement applies only in configurations where a feature is present. |
| **Unwanted behavior** | IF `<optional preconditions>` `<trigger>`, THEN the `<system>` shall `<response>`. | The requirement is a response to an error or undesired condition. |

The keyword markers (`WHEN`, `WHILE`, `WHERE`, `IF…THEN`) are capitalized in
the generic templates; actual requirement sentences use normal sentence case
(`When …, the system shall …`).

For the State-driven pattern, `DURING` is a sanctioned alternative to `WHILE`
where it reads more naturally.

The Unwanted-behavior pattern separates `<optional preconditions>` from the
`<trigger>`: both come after `IF`, but preconditions scope when the trigger
applies, while the trigger fires the response.

## Complex requirements

A single behavior may combine more than one trigger, state, or condition.
EARS calls these **complex** requirements. They chain pattern-introducer
clauses before the subject-verb body. For example:

    While <state>, when <trigger>, the <system> shall <response>.

Complex requirements are a legitimate extension of the base patterns — the
generic template above permits them directly.

## Reference

- Mavin, A., Wilkinson, P., Harwood, A., and Novak, M. *Easy Approach to
  Requirements Syntax (EARS).* 17th IEEE International Requirements
  Engineering Conference (RE'09), pp. 317–322, 2009.
  DOI: 10.1109/RE.2009.9
- Mavin, A. *EARS — the Easy Approach to Requirements Syntax.*
  https://alistairmavin.com/ears/
