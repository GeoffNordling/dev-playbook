---
name: sound-effect-feedback
description: Record sound feedback
disable-model-invocation: true
model: haiku
effort: low
argument-hint: "[feedback]"
allowed-tools: Bash(git *)
---

# Sound Effect Feedback

Record feedback about a sound effect for later processing.

## Feedback: $ARGUMENTS

## Workflow

1. Read the feedback file at `/home/gmnordling/workspace/sounds/problems-with-sounds.md`
2. Append the feedback above as a new bullet point, preserving the existing format
3. Commit and push the file: `cd /home/gmnordling/workspace/sounds && git add problems-with-sounds.md && git commit -m "sound feedback: <brief description>" && git push`
4. Confirm to the user that feedback was recorded and pushed

## Notes

- The feedback is natural language — interpret it as-is and write it as a concise bullet
- Do not process or act on the feedback beyond recording it; this file is reviewed separately later
