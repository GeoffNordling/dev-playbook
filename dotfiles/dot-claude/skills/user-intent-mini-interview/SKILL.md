---
name: user-intent-mini-interview
description: Interview the user for a drafted brief's User intent section and write it in their own words. Use when intake or design has drafted a brief and needs its User intent, or when the user wants an existing issue's User intent redone.
disable-model-invocation: false
model: inherit
effort: xhigh
argument-hint: "[issue-number]"
---

# User Intent Mini-Interview

Get the user's intent in their own voice, check it against the brief just drafted, and write the `User intent` section from what they said.

Every other heading is the agent's work — specific, literal, argued out over a long session. `User intent` is the user's: a short, high-level umbrella the build agent consults when it hits a choice the brief leaves open. It carries the user's **vibe** into an issue otherwise written end to end by an agent. Its role and shape are fixed by [issue authoring](~/workspace/dev-playbook/standards/tracking/issue-authoring.md#the-build-leaf-brief-modedirect); this skill is how the text gets written.

The brief in play is the draft the calling beat holds. Run with no draft in context and `$ARGUMENTS` names an issue — read its body and treat that as the draft.

## 1. Ask cold

Open with the ask and present nothing else:

> What's your User intent for this issue?

Then stop. The user answers from memory, and that memory is the whole signal — the vibe that has been driving the session, uncontaminated by the wording the brief settled on. A recap of the draft first hands them the agent's framing to echo back, and step 2 then finds nothing, because both sides came from the same place. Cold is what makes the check real.

Expect voice-dictation or fast typing: fragments, run-ons, trailing thoughts. That is the input this beat is built for.

## 2. Scrutinise

Read what they said against the drafted brief and surface what collides, in one message, each item quoting the specific line it lands on:

- **Contradiction** — the intent and a line of the brief cannot both hold.
- **Gap** — the intent leans on something the brief never covers.
- **Drift** — the intent stresses what the brief treats as minor, or shrugs at what the brief makes central.

The user is in an intuition headspace; the brief is literal. The distance between them is the finding. When nothing collides, say so plainly and go to step 3.

## 3. Marry the two

Either side may give, the user's call, one collision at a time. The brief is still a draft in this session and nothing has landed on GitHub, so amending an acceptance criterion costs nothing at this moment — and half the value here is the vibe catching a spec the agent got subtly wrong, so treat the brief as a live suspect, never only the intent.

The two do not have to match perfectly. They have to stop obviously fighting.

This is a conversation, and it runs until the user ends it.

## 4. Write `User intent` from their words

Free prose, five lines at most — two or three sentences is typical.

**Delete and repair; never add.** Repair grammar, merge fragments, cut fillers and asides. Every idea in the finished section traces to something the user actually said; an enriching clause the agent supplies is what this beat exists to keep out.

Raw:

```text
yeah so this one is really about not losing writes, um, I'd rather it blow up
in my face than quietly drop something, and honestly keep the function count
low if you can but not at the cost of, you know, making the callers do work
```

Landed:

```text
This one is really about not losing writes — I'd rather it blow up in my face
than quietly drop something. Keep the function count low where you can, but not
at the cost of making the callers do work.
```

Show the cleaned paragraph so the user sees the exact text, then hand it back to the calling beat, which writes it into the brief. This skill writes nothing to GitHub.
