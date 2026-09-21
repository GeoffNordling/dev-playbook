---
type: General-Sheet
title: Reasons
description: Explanation's contract shape — one subject and its Reasons, each a design decision, its argument, and the ids it explains — in prose and as code
---

# Reasons

One subject and its Reasons are Explanation's contract shape
([Doc-Type](/doc-types/doc-type.md)): the form every Explanation's
contract takes.

## The shape

- **Subject.** The document the Explanation explains, found by name: the
  same basename, one directory up. Every id a Reason names resolves to a
  part of it.
- **Reason.** One design decision and the argument for it: a heading, a
  body, and the ids it explains. The body is the why and never a
  predicate. The ids are one or several, each a part of the subject, and
  a part may have no Reason.

The composition rule: exactly one subject, any number of Reasons, and
nothing else. An Explanation states no rule and names no verifier and
no gate.

The shape as code, one module importing the base in
[Doc-Type](/doc-types/doc-type.md#the-base); the reference model holds
the same text whole and a test keeps them identical.

```python
from doc_type import DocType, Id


class Explanation(DocType):
    """The Reasons for one document. Explains.
    In code, Reasons might sit inside the document they explain, but markdown is more rigid;
    in order to ensure a markdown file holds only one concern, we split Reasons into a 
    distinct Explanation object that gets its own file."""
    operations  = {explain}
    frontmatter = DocType.frontmatter | {type, title}

    class Reason:                 # a part: an H2; one design decision and the argument for it
        explains: set[Id]         # the trailer line; each id resolves to a part of `subject`, and a part may have no Reason
        why:      str             # everything between the heading and the trailer; never a predicate

    subject: DocType              # the document this explains, found by name: the same basename, one directory up
    reasons: list[Reason]         # in file order, and nothing else under the H1
```
