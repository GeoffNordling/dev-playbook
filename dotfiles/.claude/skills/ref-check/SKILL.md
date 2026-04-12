---
name: ref-check
description: Scan for broken cross-references between markdown files
model: sonnet
effort: medium
allowed-tools: Bash(python3 *)
---

# ref-check

Run the cross-reference checker on this repository.

1. Run `python3 ~/workspace/dev-playbook/tools/bin/ref-check`
2. If there are broken references, propose fixes to the user based on the
   cross-reference conventions in `~/workspace/dev-playbook/standards/repo-documentation.md`.
   Wait for user approval before editing any files.
3. After fixes are approved and applied, run the tool again to verify all references resolve.
