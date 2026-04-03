# Ideas

Unprocessed ideas — things worth exploring but not yet committed to. Each entry is a candidate for further research or implementation.

## Idea List

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

### Context Switch Primer Skill
A generic skill invokable at any time in any context that helps the human quickly recover from a hard context switch. When invoked, it produces a structured primer covering: (1) pertinent facts about the current project/task, (2) next steps that were in flight, and (3) a summary of notable things that happened earlier in the conversation. Goal: get back up to speed fast without re-reading the full chat history.