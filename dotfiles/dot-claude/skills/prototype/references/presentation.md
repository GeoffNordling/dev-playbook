# Presentation Prototype

Several **structurally-different** variants of the same surface, switchable so you can flip between them, judge against real context, and pick one — or steal parts of each. For questions about what something should look like or how it should read: layout, information hierarchy, the primary affordance.

## When this is the right branch

- "What should this page / report / figure look like?"
- "Show me a few options for this dashboard before I commit."
- "Try a different layout for X."

## Judge against real context, not in a vacuum

A variant is far easier to judge butting up against the real thing — real data, real density, real neighbours. A variant alone on an empty surface is a vacuum: everything looks fine in isolation, and isolation hides the problems a populated context exposes. Prefer mounting variants inside the existing surface they'll live in; build a standalone surface only when there's genuinely no existing home.

## Process

### 1. State the question and pick N

Default to **3** variants. Past ~5 they stop being radically different and start being noise — cap there. Write the plan in one line at the top: e.g. "Three layouts of the settings view, switchable, on the existing surface."

### 2. Generate radically different variants

Variants must differ **structurally** — different layout, hierarchy, primary affordance — not just colour or copy. Three tweaked card grids isn't a prototype, it's wallpaper. Hold each to the surface's purpose, the data it has access to, and the project's existing component or styling system. If two come out too similar, redo one with explicit "don't reuse that structure" guidance.

### 3. Make them switchable on one surface

One switcher toggles which variant renders; everything upstream — data, params, auth — stays shared. The realization depends on the surface:

- **Web app** — gate variants on a `?variant=` URL param with a small floating switcher (arrows plus the current label). Update the param via the framework's router so the choice is shareable and reload-stable; bind `←`/`→` too, but not while an input is focused. Make the switcher visually distinct from the design under evaluation, and hide it in production builds so a stray merge can't ship it.
- **Notebook** — a selector cell (dropdown or param) that re-renders the chosen layout below it.
- **CLI, figure, or report** — a single flag or argument that selects the variant.

Keep the switcher in one shared place so the surface stays clean.

### 4. Hand it over

Surface how to switch and the variant keys. The most useful feedback is usually "I want the header from B with the sidebar from C" — that combination is the actual design they want.

## Anti-patterns

- **Variants that differ only in colour or copy.** That's a tweak, not a prototype. Real variants disagree about structure.
- **Sharing too much between variants.** A shared primitive is fine; a shared overall layout defeats the point — each variant should be free to throw out the layout.
- **Wiring variants to real mutations.** Keep them read-only, or point at a stub. The question is what it should look like, not whether the backend works.
- **Promoting prototype code straight to production.** It was written under throwaway constraints — rewrite the winner properly when you fold it in.
