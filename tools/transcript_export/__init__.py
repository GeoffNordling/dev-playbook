"""transcript-export — render a Claude Code session into an XML transcript.

Reads only AgentsView's parsed messages API (session list / get / messages) and
emits a faithful, high-signal XML transcript per session. See PLAN.md at the repo
root for the authoritative design.
"""
