"""The impure boundary: batched GraphQL fetch from GitHub via gh.

Everything deterministic (query building, parsing, pagination, error
handling) is separable and tested; only the gh subprocess call is not.
"""

import json
import re
import subprocess
import time
from collections.abc import Callable
from datetime import datetime
from typing import Literal, cast

from workflow_state_data.core import IssueData, LabelEvent
from workflow_state_data.phases import CANONICAL_LABELS

_EVENT_ACTIONS = {"LabeledEvent": "labeled", "UnlabeledEvent": "unlabeled"}

_TIMELINE_ARGS = "itemTypes: [LABELED_EVENT, UNLABELED_EVENT], first: 250"

_TIMELINE_FIELDS = """
    pageInfo { hasNextPage endCursor }
    nodes {
      __typename
      ... on LabeledEvent { label { name } createdAt }
      ... on UnlabeledEvent { label { name } createdAt }
    }
"""

_ISSUE_FIELDS = f"""
  id
  number
  title
  state
  createdAt
  closedAt
  repository {{ nameWithOwner }}
  labels(first: 50) {{ pageInfo {{ hasNextPage }} nodes {{ name }} }}
  comments {{ totalCount }}
  timelineItems({_TIMELINE_ARGS}) {{
{_TIMELINE_FIELDS}
  }}
"""

SEARCH_QUERY = f"""
query($q: String!, $cursor: String) {{
  search(type: ISSUE, query: $q, first: 100, after: $cursor) {{
    issueCount
    pageInfo {{ hasNextPage endCursor }}
    nodes {{
      ... on Issue {{
{_ISSUE_FIELDS}
      }}
    }}
  }}
}}
"""

TIMELINE_QUERY = f"""
query($id: ID!, $cursor: String) {{
  node(id: $id) {{
    ... on Issue {{
      timelineItems({_TIMELINE_ARGS}, after: $cursor) {{
{_TIMELINE_FIELDS}
      }}
    }}
  }}
}}
"""


class GitHubError(Exception):
    """Any API/auth/pagination failure — fail loud, never partial output."""


def gh_graphql(
    query: str,
    variables: dict,
    runner: Callable = subprocess.run,
    sleep: Callable[[float], None] = time.sleep,
) -> dict:
    """Run one GraphQL query via gh, retrying once after a rate limit."""
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        if value is not None:
            cmd += ["-f", f"{key}={value}"]
    result = runner(cmd, capture_output=True, text=True)
    if result.returncode != 0 and _is_rate_limited(result.stderr):
        sleep(_retry_after_seconds(result.stderr))
        result = runner(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise GitHubError(f"gh api graphql failed: {result.stderr.strip()}")
    payload = json.loads(result.stdout)
    if payload.get("errors"):
        raise GitHubError(f"GraphQL errors: {payload['errors']}")
    return cast(dict, payload["data"])


def _is_rate_limited(stderr: str) -> bool:
    """Whether gh stderr indicates a rate-limit (HTTP 429) failure."""
    return "http 429" in stderr.lower() or "rate limit" in stderr.lower()


def _retry_after_seconds(stderr: str) -> float:
    """Extract the Retry-After delay from gh stderr, defaulting to 60s."""
    match = re.search(r"retry-after:?\s*(\d+)", stderr, re.IGNORECASE)
    return float(match.group(1)) if match else 60.0


def fetch_issues(
    repos: list[str] | None,
    run_query: Callable[[str, dict], dict] = gh_graphql,
) -> list[IssueData]:
    """Fetch all workflow issues (account-wide or per repo) as IssueData."""
    search_query = build_search_query(repos)
    issues: list[IssueData] = []
    cursor: str | None = None
    while True:
        data = run_query(SEARCH_QUERY, {"q": search_query, "cursor": cursor})
        search = data["search"]
        issues.extend(
            parse_issue_node(_with_complete_timeline(node, run_query))
            for node in search["nodes"]
        )
        if not search["pageInfo"]["hasNextPage"]:
            # The search connection hard-caps at 1000 results and signals it
            # only as hasNextPage: false — never partial output, so compare
            # against the full match count.
            if len(issues) < search["issueCount"]:
                raise GitHubError(
                    f"search returned {len(issues)} of {search['issueCount']} "
                    f"matching issues (GitHub caps search at 1000 results); "
                    f"narrow the scope with --repo"
                )
            return issues
        cursor = search["pageInfo"]["endCursor"]


def _with_complete_timeline(node: dict, run_query: Callable[[str, dict], dict]) -> dict:
    """Follow timeline pagination until the issue node's events are complete."""
    items = node["timelineItems"]
    event_nodes = list(items["nodes"])
    page_info = items["pageInfo"]
    while page_info["hasNextPage"]:
        data = run_query(
            TIMELINE_QUERY, {"id": node["id"], "cursor": page_info["endCursor"]}
        )
        items = data["node"]["timelineItems"]
        event_nodes.extend(items["nodes"])
        page_info = items["pageInfo"]
    return {**node, "timelineItems": {"nodes": event_nodes}}


def parse_issue_node(node: dict) -> IssueData:
    """Map one GraphQL issue node to IssueData."""
    # The canonical label set is small (~15), so one page always suffices —
    # but a truncated list would pass the scope gate on partial data, so
    # uphold the never-partial-output contract here too.
    if node["labels"]["pageInfo"]["hasNextPage"]:
        raise GitHubError(
            f"issue {node['repository']['nameWithOwner']}#{node['number']} "
            f"has more than 50 labels; label list would be truncated"
        )
    events = tuple(
        LabelEvent(
            action=cast(
                Literal["labeled", "unlabeled"], _EVENT_ACTIONS[item["__typename"]]
            ),
            label=item["label"]["name"],
            at=datetime.fromisoformat(item["createdAt"]),
        )
        for item in node["timelineItems"]["nodes"]
    )
    return IssueData(
        repo=node["repository"]["nameWithOwner"],
        number=node["number"],
        title=node["title"],
        state=cast(Literal["open", "closed"], node["state"].lower()),
        created_at=datetime.fromisoformat(node["createdAt"]),
        closed_at=(
            datetime.fromisoformat(node["closedAt"]) if node["closedAt"] else None
        ),
        labels=tuple(label["name"] for label in node["labels"]["nodes"]),
        events=events,
        comment_count=node["comments"]["totalCount"],
    )


def build_search_query(repos: list[str] | None) -> str:
    """Build the issue search string: scope qualifier + canonical labels.

    Matching any canonical workflow label (not just phase:) keeps limbo
    issues — phase label removed without replacement — fetchable via the
    metadata labels they retain. Residual blind spot: an issue that lost
    its phase label before metadata labels were ever stamped matches
    nothing and stays invisible. Note the default user:@me scope covers
    only repos the user owns, not org-owned or collaborator repos.
    """
    scope = (
        " ".join(f"repo:{repo}" for repo in repos) if repos is not None else "user:@me"
    )
    labels = ",".join(f'"{label}"' for label in sorted(CANONICAL_LABELS))
    return f"is:issue {scope} label:{labels}"
