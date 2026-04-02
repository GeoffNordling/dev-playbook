# Triage

Work through the flagged improvement backlog with the user.

## Setup

1. Read the backlog: `/Volumes/workplace/dev-playbook/flagged_backlog/log.jsonl`
2. Read both meta-repo READMEs for context:
   - `/Volumes/workplace/dev-playbook/README.md`
   - `/Volumes/workplace/dev-tools/README.md`

## Workflow

Present every open entry to the user with a suggested functional area (standards, agent config, project template, dev-tools package, etc.). Then stop and wait — the user drives triage.

For each flag the user addresses, either:
- **Fix it** in the current session (update a standard, add a rule, modify a tool, etc.)
- **Promote it** to the ideas backlog at `/Volumes/workplace/dev-playbook/ideas/README.md`

After a flag is resolved or promoted, delete its line from `log.jsonl`. The file is a queue, not an archive — git history is the audit trail.
