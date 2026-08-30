---
name: improve-codebase-architecture
description: Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick.
disable-model-invocation: true
model: inherit
effort: xhigh
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

This command is _informed_ by the project's domain model and built on a shared design vocabulary:

- {Read [module design](~/workspace/dev-playbook/standards/modules/design.md) for the architecture vocabulary and its principles, loaded first; `module`, `interface`, `depth`, `seam`, `adapter`, `leverage`, `locality` — the deletion test, "the interface is the test surface," "one adapter = hypothetical seam, two = real"}. Use these terms exactly in every suggestion — don't drift into "component," "service," "API," or "boundary."
- The domain language in `CONTEXT.md` gives names to good seams; Decision Records in `docs/decisions/` record decisions this command should not re-litigate.

## Process

### 1. Explore

**Scope before you scan — YAGNI.** Deepening a module pays off by making future changes to it easier, so put extra weight on the parts of the codebase that have recently changed. Decide *where* to look before you look:

- If the user named a direction — a module, a subsystem, a pain point — take it, and skip the inference below.
- Otherwise, walk back a good stretch of the commit history (`git log --oneline`) to find the codebase's hot spots — the files and areas that keep coming up — and let those paths pull your attention first. If the changes are scattered with no clear hot spot, widen the net.

{Read `CONTEXT.md` for the project's domain glossary} and {Read `docs/decisions/` for the Decision Records in the area you're touching} first.

Then spawn a sub-agent to walk the codebase. Don't follow rigid heuristics — explore organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity, or just move it? A "yes, concentrates" is the signal you want.

### 2. Present candidates as an HTML report

{Read [html-report.md](references/html-report.md) for the full HTML scaffold, diagram patterns, and styling guidance}, then {Write to scratch a self-contained HTML file; the OS temp directory, so nothing lands in the repo}. Resolve the temp dir from `$TMPDIR`, falling back to `/tmp` (or `%TEMP%` on Windows), and write to `<tmpdir>/architecture-review-<timestamp>.html` so each run gets a fresh file. Open it for the user — `xdg-open <path>` on Linux, `open <path>` on macOS, `start <path>` on Windows — then {Report the finished report's absolute path, already opened for the user}.

The report uses **Tailwind via CDN** for layout and styling, and **Mermaid via CDN** for diagrams where a graph/flow/sequence reliably communicates the structure. Mix Mermaid with hand-crafted CSS/SVG visuals — use Mermaid when relationships are graph-shaped (call graphs, dependencies, sequences), and hand-built divs/SVG when you want something more editorial (mass diagrams, cross-sections, collapse animations). Each candidate gets a **before/after visualisation**. Be visual.

For each candidate, render a card with:

- **Files** — which files/modules are involved
- **Problem** — why the current architecture is causing friction
- **Solution** — plain English description of what would change
- **Benefits** — explained in terms of locality and leverage, and how tests would improve
- **Before / After diagram** — side-by-side, custom-drawn, illustrating the shallowness and the deepening
- **Recommendation strength** — one of `Strong`, `Worth exploring`, `Speculative`, rendered as a badge

End the report with a **Top recommendation** section: which candidate you'd tackle first and why.

**Use CONTEXT.md vocabulary for the domain, and the module-design vocabulary for the architecture.** If `CONTEXT.md` defines "Order," talk about "the Order intake module" — not "the FooBarHandler," and not "the Order service."

**Decision Record conflicts**: if a candidate contradicts an existing Decision Record, only surface it when the friction is real enough to warrant revisiting it. Mark it clearly in the card (e.g. a warning callout: _"contradicts 0007 — but worth reopening because…"_). Don't list every theoretical refactor a record forbids.

Do NOT propose interfaces yet. After the file is written, ask the user: "Which of these would you like to explore?"

### 3. Grilling loop

{If the user picks a candidate, {Run [/grilling](~/.claude/skills/grilling/SKILL.md) to walk the decision tree with them}} — constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive.

{If a new term surfaces that `CONTEXT.md` doesn't yet name, or a rejection deserves a Decision Record, {Run [/domain-modeling](~/.claude/skills/domain-modeling/SKILL.md) to keep the domain model current as you go}}:

- **Naming a deepened module after a concept not in `CONTEXT.md`?** Add the term to `CONTEXT.md`. Create the file lazily if it doesn't exist.
- **Sharpening a fuzzy term during the conversation?** Update `CONTEXT.md` right there.
- **User rejects the candidate with a load-bearing reason?** Offer a Decision Record, framed as: _"Want me to record this as a Decision Record so future architecture reviews don't re-suggest it?"_ Only offer when the reason would actually be needed by a future explorer to avoid re-suggesting the same thing — skip ephemeral reasons ("not worth it right now") and self-evident ones.
- {If the user wants to explore alternative interfaces for the deepened module, {Read [design-it-twice.md](references/design-it-twice.md)} and work through it: parallel sub-agents, each pinned to a different interface}.
