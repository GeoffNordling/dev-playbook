# Ideas

Unprocessed ideas — things worth exploring but not yet committed to. Each entry is a candidate for further research or implementation.

## Idea List

### MetaSync: incident learning for meta-knowledge
Build on the existing `/orient` skill with two additional capabilities:

1. **Incident reporting.** The user can report process failures ("my green agent launched into implementation without proposing a user test first") and the skill helps diagnose which skill, standard, or instruction needs strengthening to prevent recurrence.

2. **Event log.** Every incident and the resulting fix are logged with timestamps so the user can see how the system of skills and standards is developing over time — what broke, what was tightened, and whether the same class of failure recurs.

The goal is a feedback loop: observe a failure → trace it to a gap in meta knowledge → patch the gap → log the event → verify the class of failure declines.

### Prior art research: spec parsing
Before finalizing a custom spec format, investigate existing standards and libraries (TLA+, Alloy, Cucumber/Gherkin, RFC 2119, OpenAPI, etc.) that already handle deterministic parsing and testing of specifications.

### Unit tests for specs
Implement machine-parsable specs that can be deterministic tested, so you can run unit tests against specification documents.

### ClaudeWatch: edge case escalation tracking
Count the edge cases the model surfaces to the human and track the distribution of human responses (valid concern vs. noise). Detect whether the model is manufacturing edge cases to please the user rather than finding real ones.

### Idea triage agent
A lightweight agent that can be dispatched to quickly explore an idea, check prior art, estimate feasibility, and report back whether it's worth investing time in. Solves the bottleneck of generating ideas faster than you can evaluate them.

### Code Quality Skill
The green agent gave me horrible, monolithic, nested, complicated, mindlessly stupid code today, and I had to reject it multiple times and tell it to give me nice code where single functions did single things. I can't believe I had to tell it that, but apparently I still do, even with opus 4.6. A skill or a document that reminds the agents of this and automatically tells them to fix their code quality.