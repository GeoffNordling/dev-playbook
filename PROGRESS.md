# Progress log

The running memory of this Ralph loop. Each iteration appends one line below —
what it did and what is next — newest at the bottom. A fresh agent reads this
before starting, to see what earlier iterations did.

## Log

<!-- iterations append one line each below this line -->

- Task 1 done: `cloa_viewer` and `cloa_viewer.kinds` packages with empty inits, `cli.py` with `parse_args`/`main`, six tests in `tests/dev_playbook/cloa_viewer/test_cli.py`, and the `viewer` group, `dev` additions, `[tool.uv] default-groups`, and `[project.scripts]` in `pyproject.toml`; `uv sync` also rewrote the tracked `uv.lock`, which the "What you may write" list does not name but `uv sync` cannot avoid — flagged for the user, not treated as a stop; `uv run cloa-viewer --help` prints usage and the gate is green. Next: task 2, the state module and the envelope schema.
- Task 2 done: `state.py` with `state_root`/`checkout_dir`/`head_commit`/`branch_name`/`write_checkout_json`/`envelope`/`load_schema`/`validate`/`write_json`/`ContractError`, `schemas/envelope.schema.json` (draft 2020-12, `additionalProperties: false`, all seven fields required), and 13 tests in `tests/dev_playbook/cloa_viewer/test_state.py`; no design disagreement found — the contract member's envelope table and the plan's schema match field for field. Next: task 3, the registry and the `index-tree` kind, which also creates the shared `checkout` fixture.
