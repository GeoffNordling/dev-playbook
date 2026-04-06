#!/usr/bin/env bash
# Add dev-playbook tools/bin to PATH in the current shell's rc file.
set -euo pipefail

TOOLS_BIN="$(cd "$(dirname "$0")" && pwd)/bin"
chmod +x "$TOOLS_BIN"/*

# Detect rc file
if [ -n "${ZSH_VERSION:-}" ] || [ "$(basename "$SHELL")" = "zsh" ]; then
    RC="$HOME/.zshrc"
else
    RC="$HOME/.bashrc"
fi

LINE="export PATH=\"$TOOLS_BIN:\$PATH\""

if grep -qF "$TOOLS_BIN" "$RC" 2>/dev/null; then
    echo "PATH already configured in $RC"
else
    echo "" >> "$RC"
    echo "# dev-playbook tools" >> "$RC"
    echo "$LINE" >> "$RC"
    echo "Added dev-playbook tools/bin to PATH in $RC"
fi

echo "Run 'source $RC' or open a new shell to activate."
