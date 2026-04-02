---
name: commit-push
description: Commit all changes and push to remote
disable-model-invocation: true
---

# Commit-Push

Commit all changes and push.

If the working directory is /Volumes/workplace/RDMWorkspace/src/RDMCore, then immediately reject this skill and escalate to user. We should never run this skill while workiong oin the RDMCore project.

## Output discipline

Be quiet. Execute the workflow steps without narrating each one. Only speak up if something looks unexpected or needs user input. If everything is normal, go straight from tools to commit+push with minimal commentary.

## Workflow

1. Run `git status` to see all changes
2. Run `git diff --stat` to see which files changed and by how much
3. If any file in the stat output was not expected to change, run `git diff <file>` on that file only to investigate before proceeding
4. Run `git log --oneline -3` to match commit message style
5. Stage all relevant files (exclude obvious temp files, secrets, etc.)
6. Create a concise commit message summarizing the changes
7. Commit and push all in the same command.

## Commit Message Format

- Short summary line describing what was done
- Blank line
- Bullet points for multiple changes (if needed)

## Safety

- Never commit .env files, credentials, or secrets
- Ask user before committing if changes look unusual or unintended
