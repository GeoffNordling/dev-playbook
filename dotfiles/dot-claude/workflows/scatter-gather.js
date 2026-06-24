export const meta = {
  name: 'scatter-gather',
  description: 'Stateless parallel fan-out: run N independent jobs as isolated agent() calls in a single parallel() and return one structured result per job in input order. No cache, no file reads, nothing carried between jobs — all durable state lives in the caller.',
  whenToUse: 'A batch of independent jobs that do not depend on each other and whose results you want collected in one shot. model and effort are required and pinned to every job (no session inherit), so the batch runs under one fixed identity. For sequential dependent work, use the Ralph loop instead.',
  phases: [{ title: 'Scatter' }],
}

// args:
//   model   REQUIRED worker model ('haiku' | 'sonnet' | 'opus' | ...); pinned to every job
//   effort  REQUIRED reasoning effort ('low' | 'medium' | 'high' | 'xhigh' | 'max'); pinned to every job
//   schema  optional JSON Schema applied to every job's structured output (batch-level)
//   jobs    [{ id, prompt }] — independent jobs; results return in this order, keyed by id
//
// args may reach the script either as a parsed object or as a JSON string, depending on
// the launch path. Normalize once so the batch is reliably delivered however it is handed
// over (string or object). A malformed string throws loud here rather than silently losing
// the batch — which is exactly what bit the Ralph loop, whose script read args.goal without
// parsing.
const A = typeof args === 'string' ? JSON.parse(args) : (args ?? {})

// model/effort are required because the batch runs under one fixed judge identity:
// the first consumer (#98) content-addresses its cache on model + effort + prompt + schema,
// so an inherited session value would silently corrupt the fingerprint. Throw loud instead.
const MODEL  = A.model
const EFFORT = A.effort
const SCHEMA = A.schema
const JOBS   = A.jobs ?? []

if (!MODEL)  throw new Error('scatter-gather: args.model is required and must be pinned to the run — the runtime never inherits the session model.')
if (!EFFORT) throw new Error('scatter-gather: args.effort is required and must be pinned to the run — the runtime never inherits the session effort.')

if (!Array.isArray(JOBS)) throw new Error('scatter-gather: args.jobs must be an array of { id, prompt }.')

// Pre-flight batch guard at the runtime's binding single-run limit. Scatter-gather spawns
// one agent per job in a single parallel() call, so the binding ceiling is the
// agent-lifetime cap (1000), not the larger 4096 per-call item cap. Fail before fanning
// out rather than dying with an opaque error mid-run.
const MAX_JOBS = 1000
if (JOBS.length > MAX_JOBS) {
  throw new Error(`scatter-gather: batch of ${JOBS.length} jobs exceeds the runtime's single-run limit of ${MAX_JOBS} (one agent per job, the agent-lifetime cap) — split the batch and run it in parts.`)
}

for (const [i, job] of JOBS.entries()) {
  if (!job || typeof job.id !== 'string' || job.id === '' || typeof job.prompt !== 'string' || job.prompt === '') {
    throw new Error(`scatter-gather: jobs[${i}] must be { id: non-empty string, prompt: non-empty string } — the id keys the result, so it cannot be missing.`)
  }
}

phase('Scatter')

// Single fan-out: one isolated agent() per job. Catch inside the per-job thunk so a
// thrown or skipped job yields { id, result: null } and keeps its id, rather than
// dropping to a bare null (which parallel() would do on a throw) and losing the key.
const results = await parallel(JOBS.map((job) => async () => {
  try {
    const result = await agent(job.prompt, {
      label: `job:${job.id}`,
      phase: 'Scatter',
      model: MODEL,
      effort: EFFORT,
      ...(SCHEMA ? { schema: SCHEMA } : {}),
    })
    return { id: job.id, result: result ?? null }
  } catch {
    return { id: job.id, result: null }
  }
}))

return results
