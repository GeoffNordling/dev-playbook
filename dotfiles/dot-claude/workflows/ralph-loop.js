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
//   checkCmd      the iteration check gate: a shell command meaning "green" (e.g. 'make check',
//                 'make -C tools check', an && -chain); '' or whitespace-only means no gate
//
// NOTE (2026-06-25, re-probed 2026-07-31): the Workflow runtime's own docs are wrong here — they
// say objects/arrays reach the script verbatim, but every args value actually arrives
// JSON-serialized to a string (or undefined when omitted), so the contract is: the caller passes
// an object, this script parses it. Re-verified directly against the runtime with a probe workflow
// that reported `typeof args` for both a passed object ("string") and an omitted one ("undefined").
const ARG_TYPES = { model: 'string', maxIters: 'number', planFile: 'string', progressFile: 'string', checkCmd: 'string' }

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

const { model: MODEL, maxIters: MAX, planFile: PLAN, progressFile: PROGRESS, checkCmd: CHECK_RAW } = parseArgs(args)
// Empty string (or whitespace-only) is the explicit "no gate" value — the caller opts out consciously.
const CHECK = CHECK_RAW.trim()

phase('Iterate')

log(`ralph-loop config: model=${MODEL}, maxIters=${MAX}, planFile=${PLAN}, progressFile=${PROGRESS}, checkCmd=${CHECK ? CHECK : '(none)'}`)

const STATUS = {
  type: 'object', additionalProperties: false,
  required: ['done', 'blocker', 'summary'],
  properties: {
    done:    { type: 'boolean', description: 'true ONLY when every task in the plan is complete' },
    blocker: { type: ['string', 'null'], description: 'one-line reason the loop must stop — the check gate fails on entry, or a required file missing/unreadable; null if none' },
    summary: { type: 'string',  description: 'one line: what this iteration did' },
  },
}

// The check gate is loop config (the checkCmd arg), interpolated into the prompt here.
// When set, the agent runs it at entry (step 1) and pre-commit (step 4); when empty, there is no gate.
const step1 = CHECK
  ? `Run \`${CHECK}\`. If it does not pass, or if ${PLAN} or ${PROGRESS} is missing or unreadable, set blocker to a one-line reason and STOP — do nothing else. Red on entry is not yours to fix; it means a prior iteration left the repo broken.`
  : `This loop has no check gate, so there is nothing to run here. If ${PLAN} or ${PROGRESS} is missing or unreadable, set blocker to a one-line reason and STOP — do nothing else.`
const step4 = CHECK
  ? `Run \`${CHECK}\` again. If your work broke it, fix until it passes. Never commit red.`
  : `This loop has no check gate, so there is nothing to run. Still, never commit work you believe is broken.`

const PROMPT = `Work in the current directory — do not cd; use relative paths.

The plan is in ${PLAN}; the running log of work so far is in ${PROGRESS}. Both must already exist.

1. ${step1}
2. Read ${PLAN} (the plan) and ${PROGRESS} (the log of what past iterations did).
3. Find the next incomplete task in the plan and implement it — one task only, small enough to finish cleanly in this iteration.
4. ${step4}
5. Mark that task complete in ${PLAN}. Optionally record in Working notes an important, durable fact that future iterations would need. Append a one-line entry to ${PROGRESS}: what you did, and what is next.
6. Commit this iteration's work by invoking the /commit skill. Expect this to be
   denied: an iteration holds no lane of the git-authority hook's commit rule
   family, so the loop has no commit authorization of its own — see issue #351.
   Report the denial through blocker rather than re-spelling the command.
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
