# EARS — Easy Approach to Requirements Syntax

EARS defines a small set of sentence templates that authors use to phrase
requirements unambiguously. This file restates the standard as the standard
defines it; it does not describe how this workspace uses the standard. Our
conventions for combining EARS with other standards are in
[extensions.md](extensions.md) and [spec-format.md](spec-format.md).

Formal origin: Mavin, Wilkinson, Harwood, and Novak, *Easy Approach to
Requirements Syntax (EARS)*, 17th IEEE International Requirements Engineering
Conference (RE'09), 2009. Developed at Rolls-Royce for jet-engine control
software and subsequently adopted across industries.

EARS is about sentence *structure*. It does not define obligation strength;
that concern is owned by RFC 2119 (see [rfc2119.md](rfc2119.md)). EARS
templates use a modal verb slot (canonically `shall`) that any RFC 2119 word
may occupy without altering the template's structural validity.

## The five patterns

Every EARS requirement follows one of five patterns. The pattern is chosen by
the nature of the obligation — unconditional, triggered by an event, gated by
a state, conditioned on an optional feature, or a response to an unwanted
condition.

| Pattern | Template | Use when |
|---|---|---|
| **Ubiquitous** | The `<system>` `shall` `<action>`. | The requirement always holds, without precondition. |
| **Event-driven** | `When` `<trigger>`, the `<system>` `shall` `<action>`. | The requirement fires in response to a discrete event. |
| **State-driven** | `While` `<state>`, the `<system>` `shall` `<action>`. | The requirement holds during a continuous state or mode. |
| **Optional feature** | `Where` `<feature-included>`, the `<system>` `shall` `<action>`. | The requirement applies only in configurations where a feature is present. |
| **Unwanted behavior** | `If` `<condition>`, `then` the `<system>` `shall` `<action>`. | The requirement is a response to an error or undesired condition. |

Each sentence names one subject (`<system>`), one modality marker (`When` /
`While` / `Where` / `If`, except for Ubiquitous), and one verb phrase
describing the required action. The leading marker word and its associated
clause are the only structural differences between patterns.

## Complex requirements

A single behavior may combine more than one trigger, state, or condition.
EARS calls these **complex** requirements. They are formed by chaining
pattern-introducer clauses before the subject-verb body. For example:

    While <state>, when <trigger>, the <system> shall <action>.

Complex requirements are legal EARS but are read as harder to verify; the
original paper recommends decomposing them into multiple simpler requirements
when practical.

## What EARS does not define

- **Obligation strength.** The modal verb slot carries the obligation, and
  that vocabulary comes from RFC 2119 or equivalent.
- **Identity.** How a requirement is named, numbered, or linked to other
  requirements is outside EARS' scope.
- **Rationale and metadata.** Fields such as rationale, status, and coverage
  links are outside EARS' scope.

## Reference

- Mavin, A., Wilkinson, P., Harwood, A., and Novak, M. *Easy Approach to
  Requirements Syntax (EARS).* 17th IEEE International Requirements
  Engineering Conference (RE'09), pp. 317–322, 2009.
  DOI: 10.1109/RE.2009.9
- Mavin, A. and Wilkinson, P. *Big Ears (The Return of "Easy Approach to
  Requirements Syntax").* 18th IEEE International Requirements Engineering
  Conference (RE'10), pp. 277–282, 2010.
