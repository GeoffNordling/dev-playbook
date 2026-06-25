# transcript-export — reference prototype (throwaway)

Proves the approach for the real tool, `tools/bin/transcript-export`.

`render_transcript.py` renders a Claude Code session to a plain-text transcript
using the `agentsview` CLI: every message in order, each tool call with its
arguments, tool output bodies recovered from `agentsview session export`, and
sub-agents recursed and nested inline.

**Status: prototype.** Reference it while implementing the real tool, then
**delete this whole directory once the real tool exists.**

Run:

    python3 render_transcript.py <out_dir> <session_id> [<session_id> ...]
    python3 render_transcript.py <out_dir> --recent N

See `GOAL.md` at the repo root for the full goal.
