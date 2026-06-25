export const meta = {
  name: 'ralph-loop',
  description: 'Pure Ralph loop: boot a fresh agent each iteration to work a plan to done. Disk (the plan file, the progress file, git) is the only memory; loop control lives in this runtime, not in any context window.',
  whenToUse: 'A plan you want ground out autonomously without holding it in one context window. Launch from the target repo or worktree — agents inherit that cwd. Seed the plan and progress files first.',
  phases: [{ title: 'Iterate' }],
}

// args: a required JSON string of options. All fields required; no defaults.
//   model         worker model ('haiku' | 'sonnet' | 'opus' | ...)
//   maxIters      safety rail; throws if exceeded without completing
//   planFile      the plan: a task list the agent works through and checks off
//   progressFile  the running log appended each iteration
//
// NOTE (2026-06-25): the Workflow runtime's own docs are wrong here — they say objects/arrays
// reach the script verbatim, but every args value actually arrives JSON-serialized to a string
// (or undefined when omitted), so the contract is: the caller passes an object, this script parses it.
const ARG_TYPES = { model: 'string', maxIters: 'number', planFile: 'string', progressFile: 'string' }

function parseArgs(raw) {
  if (raw == null)
    throw new Error(`ralph-loop: args is required — pass {${Object.keys(ARG_TYPES).join(', ')}}`)
  if (typeof raw !== 'string')
    throw new Error(`ralph-loop: args must be a JSON string, got ${typeof raw}`)
  let opts
  try { opts = JSON.parse(raw) }
  catch (e) { throw new Error(`ralph-loop: args is not valid JSON (${e.message})`) }
  if (opts === null || typeof opts !== 'object' || Array.isArray(opts))
    throw new Error(`ralph-loop: args must decode to a JSON object`)
  for (const k of Object.keys(ARG_TYPES))
    if (!(k in opts))
      throw new Error(`ralph-loop: missing required arg "${k}" — required: ${Object.keys(ARG_TYPES).join(', ')}`)
  for (const [k, v] of Object.entries(opts)) {
    if (!(k in ARG_TYPES))
      throw new Error(`ralph-loop: unknown arg "${k}" — required: ${Object.keys(ARG_TYPES).join(', ')}`)
    if (typeof v !== ARG_TYPES[k])
      throw new Error(`ralph-loop: arg "${k}" must be ${ARG_TYPES[k]}, got ${typeof v}`)
  }
  if (!Number.isInteger(opts.maxIters) || opts.maxIters < 1)
    throw new Error(`ralph-loop: maxIters must be a positive integer, got ${opts.maxIters}`)
  return opts
}

const { model: MODEL, maxIters: MAX, planFile: PLAN, progressFile: PROGRESS } = parseArgs(args)

phase('Iterate')

log(`ralph-loop config: model=${MODEL}, maxIters=${MAX}, planFile=${PLAN}, progressFile=${PROGRESS}`)

const STATUS = {
  type: 'object', additionalProperties: false,
  required: ['done', 'blocker', 'summary'],
  properties: {
    done:    { type: 'boolean', description: 'true ONLY when every task in the plan is complete' },
    blocker: { type: ['string', 'null'], description: 'one-line reason the loop must stop — checks red on entry, or a required file missing/unreadable; null if none' },
    summary: { type: 'string',  description: 'one line: what this iteration did' },
  },
}

const PROMPT = `Work in the current directory — do not cd; use relative paths.

The plan is in ${PLAN}; the running log of work so far is in ${PROGRESS}. Both must already exist.

1. Run \`make check\`. If it does not pass, or if ${PLAN} or ${PROGRESS} is missing or unreadable, set blocker to a one-line reason and STOP — do nothing else. Red on entry is not yours to fix; it means a prior iteration left the repo broken.
2. Read ${PLAN} (the plan) and ${PROGRESS} (the log of what past iterations did).
3. Find the next incomplete task in the plan and implement it — one task only, small enough to finish cleanly in this iteration.
4. Run \`make check\` again. If your work broke it, fix until it passes. Never commit red.
5. Mark that task complete in ${PLAN}. Optionally record in Working notes an important, durable fact that future iterations would need. Append a one-line entry to ${PROGRESS}: what you did, and what is next.
6. Commit this iteration's work by invoking the /commit skill.
7. Report: summary = one line on what you did; done = true only if every task in the plan is now complete; blocker = null unless step 1 stopped you.`

let iteration = 0, done = false
while (!done) {
  iteration++
  if (iteration > MAX) throw new Error(`ralph-loop exceeded ${MAX} iterations without completing`)
  const status = await agent(PROMPT, { label: `iter-${iteration}`, model: MODEL, schema: STATUS })
  if (!status) throw new Error(`ralph-loop: iteration ${iteration} returned no result`)
  if (status.blocker) throw new Error(`ralph-loop: ${status.blocker}`)
  log(`iter ${iteration}: ${status.summary}`)
  done = status.done
}
log(`ralph-loop complete after ${iteration} iteration(s).`)
return { iterations: iteration }
