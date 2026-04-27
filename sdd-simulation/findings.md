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

## 4. Cross-module dsn coverage navigates poorly

`dsn~model.spec-item~0` and `dsn~model.item-id~0` live in `model.md`
(the types they pin live in the model module) but cover
`req~deserialize.fidelity~0` (in `deserialize.md`). The chain is
well-formed, but a reader of `deserialize.md` sees `Needs: dsn` and
gets no signpost that the dsns are in another file. The standard
admits cross-file coverage but offers no convention for navigating
it.

## 5. Prose enumeration: duplication vs separate-dimension commitment

When drafting `dsn~model.spec-item~0`, the field enumeration first
appeared in `Comment:` — duplicate of `Interface:`, no validator,
rot-prone. We removed it. But the field list also functions as a
**Data-dimension** commitment that is conceptually distinct from the
**API-Shape** commitment expressed by `Interface:`, so we re-added
the enumeration in `Description:` as a normative bulleted list.

Lesson: prose that duplicates `Interface:` is rot-prone when it is
illustrative (`Comment:`) but normative when it commits to a
different design dimension (`Description:`). The standard does not
draw this line explicitly; authors have to.

## 6. `Interface:` line goes stale when its upstream standard evolves

`dsn~model.spec-item~0`'s `Interface:` enumerates every field of
`SpecItem`, where each field corresponds to a keyword defined in
`spec-standard.md`. `Interface:` validation checks code-against-dsn,
but nothing checks dsn-against-standard. If the standard adds a
keyword, the dsn must be revised manually. This is structural — any
spec whose contract is parameterized over an external evolving
standard inherits this manual sync — and worth flagging as a limit
of in-spec validation rather than a fixable gap.

## 7. Each module mapped 1:1 to a feat

In this simulation, every module has exactly one feat. The standard
doesn't require this and it isn't universal — but for small focused
libraries it appears to be the natural shape, because feat
decomposition and module decomposition both follow "one cohesive
capability per unit."
