"""Command-line entry for transcript-export.

This scaffold only prints usage. Session selection (explicit ids, --recent N,
--all), AgentsView access, and XML rendering arrive in later tasks; see PLAN.md
for the authoritative design.
"""

USAGE = "usage: transcript-export <out_dir> <session_id>..."


def main(argv: list[str]) -> int:
    """Print usage and exit zero. Real selection/rendering land in later tasks."""
    print(USAGE)
    return 0
