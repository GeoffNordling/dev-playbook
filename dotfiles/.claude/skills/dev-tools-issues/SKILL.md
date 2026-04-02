---
name: dev-tools-issues
description: Report open GitHub issues across all workspace repositories
disable-model-invocation: true
---

# Dev Tools: Issues

Report open GitHub issues across all workspace repositories.

## Workflow

1. Determine the platform and run the issues script:
   - **Mac (Darwin):** `/Volumes/workplace/dev-tools/bin/repo-issues`
   - **WSL:** `~/workspace/dev-tools/bin/repo-issues`
2. Show the user the full output.
3. Summarize the total count and which repos have the most issues.
