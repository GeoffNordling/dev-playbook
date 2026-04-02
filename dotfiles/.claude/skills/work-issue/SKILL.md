---
name: work-issue
description: Pick up development work on a GitHub issue
disable-model-invocation: true
---

# Work Issue

Pick up development work on a GitHub issue. The user provides free-form input: an issue number, URL, or description, plus any optional context or ideas.

## Workflow

1. **Read the standards.** Determine the platform and read both standards:
   - **Mac (Darwin):** `/Volumes/workplace/dev-playbook/standards/development-workflow.md` and `repo-documentation.md`
   - **WSL:** `~/workspace/dev-playbook/standards/development-workflow.md` and `repo-documentation.md`

2. **Find the issue.** Use `gh` to read the referenced GitHub issue. If the user gave a description rather than a number, search to find it.

3. **Check for existing work.** Follow the Session Handoff sequence from the development workflow standard.

4. **Orient on the project.** Read the repo documentation files as prescribed by the repo documentation standard. Check whether the project has a `specs/` directory (indicating spec-driven development).

5. **Present findings.** Summarize the issue, any existing work, relevant project context, and a suggested approach.

6. **Scaffold.** Unless the user said to skip, set up the branch and draft PR per the development workflow standard.

7. **Wait for user direction.** Do not start coding. If the project follows SDD (`specs/` exists), note that the next step is for the user to update the spec with requirements for this issue.
