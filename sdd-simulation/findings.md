# Findings

Observations about the workspace spec standard surfaced while running the
simulation. Each entry names the friction; resolutions (if any) belong in
the standard itself or in its ADRs.

## 1. Cross-module behavioral properties have no clean home

`req~serialize.round-trip~0` spans serialize + deserialize. We parked it
on serialize but it could equally live on deserialize or as its own feat.
The standard's hierarchical chain doesn't accommodate "joint" properties.

## 2. Lossless parse + standard-conformant render does not imply round-trip

We expected `req~deserialize.fidelity~0` + `req~serialize.conformance~0`
to imply round-trip, but they don't — formatting choices at render time
can lose content the parser preserved. Round-trip is its own commitment.

## 3. Standard mandates `index.md` but is silent on tooling

Spec-standard §8 says folder-form specs `SHALL` contain `index.md`. It
is framed for human/agent readers. Whether tools should consult it is
left unstated; the simulation chose not to.

## 4. Each module mapped 1:1 to a feat

In this simulation, every module has exactly one feat. The standard
doesn't require this and it isn't universal — but for small focused
libraries it appears to be the natural shape, because feat
decomposition and module decomposition both follow "one cohesive
capability per unit."
