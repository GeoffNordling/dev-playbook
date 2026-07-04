---
type: Standard
title: The AWS Layer
description: The AWS layer — one CDK codebase under src/, per-Lambda dependency groups exported at synth time
---

# The AWS Layer

An AWS repo is one Python codebase, not a collection of per-function
mini-projects:

- `cdk.json` declares `"app": "uv run python -m <package>.app"`.
- Stacks and Lambda handlers live under `src/<package>/` as ordinary
  subpackages.
- Each Lambda's runtime dependencies are a uv dependency group; bundling
  exports the group from the lock at synth time (`uv export --group <fn>`).
  Docker bundling `MAY` be used where a group needs platform builds.

The layer's file requirements are in the
[skeleton tables](/standards/build/skeleton.md); its Make targets (`synth`,
`diff`, `deploy`) are in [make.md](/standards/build/make.md).
