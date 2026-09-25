---
type: General-Sheet
title: Instruction
description: Guide's contract shape — sequences of named steps and named references, whose names alone are the gist of the guide — in prose and as code
---

# Instruction

Instruction is Guide's contract shape
([Reference Model](/doc-types/reference-model.md)): the form every Guide's contract
takes. A guide instructs one kind of work
([Guide](/doc-types/guide/definition.md)), and what a reader needs
before that work is of two kinds, the steps to take and the reference
to consult on demand; a guide is a mixture of the two, from all steps,
a recipe, to all reference, a catalogue. The contract is the names:
each sequence, each step, and each reference carries one, and the
names read in file order are what a reader learns of the guide without
reading its body.

## The shape

- **Sequence.** A named, ordered run of steps a reader performs in
  order, numbered from one. A guide holds any number, each independent
  of the others; how they relate, two entry paths that converge on
  one tail, is the lead's prose and not a part.
- **Step.** One action, named, inside one sequence. The name is the
  whole of what the contract shows; the instruction beneath it is the
  body's.
- **Reference.** A named unit of material consulted on demand, a
  concept, a call, a catalogue entry. Its body is opaque to the
  contract and holds whatever the reader needs, prose, a table, a
  diagram, a fenced block, so its name carries the gist. References
  nest as their headings nest.
- **Pointers.** A guide points at any Target, any number of times, and
  a link to a rule is an ordinary reference. A Guide states no rule,
  so it carries no trailer.

The composition rule: any number of sequences and references, in file
order, each named; a sequence holds one or more steps and nothing else.
Whether two sequences belong in one guide is the title's test, one kind
of work, and no count.

The shape as code, one module importing the base drawn in
[Reference Model](/doc-types/reference-model.md#the-language), which
holds the same text whole; a test keeps them identical.

```python
from doc_type import DocType


class Guide(DocType):
    """What a reader needs before one kind of work: sequences of steps, and references. Instructs.
    It links a Standard's rules as any document does and states none, so it carries no trailer."""
    operations  = {instruct}
    frontmatter = DocType.frontmatter | {type, title}

    class Step:                   # a part: one item of a sequence's ordered list
        name: str                 # the item's leading bold run; the instruction after it is the body's

    class Sequence:               # a part: a heading whose section is one ordered list, numbered from one
        name:  str                # the heading's text
        steps: list[Step]         # in list order, one or more

    class Reference:              # a part: a heading whose section holds no ordered list; its body is opaque
        name:  str                # the heading's text, the whole of what the contract shows
        parts: list["Sequence | Reference"]   # the headings nested beneath it, in file order

    parts: list[Sequence | Reference]   # in file order; the names, read down, are the gist of the guide
```
