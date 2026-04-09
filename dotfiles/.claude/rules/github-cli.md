# GitHub CLI Usage

## Reading issues and PRs

Use the REST API to read issue or PR details:

```bash
gh api repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/issues/N \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['title']); print(); print(d['body'])"
```

Use `gh issue list` and `gh pr list` for listing.
