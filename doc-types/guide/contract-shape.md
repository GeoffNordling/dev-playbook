---
type: General-Sheet
title: Instruction
description: Guide's contract shape — one verb and the frontmatter every guide carries; its parts are not yet decided — in prose and as code
---

# Instruction

Instruction is Guide's contract shape
([Doc-Type](/doc-types/doc-type.md)): the form every Guide's contract
takes. Its parts are not yet decided.

## The shape

- **Parts.** Not yet decided; the class declares none.
- **Pointers.** A guide points at any Target, any number of times, and
  a link to a rule is an ordinary reference.

The composition rule: any number of pointers at any Target. A Guide
states no rule, so it carries no trailer.

The shape as code, one module importing the base in
[Doc-Type](/doc-types/doc-type.md#the-base); the reference model holds
the same text whole and a test keeps them identical.

```python
from doc_type import DocType


class Guide(DocType):
    """What a reader needs before one kind of work: steps, calls, a checklist, a catalogue. Instructs.
    It links a Standard's rules as any document does and states none, so it carries no trailer."""
    operations  = {instruct}
    frontmatter = DocType.frontmatter | {type, title}
```
