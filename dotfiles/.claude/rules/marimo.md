# Marimo Notebook Patterns

**Always load the `marimo-notebook` skill before writing or editing marimo notebooks.**

Note: The marimo-notebook skill prescribes `uv`/`uvx` for running notebooks and
checks. If the current project uses a different environment manager (e.g. Hatch),
use that instead. Run marimo through the project's tool chain, not `uvx`.

## Markdown Cell Formatting

For `.py` marimo files, `marimo check` enforces that markdown content stays
indented at 4 spaces (matching the function body). The opening `"""` goes on
the same line as `mo.md(`, content at 4-space indent, closing `""")` at
4-space indent.

```python
@app.cell
def _(mo):
    mo.md("""
    # Title

    Content here.
    """)
    return
```

NOT this (content at column 0 triggers "overly dedented" warning in .py files):

```python
@app.cell
def _(mo):
    mo.md("""
# Title

Content here.
""")
    return
```

And NOT this (separate line for opening triple-quote triggers indentation warning):

```python
@app.cell
def _(mo):
    mo.md(
        """
        # Title

        Content here.
        """
    )
    return
```

## LaTeX in Markdown Cells

Marimo markdown cells are Python strings. LaTeX commands like `\mid`, `\mathbb`,
`\text` contain backslashes that Python interprets as escape sequences (e.g.,
`\m`, `\t`), producing `SyntaxWarning: invalid escape sequence`. Use raw strings
(`r"""`) for any `mo.md()` cell containing LaTeX:

```python
@app.cell
def _(mo):
    mo.md(r"""
    The expected makespan is $\mathbb{E}[\text{makespan} \mid \theta]$.
    """)
    return
```

Cells without LaTeX can use regular `"""`. When adding LaTeX to an existing
cell, add the `r` prefix.

## Notebook Log Files

Marimo notebooks should write a structured `.log` file alongside themselves so
that both humans and agents can consume results:

- **Human**: sees rendered `mo.md()` tables and plots in `marimo edit` mode
- **Agent**: reads the `.log` file after headless execution to verify results

The log file uses INI-like format (section headers, key-value pairs). Each
notebook creates a log helper early in its cell DAG and calls it in every
computational cell. Every cell that produces data, fits a model, or computes
metrics must log its key outputs; do not skip logging on any computational cell.

Each section should have a clear **information goal**: what metric or check it
captures. Log files are generated output (gitignored), not source.

A minimal log helper looks like this:

```python
from datetime import datetime
from pathlib import Path
from typing import Any

class NotebookLog:
    """Write structured metrics to a .log file during notebook execution."""

    def __init__(self, notebook_path: str) -> None:
        self._path = Path(notebook_path).with_suffix(".log")
        with open(self._path, "w") as f:
            f.write(f"# {self._path.name}\n")
            f.write(f"# Generated: {datetime.now():%Y-%m-%d %H:%M:%S}\n\n")

    def section(self, name: str, data: dict[str, Any]) -> None:
        with open(self._path, "a") as f:
            f.write(f"[{name}]\n")
            for key, value in data.items():
                f.write(f"{key} = {value}\n")
            f.write("\n")
```

Projects may provide their own log helper module; use it if available. If not,
add a `NotebookLog` class like the one above to the project.

## Verification

Always run `marimo check <notebook.py>` before handing back. Use `--fix` if
needed but prefer getting it right the first time.
