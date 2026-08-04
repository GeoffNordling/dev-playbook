# The Judgments Node

The traverse's one armed pass of the semantic judgment gate — run after review
approves, before the user's final read. Work through it in order.

1. **Run the judgments yourself.** Invoke /run-judgments (the `Skill` tool) at
   your own main loop, in the issue's worktree. It is never delegated, for the
   reason [the judgments node](~/workspace/dev-playbook/software-factory/factory-operations.md#the-judgments-node)
   gives. It enumerates the misses, dispatches the judges, records the passes,
   and makes focused fixes for refutations; take over the ones it sets aside.

2. **Commit each fix as it lands**, on the token you hold — no go-ahead to wait
   for.

3. **Ask where a fix is ambiguous** — a refutation that may be wrong about the
   code, or right about code that should change — per
   [pause 2](~/workspace/dev-playbook/software-factory/human-checkpoints.md#pause-2-judgments-conditional).
   A clean green run asks nothing.

4. **Close green.** Confirm with `make check-judgments`.

5. **Refresh the merge message.** Regenerate the PR title and body from the final
   diff with a `gh pr edit`, per the
   [merge-message recipe](~/workspace/dev-playbook/software-factory/factory-operations.md#the-merge-message-recipe).

6. **Hand over the final verified push** if you committed fixes in step 2 — the
   command template is your own turn-boundary list. With no fixes, origin
   already holds the final diff.

7. **Present the final read** per
   [pause 3](~/workspace/dev-playbook/software-factory/human-checkpoints.md#pause-3-the-final-review),
   then stop. The user merges in the GitHub UI.
