# Commit-Push-Fast

Stage everything, commit, push. No analysis, no narration.

## Steps

1. `git add -A`
2. `git diff --cached --stat` to build a one-line commit message
3. `git commit -m "<message>"` then `git push`

Never commit .env files, credentials, or secrets. Otherwise, commit everything without hesitation.
