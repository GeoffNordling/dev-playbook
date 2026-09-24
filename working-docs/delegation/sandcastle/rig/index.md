# working-docs/delegation/sandcastle/rig/ — index

The code that runs the
[Sandcastle pipeline](/working-docs/delegation/sandcastle/pipeline.md), kept here
while the set is open and moved to a permanent home when the work lands on
`main`. Each run takes a lab directory, a scratch folder where the fake
real repository, the config copy, and the throwaway copies are made.
`node_modules` links to an installed `@ai-hero/sandcastle` and is not
committed.

- `setup.sh` — fills the lab directory: the fake real repository, the config copy with both patches applied, two fronts' throwaway copies, and the container image
- `parallel.mjs` — runs two fronts at once and closes both at once, then checks commits, billing, hook logging, and clean up
- `lifetime.mjs` — two calls in turn on one work copy with a stand-in agent; checks that each gets a new container and only the work copy carries
- `traps.mjs` — plants every booby-trap trigger in a work copy through a stand-in agent; checks that `run()` fires none on the host
- `relocated.mjs` — the plug-in: Sandcastle's podman plug-in with the work copy moved to `~/assignment/<repo>`
- `receiver.py` — the host-side receiver that writes the container's hook events into the measurement database
- `package.json` — requires `@ai-hero/sandcastle` `^0.12.0`, any 0.12 release
- `image/Containerfile` — the container image: Fedora, the `claude` binary, and the dotfile links
- `patches/measure-event-sink.patch` — from the `sandbox-probe` branch: `measure-event` sends each row to the receiver when a sink file, naming the receiver's address and port, is present
- `patches/end-hooks-wait.patch` — the Stop and SessionEnd `measure-event` hooks wait instead of running in the background
