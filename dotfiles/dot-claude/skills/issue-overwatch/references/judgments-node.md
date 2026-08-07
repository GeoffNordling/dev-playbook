# The Judgments Node

The traverse's one armed pass of the semantic judgment gate — run after review
approves, before the user's final read. Work through it in order.

1. **Run the judgments yourself.** Invoke /run-judgments (the `Skill` tool) at
   your own main loop, in the issue's worktree. It is never delegated, for the
   reason [the judgments node](~/workspace/dev-playbook/software-factory/factory-operations.md#the-judgments-node)
   gives. It enumerates the misses, dispatches the judges, records the passes,
   and makes focused fixes for refutations; take over the ones it sets aside.

2. **Commit each fix as it lands** — no go-ahead to wait for. Push
   `--no-verify`: the gate this node exists to green goes green at step 4,
   not per push.

3. **Ask where a fix is ambiguous** — a refutation that may be wrong about the
   code, or right about code that should change — per
   [pause 2](~/workspace/dev-playbook/software-factory/user-checkpoints.md#pause-2-judgments-conditional).
   A clean green run asks nothing.

4. **Close green.** Confirm with `make check-judgments`.

5. **Refresh the merge message.** Regenerate the PR title and body with
   `gh pr edit`, per the
   [merge-message recipe](~/workspace/dev-playbook/software-factory/factory-operations.md#the-merge-message-recipe):
   synthesize the entire PR record — the final diff, the comments, and the
   rulings — into an accurate squash-commit message for the whole issue,
   preserving the three mandatory sections' content, the
   `## Deviation ledger` above all. Review findings the user ruled
   real-but-not-this-issue land in `## Deferred` as their tracker stubs.

6. **Present the final read** per
   [pause 3](~/workspace/dev-playbook/software-factory/user-checkpoints.md#pause-3-the-final-review),
   then stop. The user merges in the GitHub UI.
