export const meta = {
  name: 'judgments',
  description: 'Judge a docket of uncached judgments in one parallel fan-out: one agent per judgment, pinned to the bench its declaration names, verdicts partitioned deterministically.',
  whenToUse: 'The judgment cache gate is red. Pass the stdout of `judgments-run plan` as args, verbatim — that command is the planner, and this workflow judges what it hands over. Returns the `record` command to run and the refutations to weigh.',
  phases: [{ title: 'Judge', detail: 'one pinned judge agent per uncached judgment' }],
}

// ---------------------------------------------------------------------------
// A NOTE ON THE LANGUAGE, for a Python reader
//
// This is JavaScript. The differences that matter for reading this file:
//
//   const x = ...        a name bound once (Python has no direct equivalent;
//                        think of it as a local you promise not to rebind).
//   `text ${expr}`       a template literal -- exactly Python's f-string
//                        f"text {expr}", but with backticks and a $ sigil.
//   xs.map(f)            [f(x) for x in xs]
//   xs.filter(f)         [x for x in xs if f(x)]
//   xs.some(f)           any(f(x) for x in xs)
//   xs.join(' ')         ' '.join(xs)
//   (a) => a + 1         lambda a: a + 1  -- an "arrow function". When the body
//                        is wrapped in { } it needs an explicit `return`.
//   a?.b                 b if a is not None else None -- optional chaining.
//   s.replaceAll(a, b)   s.replace(a, b) in Python. JavaScript's own .replace()
//                        substitutes only the FIRST occurrence, so this file
//                        always uses .replaceAll(), which behaves like Python's.
//   JSON.parse(s)        json.loads(s)
//   await f()            same meaning as Python's await; this whole script body
//                        runs inside an async function, so top-level await is
//                        legal here even though it is not in a Python module.
//   throw new Error(m)   raise RuntimeError(m)
//   try { } catch { }    try: / except:
//
// The three workflow built-ins used below -- agent(), parallel(), phase() --
// are supplied by the Workflow runtime, not by JavaScript itself.
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// WHY THIS SCRIPT DOES NO PLANNING
//
// There are three layers in a judgment run, and each can do exactly one kind of
// work:
//
//   1. the Claude Code session   an LLM, but it holds the Bash tool
//   2. this script               deterministic, but has NO filesystem, NO
//                                subprocess, NO network -- only agent(),
//                                parallel(), pipeline(), phase(), log(), args
//   3. the judge agents          LLMs, one fresh context each
//
// Planning -- keying every judgment and asking the seen-set which keys it
// already holds -- is deterministic work that must read files. Layer 2 cannot
// read files and layers 1 and 3 are language models, so the only place that
// combination exists is the Bash tool at layer 1. An earlier version of this
// file spawned a cheap agent to run `judgments-run plan` and transcribe its
// output; that agent had discretion it should never have had, and it used it,
// wandering out of the worktree it was launched in and judging the wrong repo.
//
// So the plan arrives as args instead. The session runs one command and copies
// its stdout into the Workflow call without reading it. Nothing here interprets
// a repository, and every agent this script spawns is a judge.
// ---------------------------------------------------------------------------

// Exactly the key set `judgments-run plan` emits. Requiring all of them and
// forbidding anything else means a payload from a newer or older CLI fails here,
// loudly, before a single agent spawns -- rather than half-working with a field
// silently missing. tests/test_judgments_workflow.py asserts this list still
// equals what plan() actually produces, so the two cannot drift.
const PLAN_KEYS = ['cli', 'root', 'schema', 'judge_prompt', 'cached', 'jobs', 'skipped']

// The substitution point inside `judge_prompt`. The prompt's wording lives with
// the CLI whose contract it describes; the only thing done to it here is putting
// each job's id where this marker is.
const ID_PLACEHOLDER = '{id}'

// One agent is spawned per judgment in a single fan-out, so the binding ceiling
// is the runtime's agent-lifetime cap rather than the larger per-call item cap.
// A repo with more uncached judgments than this has outgrown one run.
const MAX_JUDGMENTS = 1000

// ---------------------------------------------------------------------------
// Arguments: the plan
// ---------------------------------------------------------------------------

// `args` is a runtime-supplied global holding whatever the caller passed. Here it
// is required and it is the plan.
//
// The runtime delivers it in exactly two shapes, both probed against the live
// runtime rather than taken from documentation: omitting args yields `undefined`,
// and anything passed arrives JSON-**serialized to a string** -- never as a live
// object, despite what the Workflow tool's own docs claim. Since `judgments-run
// plan` prints JSON text and the caller passes that text straight through, the
// serialization is a no-op in practice: what lands here is what the CLI printed.
//
// Every check below runs before any agent spawns, and every failure is fatal. A
// mangled plan is not something to work around -- it means the string that
// reached the runtime is not the one the CLI produced.
function parsePlan(raw) {
  if (raw == null)
    throw new Error(
      'judgments: args is required — pass the stdout of `judgments-run plan` verbatim',
    )
  if (typeof raw !== 'string')
    throw new Error(`judgments: args must be a JSON string, got ${typeof raw}`)

  let plan
  try {
    plan = JSON.parse(raw)
  } catch (e) {
    throw new Error(`judgments: args is not valid JSON (${e.message}) — pass \`judgments-run plan\` stdout unedited`)
  }
  // A caller who passes the planner's stdout as a *string* rather than as the
  // object it denotes gets it serialized twice, and JSON.parse peels off only one
  // layer. That is a real mistake and still throws -- but the message names it, so
  // the fix is one obvious edit rather than a round of guessing.
  if (typeof plan === 'string')
    throw new Error(
      'judgments: args arrived double-encoded — pass the plan as a JSON object in the tool call, not as a quoted string wrapping one',
    )
  if (plan === null || typeof plan !== 'object' || Array.isArray(plan))
    throw new Error('judgments: args must decode to a JSON object')

  for (const key of PLAN_KEYS)
    if (!(key in plan))
      throw new Error(`judgments: plan is missing "${key}" — expected the keys ${PLAN_KEYS.join(', ')}`)
  for (const key of Object.keys(plan))
    if (!PLAN_KEYS.includes(key))
      throw new Error(`judgments: plan has an unexpected key "${key}" — this workflow and judgments-run have drifted apart`)

  // Every command in the run is built from `cli`, and every real one carries an
  // explicit --root. Its absence means we are holding something other than what
  // the CLI printed, and running it would judge an unknown repository.
  if (typeof plan.cli !== 'string' || !plan.cli.includes('--root '))
    throw new Error(`judgments: plan.cli is not a usable invocation: ${plan.cli}`)
  if (typeof plan.judge_prompt !== 'string' || !plan.judge_prompt.includes(ID_PLACEHOLDER))
    throw new Error(`judgments: plan.judge_prompt has no ${ID_PLACEHOLDER} placeholder to substitute an id into`)
  if (plan.schema === null || typeof plan.schema !== 'object')
    throw new Error('judgments: plan.schema must be the judge output schema object')
  if (!Array.isArray(plan.jobs) || !Array.isArray(plan.skipped))
    throw new Error('judgments: plan.jobs and plan.skipped must both be arrays')

  plan.jobs.forEach((job, index) => {
    for (const field of ['id', 'model', 'effort'])
      if (typeof job?.[field] !== 'string' || job[field] === '')
        throw new Error(`judgments: job ${index} is missing a non-empty "${field}"`)
  })
  if (plan.jobs.length > MAX_JUDGMENTS)
    throw new Error(`judgments: ${plan.jobs.length} judgments exceeds the single-run limit of ${MAX_JUDGMENTS}`)

  return plan
}

const PLAN = parsePlan(args)

// Naming the repository in the progress log makes a run against the wrong
// checkout something you can see rather than infer from a surprising docket --
// worth one line in a workspace where worktrees and their main checkout sit side
// by side and hold the same judgment ids.
log(`judgments: root ${PLAN.root}`)
log(`judgments: ${PLAN.cached} cached, ${PLAN.jobs.length} to judge${PLAN.skipped.length ? `, ${PLAN.skipped.length} set aside` : ''}`)

// ---------------------------------------------------------------------------
// Judge
// ---------------------------------------------------------------------------

// One isolated agent per judgment, all at once, each pinned to the model and
// effort its own declaration names and constrained to the plan's output schema.
// The prompt is a bootstrap: it tells the agent to run `... render <id>`, whose
// stdout is the real prompt plus the full text of every evidence file. That is
// deliberate -- the heavy bytes materialize inside the judge's own context and
// never pass through this script or the calling agent's window.
//
// The try/catch is inside each job so a crashed judge yields a null result that
// KEEPS its id. Without it, parallel() would return a bare null and we would lose
// track of which judgment it belonged to.
phase('Judge')

const verdicts = await parallel(
  PLAN.jobs.map((job) => async () => {
    try {
      const result = await agent(PLAN.judge_prompt.replaceAll(ID_PLACEHOLDER, job.id), {
        label: `judge:${job.id}`,
        phase: 'Judge',
        model: job.model,
        effort: job.effort,
        schema: PLAN.schema,
      })
      return { id: job.id, result: result ?? null }
    } catch {
      return { id: job.id, result: null }
    }
  }),
)

// Partition the verdicts. This is plain code, not an agent: which judgments
// passed is a mechanical fact about the returned data, and letting a model decide
// it would put discretion where none belongs. Only `verdict === true` is ever
// treated as a pass -- a crash (result null) is NOT a false verdict, it means the
// judgment was never ruled on at all.
const passed = verdicts.filter((v) => v.result?.verdict === true).map((v) => v.id)
const refuted = verdicts
  .filter((v) => v.result?.verdict === false)
  .map((v) => ({ id: v.id, opinion: v.result.opinion }))
const crashed = verdicts.filter((v) => v.result === null).map((v) => v.id)

log(`judgments: ${passed.length} passed, ${refuted.length} refuted, ${crashed.length} crashed`)

// ---------------------------------------------------------------------------
// The result
// ---------------------------------------------------------------------------

// `record` comes first because it is the one thing the caller must act on before
// anything else: recording is a shell command, so it belongs at the layer that
// has a shell. The ids in it were computed above by this script, never chosen by
// an agent, and only passes ever appear -- so the caller runs the string as given
// rather than assembling one. It is null when nothing passed.
//
// `green` says nothing in this run needs a human mind: every judgment that ran
// passed, none crashed, and none was set aside. The gate itself goes green only
// after `record` runs.
return {
  record: passed.length ? `${PLAN.cli} record ${passed.join(' ')}` : null,
  cached: PLAN.cached,
  ran: PLAN.jobs.length,
  passed,
  refuted,
  crashed,
  skipped: PLAN.skipped,
  green: refuted.length === 0 && crashed.length === 0 && PLAN.skipped.length === 0,
}
