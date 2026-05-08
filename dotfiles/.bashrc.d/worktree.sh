# Git worktree navigation. Sourced by ~/.bashrc via ~/.bashrc.d/* loader.
#
# Worktrees live at <repo>/.claude/worktrees/<branch-name>/ per
# standards/issue-implementation.md. `cdwt <name>` jumps into one;
# tab-completion suggests existing branch-names from the current repo.

cdwt() {
    local toplevel
    toplevel="$(git rev-parse --show-toplevel 2>/dev/null)" || {
        echo "cdwt: not in a git repo" >&2
        return 1
    }
    local repo
    repo="$(dirname "$(git -C "$toplevel" rev-parse --git-common-dir)")"
    local target="$repo/.claude/worktrees/$1"
    [ -d "$target" ] || {
        echo "cdwt: no worktree at $target" >&2
        return 1
    }
    cd "$target" || return 1
}

_cdwt() {
    local toplevel
    toplevel="$(git rev-parse --show-toplevel 2>/dev/null)" || return
    local repo
    repo="$(dirname "$(git -C "$toplevel" rev-parse --git-common-dir)")"
    local wt_dir="$repo/.claude/worktrees"
    [ -d "$wt_dir" ] || return
    local names
    names="$(ls "$wt_dir" 2>/dev/null)"
    COMPREPLY=( $(compgen -W "$names" -- "${COMP_WORDS[1]}") )
}
complete -F _cdwt cdwt
