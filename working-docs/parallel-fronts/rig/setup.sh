#!/usr/bin/env bash
# Build the fake real repos, the config copy, both fronts' throwaway copies,
# and the image. Nothing here touches the user's real repositories except
# cloning dev-playbook's published main out of them.
set -euo pipefail
E=/tmp/claude-1000/-home-geoff-workspace-dev-playbook/a7e4c307-11ae-41f0-a856-c762525f0982/scratchpad/exp3
WT=/home/geoff/workspace/dev-playbook/.claude/worktrees/worktree-sandcastle-fronts
rm -rf "$E/remote" "$E/real" "$E/config" "$E/lap" "$E/markers" "$E/image/ctx"
mkdir -p "$E/remote" "$E/real" "$E/config" "$E/lap/front-a" "$E/lap/front-b" "$E/markers"

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

# Fake real dev-playbook, for the front assigned to change dev-playbook.
git clone -q --no-hardlinks --branch main /home/geoff/workspace/dev-playbook "$E/real/dev-playbook"

# The config copy: dev-playbook at published state, mounted read-only.
git clone -q --no-hardlinks --branch main /home/geoff/workspace/dev-playbook "$E/config/dev-playbook"
# Part 4: main plus one file, the prototype's measure-event that sends events
# to a host receiver when the sink file is present. Not yet on main.
git -C "$WT" show sandbox-probe:dotfiles/dot-claude/hooks/measure-event >"$E/config/dev-playbook/dotfiles/dot-claude/hooks/measure-event"
git -C "$E/config/dev-playbook" -c user.name=exp3 -c user.email=exp3@example.invalid commit -q -am "part 4: sandbox-probe's measure-event"

"$WT/scripts/front-clone" open "$R" "$E/lap/front-a/mission-control" front-a
"$WT/scripts/front-clone" open "$E/real/dev-playbook" "$E/lap/front-b/dev-playbook" front-b

# The image, built from the config copy's published tree.
mkdir -p "$E/image/ctx"
git -C "$E/config/dev-playbook" archive HEAD src scripts dotfiles pyproject.toml | tar -x -C "$E/image/ctx"
cp -L /home/geoff/.local/bin/claude "$E/image/ctx/claude"
podman build -q -t localhost/sandcastle-probe:exp3 -f "$E/image/Containerfile" "$E/image/ctx"
echo "setup done"
