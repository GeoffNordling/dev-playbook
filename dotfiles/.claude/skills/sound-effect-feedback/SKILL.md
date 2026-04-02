---
name: sound-effect-feedback
description: Record feedback about a sound effect for later processing
disable-model-invocation: true
---

# Sound Effect Feedback

Record feedback about a sound effect (too loud, too quiet, wrong vibe, etc.) so it can be processed later.

## Workflow

1. Read the feedback file at `/home/gmnordling/workspace/sounds/problems-with-sounds.md`
2. Append the user's feedback as a new bullet point, preserving the existing format
3. Commit and push the file: `cd /home/gmnordling/workspace/sounds && git add problems-with-sounds.md && git commit -m "sound feedback: <brief description>" && git push`
4. Confirm to the user that feedback was recorded and pushed

## Notes

- The feedback is natural language — interpret it as-is and write it as a concise bullet
- Do not process or act on the feedback beyond recording it; this file is reviewed separately later
- The argument passed to this skill is the feedback string to record
