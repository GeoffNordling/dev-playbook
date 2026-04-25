# Design Layer

## Purpose

Functional requirements describe what the system does, not how. The space
of correct implementations of any behavioral requirement is enormous — many
entity shapes, many public surfaces, many algorithms, many sequencings of
operations all satisfy the same requirement.

An agent writing code directly from a functional requirement picks
somewhere in that space. The pick is often not where a human with taste,
project context, and vision would have landed. Code that meets the
requirement but takes the wrong shape — wrong abstractions, wrong API,
wrong ordering — is technically correct and practically wrong.

The design layer is where the human narrows the space. A `dsn` encodes
intuition the agent does not have on its own — what reads well in this
codebase, what the project is converging toward, what trade-off this team
prefers, what other parts of the system already do. The agent reads the
`dsn` collection before writing code and treats each item as a constraint
on the implementation.

A `dsn` lives at the **public boundary** — what callers see, what
downstream code reads, what subsequent stages depend on. Decisions that
live entirely inside a module (internal helpers, local data structures,
file layout, control flow) belong to the implementation phase and stay
with the agent.