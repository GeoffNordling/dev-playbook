---
name: dev-tools-repo-sync
description: Sync all Git repos in the workspace with their remotes
disable-model-invocation: true
---

# Dev Tools: Repo Sync

Sync all Git repos in the workspace with their remotes. Auto-pulls and auto-pushes when safe (clean repo, no conflicts). Reports errors when action would be risky.

## Workflow

1. Determine the platform and run the sync script:
   - **Mac (Darwin):** `/Volumes/workplace/dev-tools/bin/repo-sync`
   - **WSL:** `~/workspace/dev-tools/bin/repo-sync`
2. Show the user the full output.
3. If any repos are out of sync, summarize what needs attention.
