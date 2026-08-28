---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when the user wants to pin down domain terminology or a ubiquitous language, record an architectural decision, or when another skill needs to maintain the domain model.
disable-model-invocation: false
model: inherit
effort: xhigh
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* `CONTEXT.md` for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

The model lives in two files, each created lazily — only when there is something to write. The glossary is `CONTEXT.md` at the repo root ([context-content.md](~/workspace/dev-playbook/standards/knowledge-organization/context-content.md)); decisions are Decision Records under `docs/decisions/` ([records.md](~/workspace/dev-playbook/standards/decisions/records.md)).

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline

{If a term is resolved, {Read [context-content.md](~/workspace/dev-playbook/standards/knowledge-organization/context-content.md)} and {Write CONTEXT.md in place with the resolved entry; don't batch these up — capture it as it happens}}.

### Offer Decision Records sparingly

{If a decision looks hard to reverse or would surprise a future reader, {Read [records.md](~/workspace/dev-playbook/standards/decisions/records.md)} and test the decision against its when-to-offer bar}. {If every criterion holds, {Write the new record under `docs/decisions/`}}. If any criterion is missing, skip the record.
