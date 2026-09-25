---
type: General-Sheet
title: Story-Forge Survey
description: The specimen as four surveys found it on 2026-09-23 — the five parallel subsystems and their skeleton, the node types and how each is typed, the four written forms every edge takes, the rules and the lints, the nine runbooks, the gates, the derived state nothing surfaces, the declared-but-unchecked edges, the judgment residuals, the handoffs through the user, and the questions a person asks
---

# Story-Forge Survey

What four Sonnet agents and one read of the tree found in
`~/workspace/story-forge` on main at commit `3af571a`, 2026-09-23,
merged into one sheet so no later session sends them again.
Speculative, per
[Story-Forge Simulation](/workstreams/system/see/story-forge/WORKSTREAM.md),
and a specimen, not a spec: a path or a line here says where a thing
was seen, never that it is right. Every repo-relative path below is
under `~/workspace/story-forge/`.

## The shape

368 tracked files: 223 markdown, 56 Python, 31 text, 28 JSON, 8 YAML,
5 PDF. One directory per activity, five of them, and each has the
same skeleton:

| Activity | Population | Standard files | Lint | Skills |
| --- | --- | --- | --- | --- |
| stories | `stories/*.md`, `stories/tags.yaml`, `stories/projections/` | `standards/stories/{stories,tags}.md` | `stories-lint` | build-story |
| resume | `resume/*.md` and their PDFs | `standards/resume/resume.md` | `resume-lint` | build-bullet, resume-md-to-pdf, tailor-batch-resume |
| role-postings | `role-postings/<company>/…`, `role-postings/batches/` | `standards/role-postings/{assessment-records,fit-matrices}.md` | `role-postings-lint` | fetch-role-posting, assess-role-posting |
| interview-prep | `interview-prep/{playbooks,prep-units,interviews}/` | `standards/interview-prep/{interview-prep,prep-units,training-plans}.md` | `interview-prep-lint` | mock, plan-interview |
| unemployment-benefits | four YAML files under `unemployment-benefits/` | `standards/unemployment-benefits/unemployment-benefits.md` | `unemployment-lint` | unemployment-benefits-mode |

Each Standard directory also holds a `card.md` with four H2s, Define,
Audit, Enforce, Adopt: the Standard-Card dev-playbook has since
deleted. Each lint is a `uv run --script` shim under `scripts/` over
one module in `src/story_forge/`, and every rule id is a string
constant in that module in the form `<family>.<slug>`
(`stories_lint.py:39-45`, `role_postings_lint.py:50-56`,
`interview_prep_lint.py:69-81`, `unemployment_lint.py:32-38`,
`resume_lint.py:36-40`) and a backticked id in the Standard's prose.
That triple, typed population, Standard with ids, lint keyed by id, is
the doc-type system's Standard and verifier, grown rather than
designed. The domain vocabulary is `CONTEXT.md`, about 45 terms in six
clusters, each with an Avoid list; the type registry is the
`okf_types` block in `index.md`'s frontmatter, ten types.

The document ontology maps onto it without invention. Runbook: the
nine skills, all with `model` and `effort`, four with `arguments`, and
one span already in use, `{Never {Write posting content yourself}}` in
`.claude/skills/fetch-role-posting/SKILL.md`. Standard: the nine rule
files. Loop: no Loop document, and at least three loops in prose, the
tailor render-and-veto cycle, the mock check-and-grade cycle, the
weekly VEC rhythm. Guide: none.

## Node types

How a parser types each kind, and the count on main:

| Type | Typed by | Count | Content shape decided by |
| --- | --- | --- | --- |
| Story | `type: Story`, `stories/<id>.md` | 32 | `story_schema.py` pydantic model, `story_loader.py` seven fixed H2s |
| Projection | `type: Projection`, `stories/projections/*.md` | 1 | nothing: `stories_lint` globs `stories/*.md` non-recursively |
| Tag Registry | fixed path `stories/tags.yaml` | 1 | `tag_registry.py`: two disjoint lists, `role-specific` and `always-on` |
| Resume | `type: Resume`, `resume/<basename>.md` | 5 | `resume_lint.py`; body structure only as an HTML-comment table inside the master file |
| Role Posting | `.txt` under `role-postings/<company>/` or its `inbox/` | 27 | none, verbatim text with a `Source:` line |
| Stage JSON | `role-postings/<company>/assessments/<slug>.json`; merged when a `verdict` key is present | 27 | `save_scatter_results.py` key lists |
| Assessment-Record | `type: Assessment-Record`, `role-postings/<company>/<slug>.md` | 27 | `render_role_posting_record.py` emits the sections; `role_postings_lint.py` recomputes the fit summary byte-exact |
| Batch-Requirements-Profile | `type: Batch-Requirements-Profile`, `role-postings/batches/<batch>.md` | 2 | `aggregate_role_postings.py`, generated and diffed byte-exact |
| Playbook | `type: Playbook`, `interview-prep/playbooks/<round>.md` | 4 | `interview_prep_schema.py`; one `## Graded habits` H2 of `<round>.<slug>` ids |
| Interview-Record | `type: Interview-Record`, `interview-prep/interviews/<slug>/*.md` | 4 | frontmatter only |
| Training-Plan | `type: Training-Plan`, `interview-prep/interviews/<slug>/plan.md` | 1 | `interview_prep_schema.TrainingPlan`: `record`, `rounds`, `entries[]`, `gaps[]` |
| Prep-Unit | `type: Prep-Unit` in `interview-prep/prep-units/<name>/principles.md`; the directory is the name | 16 | `kind` hands-on or knowledge, `tags`, `rounds`, `core_for`, `builds_on`, `sessions[]` |
| Interviewer | `type: Interviewer` in `…/<name>/interviewer.md` | 16 | `habits[]`; `## Twist <n>` H2s numbered from 1 |
| Stub, Drill Harness | `*_drill.py`, `drill_harness.py`, hands-on units only | 8 each | banner and docstring literals, `interview_prep_lint.py:776-871` |
| Work-Search Contact, Weekly Claim, Task | rows of `work-search-log.yaml`, `weekly-claims.yaml`, `claim.yaml` | 18, 8, 1 | hand-rolled key checks in `unemployment_lint.py`, no pydantic |
| Benefit Week, Employer | not files: derived from a contact's `date` and its case-folded `employer` string | — | `unemployment_lint.py:91-113` |
| Skill | `.claude/skills/<name>/SKILL.md` | 9 | none in this repo; `playbook-lint` from dev-playbook |

Two grep hits per type are examples inside Standards prose, not data;
a frontmatter extractor over the whole tree must exclude `standards/`
or it over-counts.

## Edge forms

About twenty relation types, and every one is written in one of four
forms:

| Form | Relations seen |
| --- | --- |
| frontmatter list or key | Story `related_stories` (symmetric, `stories_lint.py:280-313`), `tags`, `supplemental_context`; Projection `sources`; Prep-Unit `builds_on` (acyclic), `sessions[].hit/missed` to habit ids; Interviewer `habits`; Training-Plan `record`, `entries[].prep_unit`, `entries[].rows` (byte-verbatim rows of the record's table); Assessment-Record `batch` |
| HTML comment | resume bullet `<!-- stories: a, b -->`; company section `<!-- unassigned stories (resume-eligible): … -->`; variant `<!-- tailored from: … -->` and `<!-- tailored to: role-postings/batches/<batch>.md -->` |
| path pairing | `<slug>.md` beside `<slug>.txt` beside `assessments/<slug>.json`; `prep-units/<name>/{principles,interviewer}.md` plus stub and harness when hands-on; `resume/<b>.md` beside `<b>.pdf` |
| YAML row | filing `employers_reported[]` to that week's contacts by employer string; contact `response` block; task `due_date` and `done` |

Three edges cross subsystems: Assessment-Record requirement rows carry
a `Tag` cell that must be in `stories/tags.yaml`; a Training-Plan's
`record` names an Assessment-Record; a Batch Variant's `tailored to`
names a Batch-Requirements-Profile. One edge is declared absent:
`CONTEXT.md` rules that Work-Search Contacts and role-postings never
join, and JPMorganChase and MORSE Corp appear in both. A fact base
carries that absence explicitly or a naive view draws the join.

So a first fact base needs the bedrock extractors, fs, frontmatter,
mdlink, and three domain extractors: html-comment link, path pair,
YAML row. No span parser.

## Rules and lints

Rule counts by Standard file, H2s: stories 9, tags 4, resume 8,
assessment-records 11, fit-matrices 6, interview-prep 6, prep-units
8, training-plans 4, unemployment-benefits 8. Lint rule ids:
stories 7, resume 5, role-postings 7, interview-prep 13,
unemployment-benefits 7. The rest say in prose that no detector
checks them: story prose voice and bullet length; tag-list order as
matrix dimension order; resume bullet length (`make measure` reports,
never gates), Fun Facts kept, the rendered PDF; the one-home rule of
interview-prep, delegated to a `doc-set-auditor` that does not exist
in this repo; certification-question drift and the 21-day filing
deadline in unemployment-benefits.

Two rules are byte-exact recomputes and are the sharpest examples of a
deterministic verifier over declared content: `role-postings.fit-summary`
regenerates the Fit summary block from the record's own table rows and
diffs it line for line (`role_postings_lint.py:528-572`), and
`role-postings.batch-profile` does the same for a whole generated file
(`:575-691`).

## Runbooks

| Skill | model / effort | Runs | Writes |
| --- | --- | --- | --- |
| build-story | inherit / medium | `stories-lint` | `stories/<id>.md`, never printed, the diff is the review copy |
| build-bullet | inherit / medium | `make measure`, `/resume-md-to-pdf` | the resume, only after approval |
| resume-md-to-pdf | inherit / medium | `make pdf` | the PDF; hard stop on any `{`, `}`, `TBD` |
| tailor-batch-resume | inherit / xhigh | `make measure`, `/resume-md-to-pdf` | a variant file and an index row; every trim reported for veto |
| fetch-role-posting | sonnet / low | `scripts/fetch_posting.py` | inbox `.txt`, `urls.txt`; the model never writes posting text |
| assess-role-posting | sonnet / xhigh | Sonnet extraction and Opus assessment subagents, `save_scatter_results.py`, `make render-role-posting`, `make refresh-role-posting`, `role-postings-lint` | stage JSON, the record, the company index row |
| unemployment-benefits-mode | opus / medium | `date +%F`, `unemployment-lint` | contacts, filings, task done flags |
| mock | inherit / high | `drill_harness.py --through <n>`, `interview-prep-lint` | one session row appended to `principles.md` frontmatter |
| plan-interview | inherit / high | `interview-prep-lint` | `plan.md` and the loop's index row; no user step mid-run |

No Python file carries a prompt string; every model dispatch is a
fenced block in a `SKILL.md` naming a `references/*.md` procedure. No
Python file calls a model API.

## Gates

`.pre-commit-config.yaml`: `playbook-lint` from dev-playbook at a
pinned rev, ruff check and format, shellcheck and shfmt (no `.sh`
files, so no-ops), then the five domain lints, all `always_run`, then
`make-check` at `stages: [pre-push]` only. `make check` is
format-check, lint, typecheck, test, then `pre-commit run
--all-files`. CI (`.github/workflows/ci.yml`) runs `pre-commit run
--all-files` with `SKIP=ref-lint,web-typecheck` and no `--hook-stage`,
so `make-check` never runs there: mypy and pytest run only at the
local pre-push hook. The `SKIP` names are dev-playbook detector names
read by `playbook-lint`'s dispatcher, not pre-commit hook ids.

## Derived state nothing surfaces

State a Standard says is read off the record and never written down,
and what computes it today:

- **Readiness** of a Prep-unit, untouched, in-progress, ready, from
  the last session's verdict: `interview_prep_schema.py:158-165`
  computes it and nothing calls it outside tests; the mock skill
  re-derives it in prose.
- **Benefit Week satisfied** by the Different-Employer Rule:
  `unemployment_lint.py:486-508` emits a finding on a shortfall and
  says nothing on success, so satisfaction is the absence of a
  finding; the skill restates the count in prose each activation.
- **Unfiled weeks and the 21-day cutoff**: prose in the skill only,
  needs today's date, no code enumerates the expected week sequence.
- **A variant stale against its batch profile**: the `tailored to`
  comment carries a path and no version, so nothing detects it.

These are derivations in the fact base's sense and the views a CLOA
viewer would draw first.

## Declared but unchecked

- Interview-Record to Role Posting is a prose link in an index, no
  frontmatter key, no detector.
- Projection `sources` is frontmatter no lint reads, since
  `stories/projections/` is outside every population.
- "Builds on agent-loop" is prose in `prep-units/agent-graph/index.md`
  and no `builds_on` key in the frontmatter that would carry it.
- The company index row equals the record's `description`, checked by
  dev-playbook's okf-lint, not by the repo's own lint.
- Two constants in `src/story_forge/paths.py`, `CONFIG_FILE` and
  `BATCHES_DIR`, are read by nothing.

## Judgment residuals

Each is a stochastic rule with a runbook as its verifier, and the
Standards say so:

- Requirement Classification, met, defensible, boilerplate miss,
  genuine miss, and the Vibe Read, made by an Opus subagent against
  `career/candidate-profile.md`; the lint checks the call is
  internally consistent, never that it is sound.
- Which tag a requirement row should carry; the lint checks
  membership in the registry only.
- `qualified` on a Work-Search Contact: asserted, never derived, no
  rationale stored, by design.
- Whether two employer strings are one employer: the lint proposes
  near-duplicates by edit distance and prefix; only the user decides.
- The one-home rule of interview-prep: which document a sentence
  belongs in.
- Bullet faithfulness to its source stories, story atomicity, prose
  voice.

## Handoffs through the user

Points where the user, not a script or a skill, carries the result:
settling `discuss` rows in an assessment; approving a new tag, since
only the user edits `stories/tags.yaml`; running
`make role-posting-status` to record applied, declined, or rejected;
forming a batch and running `make aggregate-role-postings`; vetoing
each trim in tailoring; typing `check`, `autocomplete`, `real talk`,
`pause`, `debrief` in a mock; reading the recruiter's named rounds
into a loop; and filing at VEC, the one step only the user can
execute. The role-postings pipeline self-chains once, fetch suggesting
assess.

## Questions a person asks

Candidates the agents raised, marked A where extractable and declared
facts answer it and J where a judgment or a live input is needed:

- Which stories are `resume_eligible` and cited by no resume? A.
- Which tags have no story? A.
- Which prep-units does one employer's interview loop demand that are still untouched? A.
- Is this prep-unit ready for a coding round? A, and no tool prints it.
- Which playbook habits does no interviewer sheet grade? A, and no rule computes it.
- Which requirement rows have neither a prep-unit nor an admitted gap? A, the `plan-gaps` rule.
- Which postings sit unassessed? A, the inbox listing.
- What is the worst weak spot across the batch? A, the profile's table.
- Is this week's claim satisfied? A.
- Which weeks are unfiled? J, needs today.
- Is a variant stale against its regenerated profile? J, no version on the edge.
- Are these two employer strings one employer? J.
- What does `make check` run, and does CI run the same? A, and the answer is no.
- Which skill can write to `stories/`? A, build-story only.
- What breaks if `tags.yaml` is renamed? A, one seam, `paths.TAGS_FILE`, six modules.
