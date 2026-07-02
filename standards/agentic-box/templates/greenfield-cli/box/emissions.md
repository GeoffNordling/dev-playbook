---
type: Box Artifact
title: "Emissions: sessionxml"
description: Required deliverables the sessionxml agent hands back — DEVIATIONS.md and UPSTREAM.md
---

# Emissions

Required in tools/sessionxml/ before the gate passes:

DEVIATIONS.md

    Every notable behavior NOT pinned by contract or fixtures:
    | file:line | behavior chosen | resolution rule applied |
    An empty table is valid. An absent file is not.

UPSTREAM.md — the upward channel; recommendations, not tasks

    ## With more fixtures I would test        (risks you couldn't cover)
    ## Contract changes I would propose       (and why; you may not make them)
    ## Known weak points                      (file:line where you'd look first
                                               if this breaks in the field)

    Empty sections are valid. An absent file is not.
