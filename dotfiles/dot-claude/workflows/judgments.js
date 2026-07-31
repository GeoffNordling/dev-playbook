export const meta = {
  name: 'judgments',
  description: 'Run the repo’s uncached judgments end to end: plan the docket, fan out one judge per miss, record the passes, and return only what was refuted.',
  whenToUse: 'The judgment cache gate is red. Takes no arguments in the normal case; pass {skip: [id, ...]} to leave judgments you have already set aside unjudged. Returns a compact summary whose only actionable part is `refuted`.',
  phases: [
    { title: 'Plan', detail: 'read the docket of uncached judgments from the CLI' },
    { title: 'Judge', detail: 'one pinned judge agent per uncached judgment' },
    { title: 'Record', detail: 'write the passing verdicts to the seen-set' },
  ],
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
//   (a) => a + 1         lambda a: a + 1  -- an "arrow function". When the body
//                        is wrapped in { } it needs an explicit `return`.
//   {...obj, k: v}       {**obj, "k": v}  -- the spread operator.
//   a ?? b               "a unless a is null/undefined, else b". Like
//                        `a if a is not None else b`, NOT Python's `or`:
//                        it does not treat 0 or "" as missing.
//   a?.b                 b if a is not None else None -- optional chaining.
//   JSON.parse(s)        json.loads(s)
//   await f()            same meaning as Python's await; this whole script body
//                        runs inside an async function, so top-level await is
//                        legal here even though it is not in a Python module.
//   throw new Error(m)   raise RuntimeError(m)
//   try { } catch { }    try: / except:
//
// The three workflow built-ins used below -- agent(), parallel(), phase() --
// are supplied by the Workflow runtime, not by JavaScript itself. There is no
// filesystem and no subprocess access in this script: anything that must touch
// disk or run a shell command has to be done by an agent() we spawn.
// ---------------------------------------------------------------------------

// The structured-output contract every judge must fill. This is a VERBATIM
// mirror of judgments.core.SCHEMA in Python, and it must stay verbatim: that
// exact object is hashed into every judgment's content key, so a judge that
// answered under a different schema than the one recorded would put a quiet
// lie in the cache. The mirror is deliberate rather than transcribed at
// runtime by the planner agent -- an LLM must never be in the path of a
// key-critical value. tests/test_judgments_workflow.py parses this literal out
// of this file and asserts it equals core.SCHEMA, so drift fails `make check`
// deterministically instead of corrupting verdicts.
//
// It is written with quoted keys and no trailing comma, which is unidiomatic
// JavaScript but makes the literal simultaneously valid JSON — so that test can
// json.loads() it directly instead of hand-rolling a JS parser it could get
// wrong. Keep it that way.
const VERDICT_SCHEMA = {
  "type": "object",
  "properties": {
    "verdict": { "type": "boolean" },
    "opinion": { "type": "string" }
  },
  "required": ["verdict", "opinion"],
  "additionalProperties": false
}

// The shape the planner agent must return: a faithful transcription of
// `judgments-run plan` stdout, minus the parts nothing here reads. Declaring it
// as a schema means the runtime validates the agent's answer and makes it retry
// on a mismatch, so a garbled transcription cannot flow downstream silently.
// `error` is the planner's failure channel and is the only optional field: listing
// a property without naming it in `required` makes it optional, while
// additionalProperties:false still bars anything not listed here.
const PLAN_SCHEMA = {
  type: 'object',
  properties: {
    cli: { type: 'string' },
    seen_count: { type: 'integer' },
    unseen: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          model: { type: 'string' },
          effort: { type: 'string' },
          prompt: { type: 'string' },
        },
        required: ['id', 'model', 'effort', 'prompt'],
        additionalProperties: false,
      },
    },
    error: { type: 'string' },
  },
  required: ['cli', 'seen_count', 'unseen'],
  additionalProperties: false,
}

// Confirmation shape for the recorder agent. It reports whether the command
// actually succeeded rather than just claiming to have run, so a failed record
// surfaces as a loud error instead of a silent no-op that leaves the gate red
// with no explanation.
const RECORD_SCHEMA = {
  type: 'object',
  properties: {
    recorded: { type: 'boolean' },
    detail: { type: 'string' },
  },
  required: ['recorded', 'detail'],
  additionalProperties: false,
}

// The planner and recorder do mechanical transcription, not reasoning, so they
// run on the cheapest bench available. The judges themselves are pinned
// per-judgment from the declaration, never from here.
const CLERK = { model: 'claude-haiku-4-5-20251001', effort: 'low' }

// One agent is spawned per uncached judgment in a single fan-out, so the binding
// ceiling is the runtime's agent-lifetime cap rather than the larger per-call
// item cap. A repo with more judgments than this has outgrown one run.
const MAX_JUDGMENTS = 1000

// ---------------------------------------------------------------------------
// Arguments
// ---------------------------------------------------------------------------

// `args` is a runtime-supplied global holding whatever the caller passed. The
// normal call is Workflow({name: "judgments"}) with no args at all.
//
// The runtime delivers it in exactly two shapes, both probed against the live
// runtime rather than taken from documentation: omitting args yields `undefined`,
// and anything passed arrives JSON-**serialized to a string** — never as a live
// object, despite what the Workflow tool's own docs claim. So the caller writes an
// object and this parses the text of it. Any third shape is a real surprise about
// the runtime and throws, before a single agent spawns.
function parseArgs(raw) {
  if (raw == null) return {}
  if (typeof raw !== 'string')
    throw new Error(`judgments: args must arrive as a JSON string, got ${typeof raw}`)
  let opts
  try {
    opts = JSON.parse(raw)
  } catch (e) {
    throw new Error(`judgments: args is not valid JSON (${e.message})`)
  }
  if (opts === null || typeof opts !== 'object' || Array.isArray(opts))
    throw new Error('judgments: args must be an object, e.g. {skip: ["some-id"]}')
  for (const key of Object.keys(opts)) {
    if (key !== 'skip')
      throw new Error(`judgments: unknown arg "${key}" — the only accepted arg is "skip"`)
  }
  const skip = opts.skip ?? []
  if (!Array.isArray(skip) || skip.some((id) => typeof id !== 'string' || id === ''))
    throw new Error('judgments: arg "skip" must be an array of non-empty judgment id strings')
  return { skip }
}

const { skip: SKIP = [] } = parseArgs(args)

// A Set gives O(1) membership tests, like a Python set. `skipSet.has(x)` is `x in skipSet`.
const skipSet = new Set(SKIP)

// ---------------------------------------------------------------------------
// Phase 1 — Plan
// ---------------------------------------------------------------------------

phase('Plan')

// This script cannot run a shell command itself, so a cheap agent reads the
// docket for us. This is the one command in the whole flow that has to be found
// the ordinary way: it is the bootstrap, so it cannot yet know the absolute
// invocation that `plan` is about to hand back for every later call.
const plan = await agent(
  [
    'Work in your current working directory. Do NOT `cd` anywhere first, and do not',
    'go looking for a better place to run this. You may be standing in a git worktree',
    'under a .claude/worktrees/ path — if so, THAT is the repository you must read,',
    'not the main checkout above it. Moving would read the wrong repo and silently',
    'judge the wrong files.',
    '',
    'Run exactly this command, unmodified:',
    '',
    '    uv run judgments-run plan',
    '',
    'It prints a single JSON object on stdout. Return its `cli`, `seen_count`, and',
    '`unseen` fields exactly as printed — copy them, do not summarize, reword, or',
    'renumber anything, and do not add entries of your own. `unseen` may be empty;',
    'that is a valid answer meaning every judgment is already cached.',
    '',
    'If the command fails, do not work around it with a different command, a different',
    'directory, or a different spelling, and do not invent a result. Report the failure:',
    'set `error` to the exact error output, `cli` to the empty string, `seen_count` to 0,',
    'and `unseen` to an empty list.',
  ].join('\n'),
  { label: 'plan', phase: 'Plan', schema: PLAN_SCHEMA, ...CLERK },
)

// agent() returns null if it crashed or the user skipped it. Fail loud: without a
// docket there is nothing meaningful this run can do.
if (plan === null)
  throw new Error('judgments: the planning agent failed — could not read the docket')

// The planner's own failure channel, and a shape check on what it transcribed. Every
// real invocation carries an explicit --root, so its absence means we are holding an
// error message or a hallucinated command rather than something safe to run.
if (plan.error)
  throw new Error(`judgments: \`judgments-run plan\` failed — ${plan.error}`)
if (!plan.cli.includes('--root'))
  throw new Error(`judgments: the planner returned an unusable command: ${plan.cli}`)

if (plan.unseen.length > MAX_JUDGMENTS)
  throw new Error(
    `judgments: ${plan.unseen.length} uncached judgments exceeds the single-run limit of ${MAX_JUDGMENTS}`,
  )

// Honour the caller's set-aside list. Fix attempts are tracked by the calling
// agent, in its own context, by design — this workflow is stateless and simply
// judges whatever it is not told to leave alone.
const docket = plan.unseen.filter((job) => !skipSet.has(job.id))
const skipped = plan.unseen.filter((job) => skipSet.has(job.id)).map((job) => job.id)

// Surface which repo was actually planned. The planner is the one step whose command
// depends on where its agent is standing, so naming the root it resolved turns a
// wrong-directory run into something visible in the progress log rather than a silent
// judging of the wrong files. `cli` carries it as `--root <path>`.
const plannedRoot = plan.cli.slice(plan.cli.indexOf('--root ') + '--root '.length).trim()
log(`judgments: root ${plannedRoot}`)
log(`judgments: ${plan.seen_count} cached, ${docket.length} to judge${skipped.length ? `, ${skipped.length} set aside` : ''}`)

// Nothing to do. Return the same summary shape as a full run so the caller has
// exactly one result contract to read, never a special case.
if (docket.length === 0) {
  return {
    cached: plan.seen_count,
    ran: 0,
    passed: [],
    refuted: [],
    crashed: [],
    skipped,
    green: skipped.length === 0,
  }
}

// ---------------------------------------------------------------------------
// Phase 2 — Judge
// ---------------------------------------------------------------------------

phase('Judge')

// One isolated agent per judgment, all at once, each pinned to the model and
// effort its own declaration names. The judge's prompt is a two-line bootstrap:
// it tells the agent to run `... render <id>`, whose stdout is the real prompt
// plus the full text of every evidence file. That is deliberate — the heavy
// bytes materialize inside the judge's own context and never pass through this
// script or the calling agent's window.
//
// The try/catch is inside each job so a crashed judge yields a null result that
// KEEPS its id. Without it, parallel() would return a bare null and we would
// lose track of which judgment it belonged to.
const verdicts = await parallel(
  docket.map((job) => async () => {
    try {
      const result = await agent(job.prompt, {
        label: `judge:${job.id}`,
        phase: 'Judge',
        model: job.model,
        effort: job.effort,
        schema: VERDICT_SCHEMA,
      })
      return { id: job.id, result: result ?? null }
    } catch {
      return { id: job.id, result: null }
    }
  }),
)

// Partition the verdicts. This is plain code, not an agent: which judgments
// passed is a mechanical fact about the returned data, and letting a model
// decide it would put discretion where none belongs. Only `verdict === true`
// is ever treated as a pass — a crash (result null) is NOT a false verdict,
// it means the judgment was never ruled on at all.
const passed = verdicts.filter((v) => v.result?.verdict === true).map((v) => v.id)
const refuted = verdicts
  .filter((v) => v.result?.verdict === false)
  .map((v) => ({ id: v.id, opinion: v.result.opinion }))
const crashed = verdicts.filter((v) => v.result === null).map((v) => v.id)

log(`judgments: ${passed.length} passed, ${refuted.length} refuted, ${crashed.length} crashed`)

// ---------------------------------------------------------------------------
// Phase 3 — Record
// ---------------------------------------------------------------------------

// Only passes are ever recorded, and the id list was computed above by this
// script rather than chosen by any agent. The recorder is a courier: it runs one
// fully-specified command that the CLI itself handed us in `plan.cli`.
let recorded = []
if (passed.length > 0) {
  phase('Record')
  const command = `${plan.cli} record ${passed.join(' ')}`
  const confirmation = await agent(
    [
      'Run this exact shell command, verbatim:',
      '',
      `    ${command}`,
      '',
      'It is absolute and needs no PATH lookup, no virtualenv activation, and no',
      'particular working directory. Do not modify it, do not shorten it, and do not',
      'run any other command. Set `recorded` true only if it exited 0; otherwise set',
      'it false and put the exact error output in `detail`.',
    ].join('\n'),
    { label: 'record', phase: 'Record', schema: RECORD_SCHEMA, ...CLERK },
  )
  if (confirmation === null || confirmation.recorded !== true)
    throw new Error(
      `judgments: judges passed ${passed.length} judgment(s) but recording them failed — ` +
        `${confirmation?.detail ?? 'the recording agent crashed'}. ` +
        'The verdicts are lost; re-run to re-judge them.',
    )
  recorded = passed
}

// The caller's whole result. `refuted` is the only actionable part — everything
// else is bookkeeping for its report. `green` says whether the cache gate should
// now be satisfied: it needs every judgment passing, so any refusal, crash, or
// set-aside judgment keeps it false.
return {
  cached: plan.seen_count,
  ran: docket.length,
  passed: recorded,
  refuted,
  crashed,
  skipped,
  green: refuted.length === 0 && crashed.length === 0 && skipped.length === 0,
}
