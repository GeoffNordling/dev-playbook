#!/usr/bin/env bash
# Build the lab: the fake real repos, the config copy, the fronts' throwaway
# copies, and the image. Nothing here touches the user's real repositories
# except cloning dev-playbook's published main out of them.
# Usage: setup.sh <lab directory>
set -euo pipefail
E="$1"
RIG="$(cd "$(dirname "$0")" && pwd)"
WT="$(cd "$RIG/../../.." && pwd)"
rm -rf "$E/remote" "$E/real" "$E/config" "$E/lap" "$E/image"
mkdir -p "$E/remote" "$E/real" "$E/config" "$E/lap" "$E/image"

# Fake mission-control, with the user's unpushed work in a worktree.
git init -q --bare -b main "$E/remote/mission-control.git"
R="$E/real/mission-control"
git init -q -b main "$R"
git -C "$R" remote add origin "$E/remote/mission-control.git"
echo "# mission-control" >"$R/README.md"
git -C "$R" add README.md
git -C "$R" commit -q -m "first"
git -C "$R" push -q origin main
git -C "$R" worktree add -q -b issue-123 "$R/.claude/worktrees/issue-123"
echo "precious" >"$R/.claude/worktrees/issue-123/precious.txt"
git -C "$R/.claude/worktrees/issue-123" add precious.txt
git -C "$R/.claude/worktrees/issue-123" commit -q -m "unpushed work"
printf '.claude/\n' >"$R/.git/info/exclude"

# The config copy: dev-playbook at published main, plus the two changes the
# pipeline needs that are not yet on main, mounted read-only.
C="$E/config/dev-playbook"
git clone -q --no-hardlinks --branch main /home/geoff/workspace/dev-playbook "$C"
git -C "$C" apply "$RIG/patches/measure-event-sink.patch" "$RIG/patches/end-hooks-wait.patch"
git -C "$C" -c user.name=rig -c user.email=rig@example.invalid commit -q -am "rig: the pipeline's two dev-playbook changes"

# Two fronts on the same repository, for the parallel run.
"$WT/scripts/front-clone" open "$R" "$E/lap/front-a/mission-control" front-a
"$WT/scripts/front-clone" open "$R" "$E/lap/front-b/mission-control" front-b

# The image, built from the config copy's tree.
mkdir -p "$E/image/ctx"
git -C "$C" archive HEAD src scripts dotfiles pyproject.toml | tar -x -C "$E/image/ctx"
cp -L "$HOME/.local/bin/claude" "$E/image/ctx/claude"
podman build -q -t localhost/sandcastle-pipeline:rig -f "$RIG/image/Containerfile" "$E/image/ctx"
echo "setup done"
