# Design It Twice

How a load-bearing public surface is settled: propose it several ways in
parallel, then pick. Read only when §2 settled that the surface *is*
load-bearing — written against by code you don't control, or costly to change
once shipped.

## The fan-out

Spawn three or four Opus subagents in one message, one per axis. Each gets
the same work and the same reading, and returns a proposed surface with its
costs.

Each is asked for a **radically different** design. Four proposals that
converge on the same shape cost four agents and answer nothing; the axes
exist to force them apart.

| Axis | The brief it works under |
|---|---|
| Minimize surface | Expose the least that satisfies the issue; push everything else behind it. |
| Maximize flexibility | Expose what leaves the most future moves open, and name what that costs today. |
| Common caller | Design from the call sites that exist — what reads best where it is actually used. |
| Ports and adapters | Split the surface into a port the domain owns and adapters at the edges. |

Four axes when the surface is genuinely contested; three when one axis is
obviously inapplicable — a module with no edges has no ports-and-adapters
answer worth paying for.

## The comparison

Judge the returns in this order:

- **Depth.** How much implementation each interface hides. A surface that
  restates its implementation is shallow whatever else it gets right — the
  first thing the module-design standard asks for.
- **Locality.** How much of a plausible future change stays in one place.
  Spread a change across three modules and the seams are in the wrong spots.
- **Seam placement.** Where each seam falls, and whether it falls where
  something actually varies. One adapter is a hypothetical seam; two is a
  real one — a seam nothing varies across is cost with no return.

The winner is usually not one proposal intact: take its shape and graft the
better ideas from the runners-up, then say which came from where so the
reasoning survives into the brief.

## What reaches the issue

The winner's seams are what you carry into §6's sketch, and the axes you
rejected are its alternatives weighed. Nothing else from the fan-out
survives — the proposals themselves are working material.
