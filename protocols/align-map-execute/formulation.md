# Align, Map, Execute

A frontier-invariant protocol for human-agent collaborative work.
The human has a task whose scope exceeds what they can hold in mind.
The agent can search that scope, but the human cannot evaluate the raw
results. This protocol compresses the task into a stream of human-sized
decision points: align on intent, build a low-dimensional structure of
the problem, then execute while minimizing demands on human attention.

---

## Base Loop

The simplest human-agent interaction loop:

1. The human states what they want.
2. The agent and human iterate toward shared understanding.
3. The agent acts; the human evaluates.
4. Repeat until the objective is satisfied.

Every productive human-agent session is an instance of this loop.
Two problems make it hard: the task is too large for the human to
hold in mind, so the human cannot evaluate the agent's raw results;
and the agent's effectiveness depends on its understanding of what
the human truly wants. This protocol addresses both — compressing
the agent's findings into objects small enough for the human to
evaluate, and iteratively refining the agent's model of human intent.

---

## Primitives

#### Latent

| Symbol | Name | Description |
|--------|------|-------------|
| $H$ | Human intent | The human's true intent — latent, fixed, never fully observable |

#### Human-provided

| Symbol | Name | Description |
|--------|------|-------------|
| $O$ | Objective | The explicit statement of what the task should accomplish — the human's best articulation of $H$, communicated precisely enough for the agent to act on |
| $S$ | Scope | The boundary of the task — what is in and what is out: which artifacts to examine (often a codebase) and to what depth (level of abstraction) |
| $F$ | Facets | The dimensions along which the human evaluates the territory — what the human cares about. Each facet becomes a column of $M$ |
| $R$ | References | Documents for agent context and/or normative standards |

#### Constructed

| Symbol | Name | Description |
|--------|------|-------------|
| $A$ | Alignment | The shared operating model — the human and agent's working approximation of $H$, encoding how they have agreed to work: quality criteria, what to bring back for evaluation. Constructed in Stage 1 from $O$, $S$, $F$, $R$; persisted in the protocol state document, mutable throughout |
| $M$ | Map | The map of the territory — a matrix whose columns are the facets in $F$ and whose rows are regions discovered by surveying $S$. Each cell is a descriptor: what is there, not whether it is good. Constructed in Stage 2, persisted in the protocol state document, mutable throughout |

#### Operational

| Symbol | Name | Description |
|--------|------|-------------|
| $C_a$ | Agent context | Token budget for a single agent pass; discrete, finite. Degrades under load — a leaner context produces sharper reasoning |
| $C_h$ | Human context | What a human can hold in mind simultaneously; latent, finite. Smaller than $C_a$ for raw information, richer for abstraction and judgment. Same degradation applies |
| $\kappa$ | Agent capability | Effective capability of the agent for this task: $\kappa(O, S, F, R, C_a)$. Not fixed — the same model has different $\kappa$ for different tasks. Improves as the frontier advances |
| $Q^\ast$ | Quality threshold | The minimum acceptable quality of the agent's work at each step — latent, never directly observable by either party |
| $\sigma^\ast$ | Optimal step size | The latent optimal amount of work per iteration — a property of the task/agent/alignment configuration, not a human preference. Neither party knows $\sigma^\ast$ |
| $\sigma$ | Step size | How far the agent goes any time it is operating on its own before checking back: $\sigma = f(\kappa)$. Applies at whatever scale the agent happens to be working. Higher capability, bigger steps. $\sigma$ bounds the accumulated drift between the agent's working model and $H$ — the human cannot observe quality directly, so smaller $\sigma$ limits the risk of unobserved degradation |
| $L$ | Intent calibration log | Persistent record of human direction — each entry captures a finding the agent raised, the human's response, and the implication for future work. Organized by $F$. Survives context resets; enables a fresh agent to reconstruct $A$ |

### Artifact constraints

Because $\dim(S) \gg C_h$, $F$, $A$, and $M$ must each be:

- **Low-dimensional.** Each is low-dimensional relative to $S$ —
  captures only what matters, not everything that could be said.
- **Bounded.** Fits within $C_h$ — the human can read and evaluate
  it in a single pass.
- **Falsifiable.** Each is falsifiable against its referent: $F$
  and $A$ against $H$; $M$ against $S$ conditioned on $F$ and $A$.
- **Complete.** $F$, $A$, and $M$ are jointly a sufficient basis for
  executing the work. $F$ defines how to focus attention. $A$ addresses
  intent. $M$ inventories the territory along those
  dimensions. The decomposition of $H$ is lossy but complete.

---

## Stage 1: Build the Shared Alignment

The human provides $O$, $S$, $F$, and $R$. The agent forms an
initial alignment state $A$:

$$A_0 = f(O,  S,  F,  R)$$

$A^\ast$ is the shared operating model — how the human and agent have
agreed to work: what quality criteria to apply, what the agent should
bring back for evaluation. $A^\ast$ persists
as a section of the protocol state document and governs all
subsequent work.

The agent asks clarifying questions to refine its understanding.
Each question-response pair updates the alignment:

$$A_{i+1} = A_i + \Delta_i$$

This continues until the human signals confidence. Let $A^\ast$ denote
the approved alignment.

---

## Stage 2: Build the Map

The agent surveys $S$ and produces $M$ — the map of the territory.
$F$ defines the columns (the dimensions of evaluation). The survey
of $S$ reveals natural regions — contiguous areas that form coherent
units of work — which become the rows. Each cell is a descriptor:
what is there, with counts where useful. If a cell requires detailed
reading to evaluate, the region is too large or the facet too broad.

$M$ is a matrix: one row per region, one column per facet. Each
cell $M_{wf}$ describes region $w$ along facet $f$.

The agent produces $M$ by applying a projection operator $\pi$ to
$S$, conditioned on $A$ and $F$:

$$\pi : (A,  F,  S)  \to  M$$

$$M_0 = \pi(A^\ast,  F,  S)$$

$\pi$ must be faithful enough that **approving both $A$ and $M$ is
equivalent to approving the operating model and the exhaustive
survey**.

The human evaluates $M$ and provides feedback. Each round of
feedback updates $A$, $M$, or both:

$$M_{j+1} = \pi(A_j + \Delta_j,  F,  S)$$

This continues until the human approves.

---

## Stage 3: Write the Protocol State Document

The agent persists the full protocol state as the **protocol state
document** (`PROTOCOL_STATE.md` in the project repo). It contains:

- $O$, $S$, $F$, $R$ — as refined through alignment
- $A$ — the shared alignment reached in Stage 1
- $M$ — the map produced in Stage 2
- $L$ — the intent calibration log, updated during Stage 4

The document is self-contained: any party reading it cold can
reconstruct the full protocol state without access to the
conversation that produced it.

---

## Stage 4: Execute

The agent and human collaborate to satisfy $H$ by executing work
across the regions of $M$, updating $A$ and $M$ as understanding
evolves. Execution has two convergence goals: converge on $H$ so
work is done correctly, and converge on $\sigma^\ast$ so work is done
efficiently.

### Work loop

1. **Select.** The human and agent select the next unit of work from
   $M$ — a region, a facet across regions, or a single cell.
2. **Analyze.** The agent reads and assesses the selection according
   to $A$, producing a structured analysis $a_k$.
3. **Present.** The agent surfaces $a_k$ to the human with enough
   context for independent verification.
4. **Direct.** The human evaluates $a_k$ and provides direction
   $d_k$ — a judgment, decision, or instruction.
5. **Act.** If $d_k$ requires action, the agent executes it.

### Step size

$\sigma$ governs how far the agent goes autonomously — in both
analysis and action — before checking back with the human. The
agent approximates $\sigma^\ast$ conservatively: it never knows
whether its output meets $Q^\ast$, so smaller $\sigma$ limits the
risk of unobserved drift from $A$. As $A$ improves, $\sigma$ can
grow — the agent earns autonomy.

### Intent calibration log

Each direction $d_k$ is a sample of $H$ — the human revealing
their intent through a concrete decision. The agent records these
in a persistent log $L$, organized by the facets in $F$. Each
entry captures the specific finding the agent raised, the human's
response, and the implication for future work.

$L$ survives context resets. A fresh agent reading $L$ reconstructs
$A$ without access to the conversations that produced it. Over
time, $L$ refines $A$, which in turn allows $\sigma$ to grow
toward $\sigma^\ast$.

After completing a unit of work, the human and agent update $M$
(status, structure) and may revise $A$ if the work revealed a gap
in the operating model. When traversing $M$ by facet, content
removed from one facet may belong in another; displaced content is
recorded in the protocol state document until the relevant pass.
The work is complete when $O$ is satisfied.
