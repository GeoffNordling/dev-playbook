# workstreams/delegation/sandcastle/rig/ — index

The code that runs the
[Sandcastle pipeline](/workstreams/delegation/sandcastle/pipeline.md), kept here
while the workstream is open and moved to a permanent home when the work lands on
`main`. Each run takes a lab directory, a scratch folder where the fake
real repository, the config copy, and the throwaway copies are made.
`node_modules` links to an installed `@ai-hero/sandcastle` and is not
committed.

- `setup.sh` — fills the lab directory: the fake real repository, the config copy with both patches applied, two stints' throwaway copies, and the container image
- `parallel.mjs` — runs two stints at once and closes both at once, then checks commits, billing, hook logging, and clean up
- `call.mjs` — one sealed call of a stint: one Claude session in a new container on the stint's work copy, fresh or resumed, then a probe for uncommitted work; writes the call's record to the stint's folder
- `stint.py` — the headless driver and the command that starts a stint: makes the work copy and the config copy in `~/stints/<repo>/<stint>/`, runs one stint from the principal's opening call to the yield, then lands the branch and deletes both copies, with the stop rules and checkpoints in the script and every call sealed through `call.mjs`; refuses to launch a plan with more tasks than the budget, reads the copy as plain files only, and writes the stint's record to its folder, the principal's context size after each of its calls included
- `rules.py` — checks `stint.py` with no tokens: a scripted fake step plays every agent, in each case one call misbehaves, and a last case runs the whole command from opening both copies to deleting them
- `prompts/` — the stint's four prompts: `iteration.md.in`, `reviewer.md.in`, `principal-open.md.in`, and `principal-checkpoint.md.in`, templates whose `{{KEY}}` placeholders the driver fills
- `seed/` — the `wordcount` workstream the by-hand stint ran on: its head file, plan, and progress log as `.md.in` templates, copied in without the `.in`, a smoke test for the check gate, and `gitignore`, copied in as `.gitignore`
- `lifetime.mjs` — two calls in turn on one work copy with a stand-in agent; checks that each gets a new container and only the work copy carries
- `traps.mjs` — plants every booby-trap trigger in a work copy through a stand-in agent; checks that `run()` fires none on the host
- `resume.mjs` — a Sonnet session told a magic word, then resumed in a new container and asked it, beside a fresh control; checks the conversation carries and its session file stays in the stint's folder
- `relocated.mjs` — moved to [`src/dev_playbook/stint/sandcastle/relocated.mjs`](/src/dev_playbook/stint/sandcastle/relocated.mjs): the plug-in, Sandcastle's podman plug-in with the work copy moved to `~/assignment/<repo>`
- `receiver.py` — the host-side receiver that writes the container's hook events into the measurement database
- `package.json` — requires `@ai-hero/sandcastle` `^0.12.0`, any 0.12 release
- `image/Containerfile` — the container image: Fedora, the `claude` binary, and the dotfile links
- `patches/measure-event-sink.patch` — from the `sandbox-probe` branch: `measure-event` sends each row to the receiver when a sink file, naming the receiver's address and port, is present
- `patches/end-hooks-wait.patch` — the Stop and SessionEnd `measure-event` hooks wait instead of running in the background
- `patches/commit-sandbox.patch` — the `commit-sandbox` skill and the commit procedure it reads, which the stint's prompts run
