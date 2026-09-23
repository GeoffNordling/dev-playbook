# working-docs/parallel-fronts/rig/ — index

The code that runs the
[Sandcastle pipeline](/working-docs/parallel-fronts/pipeline.md), kept here
while the set is open and moved to a permanent home when the work lands on
`main`. It is copied as it ran for experiment three, part 4, and still
names that run's scratchpad folder as its lab, where the throwaway copies
and the fake real repository are made.

- `setup.sh` — makes the fake real repository, the config copy, the fronts' throwaway copies, and the container image
- `part4.mjs` — runs one front through Sandcastle with real Claude and checks billing, config, and hook logging
- `relocated.mjs` — the plug-in: Sandcastle's podman plug-in with the work copy moved to `~/assignment/<repo>`
- `receiver.py` — the host-side receiver that writes the container's hook events into the measurement database
- `snapshot.sh` — records the real side before and after a run, to prove nothing changed
- `package.json` — pins `@ai-hero/sandcastle` 0.12.0
- `image/Containerfile` — the container image: Fedora, the `claude` binary, and the dotfile links
- `patches/measure-event-sink.patch` — `measure-event` sends each row to the receiver when a port file is present, from the `sandbox-probe` branch
- `patches/end-hooks-wait.patch` — the Stop and SessionEnd `measure-event` hooks wait instead of running in the background
