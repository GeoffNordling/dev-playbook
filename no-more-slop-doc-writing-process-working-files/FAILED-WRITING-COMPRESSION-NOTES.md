# Failed-Writing Compression Notes

## Situation

This branch (`no-more-slop-doc-writing-process`) spins off the
`no-more-slop` branch at commit `5974223` — the commit that captures
Claude's unaided draft of `standards/harness/runbook-conventions.md`,
before the user's corrections. The commit before it, `923c206`, is the
state just before the write began. `git diff 923c206..5974223` is
therefore the negative case: a document written by Claude exactly as
Claude wrote it. The user's subsequent fix-up iterations were committed
on `no-more-slop` and are deliberately not part of this pair.

The goal of this branch: develop a generalized method by which Claude
can write a significant, large document without failing in the usual
ways. The user reports that the failure classes below recur essentially
every time Claude writes a document, and have for months. The
runbook-conventions.md episode is the worked example — representative,
not special.

## What we knew and intended when the write began

- Task: parts 3+4 of the stage-1 plan merged into one deliverable —
  replace `skill-conventions.md` with `runbook-conventions.md`, covering
  both runbook kinds (skill bundles, agent definitions), because the
  overlap between the two planned files was class-level, not incidental.
  Structure approved before writing: opening (class + grammar split),
  shared core, Skills, Agents; `git mv` for history; ~12 inbound link
  files to retarget.
- Pre-write investigation had established: the 9-agent corpus uses
  exactly `name, description, tools, model, effort` (two omit `tools`);
  part-4 trims to fold in (`argument-hint` retired, checklist deleted,
  `user-invocable` rationale corrected — it exists upstream, we ban it
  because `disable-model-invocation` is our single switch);
  `allowed-tools` pre-approves rather than restricts.
- The user pre-emptively made Claude confirm the boundary: this file is
  structural only — voice/craft/grammar live in grammar.md,
  writing-for-agents, and the prose standards. Claude confirmed it, then
  still wrote meta-commentary into the file.
- Standing rulings from part 2 (grammar.md's own review loop) that
  should have governed this draft and didn't: no corpus-specific
  examples that go stale; minimal text ("I am not able to read all
  this"); never restate what another file owns; write the future state
  as arrived (no third-party anything); don't mention what isn't ruled.
  Every one of these had to be re-issued against the new file.
- A known duplicate Claude failed to integrate: cross-references.md and
  skill-conventions.md already pointed at each other for the
  no-fixed-root rule — a split-brain already visible before the write.
  Claude ported the duplication forward verbatim; the user had to find
  it and ask where it should live. Same pattern with files.md already
  owning the harness-owned/not-OKF fact.
- Docketed for later, unrelated to this branch's goal but part of the
  session state: deslopper.md's repo-absolute links break outside
  dev-playbook; `set-auditor`/`set-deslopper` duplicated in two agent
  dirs; plan part 5 = detector work; part 6 = corpus scrub.

## Catalog of the user's negative feedback, generalized

Issued in this order against the draft:

1. Don't point at external official docs for features not covered here.
2. Don't say "this standard is binding / the lint enforces it" —
   enforcement meta-commentary out.
3. Don't describe relationships to craft skills (the writing-for-agents
   paragraph) — out.
4. Challenged a paragraph as duplicate vs. home — it was a duplicate
   (files.md / file-roles.md own it) — out.
5. Remove all references to existing skills/paths as examples; "say the
   rules and the classes they apply to. It's that simple."
6. Don't mention things we've decided won't exist (third-party skills).
7. No negative examples / what-not-to-do instructions without a specific
   reason or user approval (the `user-invocable` bullet).
8. Coined transitions confuse ("Beyond the shared four"); and whole
   rows explained how Claude Code operates instead of how we write —
   reduce to rules only.
9. A section that near-verbatim duplicates another standard belongs in
   that standard (Cross-references — moved to cross-references.md).
10. Verdict: "You did such a bad job writing this file… it's always bad
    in the same way."

The meta-failure tying them together: each ruling class was already
issued earlier in the same session against grammar.md, and Claude did
not carry it forward to the next document — every rule got re-litigated
per file.

## State recovery

- Anchor commits: `923c206` (before the write), `5974223` (the unaided
  draft; this branch's base). Both on the `no-more-slop` lineage,
  pushed.
- The user's post-draft refinement commits live on `no-more-slop`, not
  here.
- This worktree:
  `/home/geoff/workspace/dev-playbook/.claude/worktrees/no-more-slop-doc-writing-process`.
- File of interest in the anchor diff:
  `standards/harness/runbook-conventions.md` (the 15 retargeted link
  sites in the same diff were mostly fine — the failure is concentrated
  in the new file itself).
