# working-docs/parallel-fronts/rig/ — index

The code that runs the
[Sandcastle pipeline](/working-docs/parallel-fronts/pipeline.md), kept here
while the set is open and moved to a permanent home when the work lands on
`main`. Each run takes a lab directory, a scratch folder where the fake
real repository, the config copy, and the throwaway copies are made.
`node_modules` links to an installed `@ai-hero/sandcastle` and is not
committed.

| File | What it is |
|------|------------|
| `setup.sh` | makes the lab: the fake real repository, the config copy with both patches applied, two fronts' throwaway copies, and the container image |
| `parallel.mjs` | runs two fronts at once and closes both at once, then checks commits, billing, hook logging, and clean up |
| `relocated.mjs` | the plug-in: Sandcastle's podman plug-in with the work copy moved to `~/assignment/<repo>` |
| `receiver.py` | the host-side receiver that writes the container's hook events into the measurement database |
| `package.json` | pins `@ai-hero/sandcastle` 0.12.0 |
| `image/containerfile` | the container image: Fedora, the `claude` binary, and the dotfile links |
| `patches/measure-event-sink.patch` | `measure-event` sends each row to the receiver when a port file is present, from the `sandbox-probe` branch |
| `patches/end-hooks-wait.patch` | the Stop and SessionEnd `measure-event` hooks wait instead of running in the background |
