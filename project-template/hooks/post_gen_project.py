"""Post-generation hook: remove optional directories and initialize the project."""

import os
import shutil
import subprocess

# Remove directories the user opted out of
layout = "{{ cookiecutter.project_layout }}"

if "package" not in layout:
    shutil.rmtree("src", ignore_errors=True)

if "scripts" not in layout:
    shutil.rmtree("scripts", ignore_errors=True)

if "notebooks" not in layout:
    shutil.rmtree("notebooks", ignore_errors=True)

# Initialize git repo
subprocess.run(["git", "init", "-b", "main"], check=True)
subprocess.run(["git", "add", "."], check=True)
subprocess.run(["git", "commit", "-m", "Initial commit from project-template"], check=True)

# Create uv environment
if shutil.which("uv"):
    subprocess.run(["uv", "sync"], check=True)

# Install pre-commit hooks
if shutil.which("pre-commit"):
    subprocess.run(["pre-commit", "install"], check=True)

# Final reminder: the agent-skills configuration is not seeded by this template;
# it is scaffolded by /setup-matt-pocock-skills inside Claude Code.
print()
print("=" * 64)
print(" Next step: open this repo in Claude Code and run:")
print()
print("     /setup-matt-pocock-skills")
print()
print(" This scaffolds docs/agents/* and the Agent skills block in")
print(" CLAUDE.md. Until then, CLAUDE.md instructs agents to STOP.")
print("=" * 64)
