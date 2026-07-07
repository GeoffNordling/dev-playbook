# File-Graph Instrument — Product Requirements

*THIS FILE IS NOT TO BE COMMITTED*; it is temporary to be deleted before PR.

The file-graph instrument is the third kind of instrument (alongside the
datasheet and the judgment): pointed at a repo, it accounts for every file,
classifies and connects them, and renders the result as an interactive graph.

These are the features the user asked for, in the order they surfaced. They
define intended behavior — the product should do these things.

## The instrument (analysis engine)

1. Account for every file in a target repo — nothing unaccounted for.
2. Bucket files at varying levels of detail, including a throwaway/ignored
   bucket (`.pyc`, mypy/build caches) filtered out via the repo's existing
   gitignore-style rules.
3. Classify markdown into harness-injected (non-OKF) vs OKF-standard concept
   files.
4. Sub-classify harness-injected files: authored-in-`dotfiles` vs
   third-party-imported (`.agents`); treat config as canonical.
5. Detect edges between files in three forms: formal OKF references/links,
   informal file references in code comments, and structural relationships
   (files sharing a standardized directory such as a skill's `references/`
   folder count as linked even without a direct reference).
6. Compute reachability from CLAUDE.md: which files an agent reading only
   CLAUDE.md can reach, and the hop distances — and by implication which files
   are unreachable.
7. Reuse existing repo docs and linting/enforcement scripts for detection
   rather than reinventing them.
8. Produce a runnable tool that emits a JSON archive of every file (the data
   model).
9. Report a file-extension inventory with approximate counts.
10. Be a proper instrument: a defined notion of "instrument", a written
    file-graph spec covering the every-file bucketing, and a designed
    user-facing output.

## The visualization (interactive graph)

11. Interactive force-directed graph built on d3.
12. Pan and zoom (mouse wheel).
13. Encode file type by shape and subtype by color:
    - skills = star, colored to distinguish authored (dotfiles) vs third-party;
    - index files = circle (same shape as concept files) with a distinct color;
    - test code = same shape as other code, different color;
    - CLAUDE.md stands out distinctly, and only the real central one appears
      (the dotfiles copy is excluded).
14. Color edges with a simple scheme — few colors.
15. Two color modes (by-bucket / by-reach-from-CLAUDE.md); switching a mode
    updates the legend to match, and a button's title stays consistent with its
    histogram's title.
16. Encode reach distance as a single graduated continuous green→red scale
    (green = close to CLAUDE.md, red = far).
17. Show a histogram of hops, labeled consistently with its button.
18. Show a "nodes by bucket" summary with visually distinguishable colors.
19. Clickable legends: clicking any legend entry (any color/shape category, in
    the node-color or reach-distance legend) highlights those nodes in the
    graph.
20. Light theme for the entire artifact, with visuals tuned for a light
    background.
21. Search box: type a string, highlight all matching files.
22. Shortest path: pick two files by clicking, highlight the shortest path
    between them.
23. (Stretch) Raw-text viewer: click a document, see its raw text on screen.

## Integration

24. Document the instrument consistent with the other instrument docs — at
    minimum note that a graph visualizer exists.
