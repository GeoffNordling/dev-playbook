# workstreams/delegation/sandcastle/rig/ — index

History: the experiment code that proved the
[Sandcastle pipeline](/workstreams/delegation/sandcastle/pipeline.md), kept as
the [experiment log](/workstreams/delegation/sandcastle/experiment-log.md)
ran it. **These scripts no longer run.** The tool moved to
[`src/dev_playbook/stint/`](/src/dev_playbook/stint/cli.py), the `stint`
command, and the prompts, the plug-in, the receiver, the image, and the
patches moved with it. [Running a Stint](/guides/running-a-stint.md) is how
to run one now.

What stayed, as the experiments left it:

- `setup.sh` — filled a lab directory: a fake real repository, the config copy, two stints' throwaway copies, and the container image
- `parallel.mjs` — ran two stints at once and closed both at once, then checked commits, billing, hook logging, and clean up
- `call.mjs` — one sealed call; now `call.py` and `sandcastle/run.mjs` in the package
- `stint.py` — the headless driver; now `loop.py`, `launch.py`, and `cli.py` in the package
- `rules.py` — checked `stint.py`'s stop rules with a scripted fake call; now the package's tests in `tests/dev_playbook/stint/`
- `lifetime.mjs` — two calls in turn on one work copy with a stand-in agent; checked that each gets a new container and only the work copy carries
- `traps.mjs` — planted every booby-trap trigger in a work copy through a stand-in agent; checked that `run()` fires none on the host
- `resume.mjs` — a Sonnet session told a magic word, then resumed in a new container and asked it, beside a fresh control; checked the conversation carries
- `receiver.py` — the hook receiver as a standalone script; now `receiver.py` in the package, run in a thread
- `package.json` — the experiments' `@ai-hero/sandcastle` `^0.12.0`
- `seed/` — the `wordcount` workstream the stints ran on: its head file, plan, and progress log as `.md.in` templates, a smoke test for the check gate, and `gitignore`, copied in as `.gitignore`
