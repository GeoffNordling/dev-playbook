# sandbox_probe/ — index

A prototype that runs a headless Claude agent inside a podman container, on subscription billing, with a fence a confused agent cannot cross. Read [Sandboxed agent design](/sandbox_probe/SPEC.md) for how the thing is meant to be built and run; read [Sandboxed headless Claude](/sandbox_probe/NOTES.md) for what the prototype measured and the defect it left standing.

Ordering: the design first, then the record it came from, then the open decision it left.

- [Sandboxed agent design](/sandbox_probe/SPEC.md) — The prescribed build-and-run design for a sandboxed Claude agent — one image, three mounts, and the path layout that makes one instruction work inside and outside podman
- [Sandboxed headless Claude](/sandbox_probe/NOTES.md) — What the sandbox prototype is, how its fence works, what it found on this machine, and the defect to fix next time
- [Sandbox measurement options](/sandbox_probe/MEASUREMENT-OPTIONS.md) — The options for carrying a sandboxed run's hook events into the host measurement store — what is rejected, and what the two live options still need
