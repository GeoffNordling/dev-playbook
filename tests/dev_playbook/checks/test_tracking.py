"""Unit tests for the tracking family's checks."""

from pathlib import Path

from dev_playbook.checks.tracking import one_list_item_per_entry
from dev_playbook.model import Repo

CANDIDATES = b"""\
# Candidates

## Export

- **Scheduled exports** \xe2\x80\x94 a report reaches the inbox.
  - **Cadence picker** \xe2\x80\x94 daily, weekly, or monthly.
  - Owner: the export team
- [ ] **Column selection** \xe2\x80\x94 users choose columns.
1. **Fuzzy matching** \xe2\x80\x94 typos return nothing.

```markdown
- not an entry, only an example
```
"""


def test_one_list_item_per_entry() -> None:
    repo = Repo.from_files(
        Path("/r"),
        {
            "CANDIDATES.md": CANDIDATES,
            "docs/CANDIDATES.md": b"- no name here\n",
        },
    )
    assert [(f.path, f.line) for f in one_list_item_per_entry(repo)] == [
        ("CANDIDATES.md", 7),
        ("CANDIDATES.md", 8),
    ]
