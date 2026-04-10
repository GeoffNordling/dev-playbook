---
name: ref-check
description: Scan this repo for broken cross-references between markdown files
---

# ref-check

Run the cross-reference checker on this repository and fix any broken references.

1. Run `python3 ~/workspace/dev-playbook/tools/bin/ref-check`
2. If there are broken references, fix them according to the cross-reference
   conventions in `~/workspace/dev-playbook/standards/repo-documentation.md`.
3. Run the tool again to verify all references resolve.
