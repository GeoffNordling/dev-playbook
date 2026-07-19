export const meta = {
  name: 'scatter-gather',
  description: 'Stateless parallel fan-out: run N independent jobs as isolated agent() calls in a single parallel() and return one structured result per job in input order. No cache, no file reads, nothing carried between jobs — all durable state lives in the caller.',
  whenToUse: 'A batch of independent jobs that do not depend on each other and whose results you want collected in one shot. model and effort are required on every job (no session inherit, no batch-level default), so each job runs under its own pinned identity. For sequential dependent work, use the Ralph loop instead.',
  phases: [{ title: 'Scatter' }],
}

// args: a required JSON string of options. No defaults.
//   jobs    array of { id, prompt, model, effort }; results return in this order, keyed by id.
//           model ('haiku' | 'sonnet' | 'opus' | ...) and effort ('low' | 'medium' | 'high' |
//           'xhigh' | 'max') are per-job and required on every job — no batch-level identity.
//   schema  optional JSON Schema applied to every job's structured output
//
// NOTE (2026-06-25): the Workflow runtime's own docs are wrong here — they say objects/arrays
// reach the script verbatim, but every args value actually arrives JSON-serialized to a string
// (or undefined when omitted), so the contract is: the caller passes an object, this script parses it.
const ALLOWED = ['jobs', 'schema']

// Pre-flight batch limit. Scatter-gather spawns one agent per job in a single parallel() call,
// so the binding ceiling is the agent-lifetime cap (1000), not the larger 4096 per-call item cap.
const MAX_JOBS = 1000

function parseArgs(raw) {
  if (raw == null)
    throw new Error(`scatter-gather: args is required — pass {jobs} (schema optional)`)
  if (typeof raw !== 'string')
    throw new Error(`scatter-gather: args must be a JSON string, got ${typeof raw}`)
  let opts
  try { opts = JSON.parse(raw) }
  catch (e) { throw new Error(`scatter-gather: args is not valid JSON (${e.message})`) }
  if (opts === null || typeof opts !== 'object' || Array.isArray(opts))
    throw new Error(`scatter-gather: args must decode to a JSON object`)
  for (const k of Object.keys(opts)) {
    if (!ALLOWED.includes(k))
      throw new Error(`scatter-gather: unknown arg "${k}" — allowed: ${ALLOWED.join(', ')}`)
  }
  if (!Array.isArray(opts.jobs))
    throw new Error(`scatter-gather: arg "jobs" is required and must be an array of {id, prompt, model, effort}`)
  if (opts.jobs.length > MAX_JOBS)
    throw new Error(`scatter-gather: batch of ${opts.jobs.length} jobs exceeds the runtime's single-run limit of ${MAX_JOBS} (one agent per job, the agent-lifetime cap) — split the batch and run it in parts.`)
  opts.jobs.forEach((job, i) => {
    if (!job || typeof job.id !== 'string' || job.id === '' || typeof job.prompt !== 'string' || job.prompt === '')
      throw new Error(`scatter-gather: jobs[${i}] must have { id: non-empty string, prompt: non-empty string } — the id keys the result`)
    if (typeof job.model !== 'string' || job.model === '')
      throw new Error(`scatter-gather: jobs[${i}] (id ${JSON.stringify(job.id)}) is missing a non-empty "model" — model is required on every job`)
    if (typeof job.effort !== 'string' || job.effort === '')
      throw new Error(`scatter-gather: jobs[${i}] (id ${JSON.stringify(job.id)}) is missing a non-empty "effort" — effort is required on every job`)
  })
  if ('schema' in opts && (opts.schema === null || typeof opts.schema !== 'object' || Array.isArray(opts.schema)))
    throw new Error(`scatter-gather: arg "schema" must be a JSON Schema object when provided`)
  return opts
}

const { jobs: JOBS, schema: SCHEMA } = parseArgs(args)

phase('Scatter')

// Fan-out guard — count-stating: this log surfaces how many agents are about to spawn *before* the
// parallel() fan-out below, so a scope mismatch ("expected 3, this launches 8") shows up before the spend.
log(`scatter-gather: ${JOBS.length} job(s), per-job model/effort, schema=${SCHEMA ? 'yes' : 'no'}`)

// Fan-out guard — leaf clause: prepend the leaf discipline to every job's prompt so no worker launches
// without it. Each job is one leaf in a supervised fan-out, not an orchestrator: it does its task and
// returns, spawning nothing further.
const LEAF_CLAUSE =
  'You are one leaf in a supervised parallel fan-out, not an orchestrator: do not use the Agent tool ' +
  'to spawn sub-agents and do not invoke skills — do only the task below and return its result as ' +
  'your final message.\n\n'

// Single fan-out: one isolated agent() per job, each pinned to its own model/effort. Every agent() here
// is a fresh, zero-context session by construction — never a fork — so a job cannot inherit and re-run a
// caller's wider directive; and a bounded job gone silent past ~5–10 min is a stop-and-investigate signal
// for the caller, never something to passively wait out. Catch inside the per-job thunk so a thrown or
// skipped job yields { id, result: null } and keeps its id, rather than dropping to a bare null (which
// parallel() returns on a throw) and losing the key.
const results = await parallel(JOBS.map((job) => async () => {
  try {
    const result = await agent(LEAF_CLAUSE + job.prompt, {
      label: `job:${job.id}`,
      phase: 'Scatter',
      model: job.model,
      effort: job.effort,
      ...(SCHEMA ? { schema: SCHEMA } : {}),
    })
    return { id: job.id, result: result ?? null }
  } catch {
    return { id: job.id, result: null }
  }
}))

return results
