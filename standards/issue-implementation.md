# Implementing a Tracked Issue

The procedure for turning a tracked issue into a merged PR. One issue → one branch → one PR → one merge. Applies to every workspace repo.

## Branch name

`<issue#>-<slug>`. The slug is kebab-case, derived from the issue title; drop tracker prefixes (e.g. `spec-tools:`); keep it short.

The branch lives in a worktree at `.claude/worktrees/<branch-name>/`. The worktree directory and the branch share the same name.

## Setup (new work)

1. From the repo root, ensure `main` is checked out:

   ```bash
   git checkout main
   ```

2. Confirm local `main` matches `origin/main`:

   ```bash
   git rev-parse main
   gh api repos/{owner}/{repo}/branches/main --jq .commit.sha
   ```

   If the SHAs differ, stop and ask the user to `git pull`. The agent does not hold the SSH credential a pull requires.

3. Create the worktree and enter it:

   ```bash
   git worktree add .claude/worktrees/<name> -b <name>
   cd .claude/worktrees/<name>
   ```

## In flight

- Commit on the branch.
- Push with `git push -u origin <name>`.
- Open the PR with `gh pr create --body "Closes #<N> …"`. The `Closes #<N>` token is mandatory — merging the PR closes the issue.

## Resuming work in progress

Any session — agent, human, fresh terminal — resumes by `cd .claude/worktrees/<name>`. The worktree persists across sessions.

## Cleanup

Run `worktree-sweep` from inside the repo. It prunes worktrees whose PR is merged with no local divergence; anything ambiguous (rejected PRs, unpushed commits, missing PRs) is reported for case-by-case handling.

```bash
python3 ~/workspace/dev-playbook/tools/bin/worktree-sweep
```
