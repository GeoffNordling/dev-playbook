# Diagram contract

You are drawing the **relationships layer** of a Python package for a reader who has not read the code, on top of a deterministic inventory. The dispatching prompt gives you the inventory path, the package path, an optional focus, and the report output path.

## Ground truth — do not re-derive

Read the inventory file (py-outline output: every module, class, function, and signature). Treat it as authoritative for *what exists*. Do not rediscover structure by reading the whole package — read source only where you must to establish relationships the inventory cannot show: which module imports which, and how objects are constructed and wired at runtime.

## Diagrams — produce both, named

Name each explicitly; an unnamed artifact gets dropped.

1. **Static import/dependency graph** — a Mermaid `flowchart` of module-level import edges. Module nodes only.
2. **Runtime assembly / call sequence** — a Mermaid `sequenceDiagram` showing how objects are constructed and wired, and the order of the main call flow from the entry point onward. If there are no clear participants, use an ordered `flowchart` instead.

Add a third **Class collaboration** diagram (Mermaid `classDiagram`, class nodes only) *only* if it shows something the two above cannot.

## Rules

- **Never mix node kinds in a structural diagram.** In the dependency graph (and any class diagram), every node is one kind — modules with modules, classes with classes. Do not drop a class node into the module graph. The sequence diagram is exempt: its participants are runtime actors, whatever they are.
- **Live code only.** Describe what the code does. No speculation, no recommendations, no "where X could plug in." Where the code leaves something genuinely unclear, say so plainly rather than guessing.

## The report

Write one Markdown file to the output path you were given, containing in order:

1. A one-line note of which files you actually read — the inventory plus the source files you opened.
2. Each diagram, with a 2–4 line legend beneath it explaining what the reader is looking at.

Center the report on the focus if one was given; otherwise cover the package.

## Return

Return only the report path and a one-line summary. Do not print the report contents — they live in the file.
