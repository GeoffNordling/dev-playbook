export const meta = {
  name: 'ralph-loop',
  description: 'Ralph loop: boot a fresh agent each iteration to work a plan to done. Disk (the plan file, the progress file, git) is the only memory; loop control lives in this runtime, not in any context window. The run stops at the first unreviewed checkpoint marker in the plan, or at the end of the plan when it carries none.',
  whenToUse: 'A plan you want ground out autonomously without holding it in one context window. Launch from the target repo or worktree — agents inherit that cwd. Seed the plan and progress files first.',
  phases: [{ title: 'Iterate' }],
}

// args: a required JSON string of options. All fields required; no defaults.
//   model         worker model ('haiku' | 'sonnet' | 'opus' | ...)
//   maxIters      safety rail; returns a blocker if exceeded without reaching a stopping point
//   planFile      the plan: a task list the agent works through and checks off
//   progressFile  the running log appended each iteration
//   checkCmd      the iteration check gate: a shell command meaning "green" (e.g. 'make check',
//                 'make -C tools check', an && -chain); '' or whitespace-only means no gate
//
// There is no arg for where this run stops. The plan file carries that, in the checkpoint markers
// the setup wrote, and the iteration agent reads the plan anyway. An arg could only ever disagree
// with the file, and a disagreement resolves toward blowing through a review point.
//
// NOTE (2026-06-25, re-probed 2026-07-31 and 2026-09-08): how args reaches the script has changed
// across runtime versions. Through 2026-07 every value arrived JSON-serialized to a string; on
// 2026-09-08 the same launch arrived as the object itself (a string passed by the caller was
// parsed by the tool before it reached the script). The contract is therefore: the caller passes
// an object, and this script accepts either form and validates the result the same way.
const ARG_TYPES = { model: 'string', maxIters: 'number', planFile: 'string', progressFile: 'string', checkCmd: 'string' }

function parseArgs(raw) {
  if (raw == null)
    throw new Error(`ralph-loop: args is required — pass {${Object.keys(ARG_TYPES).join(', ')}}`)
  let opts
  if (typeof raw === 'string') {
    try { opts = JSON.parse(raw) }
    catch (e) { throw new Error(`ralph-loop: args is not valid JSON (${e.message})`) }
  } else {
    opts = raw
  }
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

// A checkpoint marker is an HTML comment, so it is invisible wherever the plan renders.
const OPEN = '<!-- [ ] checkpoint -->'
const CLOSED = '<!-- [x] checkpoint -->'

phase('Iterate')

log(`ralph-loop config: model=${MODEL}, maxIters=${MAX}, planFile=${PLAN}, progressFile=${PROGRESS}, checkCmd=${CHECK ? CHECK : '(none)'}`)

// This runtime has no filesystem access, so the iteration agent supplies the one fact the stopping
// rule needs — how many tasks are left in the segment — and the rule itself stays here. The count is
// an observation the agent reads off the plan, never a judgment about whether the loop should end.
const STATUS = {
  type: 'object', additionalProperties: false,
  required: ['tasksLeft', 'blocker', 'summary'],
  properties: {
    tasksLeft: { type: 'integer', minimum: 0, description: 'how many unchecked `- [ ]` task lines remain in your segment after your edit' },
    blocker:   { type: ['string', 'null'], description: 'one-line reason the loop must stop — the check gate fails on entry, a required file missing/unreadable, or a malformed checkpoint marker; null if none' },
    summary:   { type: 'string',  description: 'one line: what this iteration did' },
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

// Every plan ends with a checkpoint, so these clauses are unconditional and there is no plan shape
// they do not cover. The two entry rules together are what guarantee a review after all work: at
// least one unreviewed checkpoint exists, and no unchecked task sits past the last one.
const segmentCheck = ` Then check the checkpoint markers in ${PLAN}: every HTML comment mentioning "checkpoint" must read exactly \`${OPEN}\` or exactly \`${CLOSED}\`, at least one \`${OPEN}\` must be present, and no unchecked task may sit below the last \`${OPEN}\`. If any of those fails, set blocker naming the offending line and STOP — a marker no parser recognizes, or a plan whose work runs past the last one, would let this run reach the end with nobody reviewing it.`
const segmentScope = `Checkpoint markers cut this plan into segments. A line reading exactly \`${OPEN}\` is a checkpoint not yet reviewed; exactly \`${CLOSED}\` is one already reviewed. **Your segment is the part of the plan above the first \`${OPEN}\` line.** Work only inside it: tasks below that line belong to a later segment and are not yours, however ready they look. Never add, remove, move, or edit a marker — a reviewer owns them.`

const PROMPT = `Work in the current directory — do not cd; use relative paths.

The plan is in ${PLAN}; the running log of work so far is in ${PROGRESS}. Both must already exist.

${segmentScope}

1. ${step1}${segmentCheck}
2. Read ${PLAN} (the plan) and ${PROGRESS} (the log of what past iterations did).
3. Find the next incomplete task in your segment and implement it — one task only, small enough to finish cleanly in this iteration.
4. ${step4}
5. Mark that task complete in ${PLAN}. Optionally record in Working notes an important, durable fact that future iterations would need. Append a one-line entry to ${PROGRESS}: what you did, and what is next. Where the plan and its sources did not settle something you had to decide, add one indented line under that entry in the shape ${PROGRESS} gives — never stop for such a point, and never decide one silently.
6. Commit this iteration's work by invoking the /commit skill.
7. Report: summary = one line on what you did; tasksLeft = how many unchecked \`- [ ]\` task lines are left in your segment now that yours is checked off — count them in the file, and do not count a checkpoint marker line; blocker = null unless step 1 stopped you.`

// The loop stops on tasksLeft === 0: the checkpoint this segment ran up to. Whether it is the last
// checkpoint in the plan is not this runtime's question — a review follows either way. Every exit
// returns rather than throws, so the launching session reads a sentence instead of a stack trace.
let iteration = 0, tasksLeft = -1
while (tasksLeft !== 0) {
  iteration++
  if (iteration > MAX) {
    log(`ralph-loop stopped: ${MAX} iterations without reaching a stopping point.`)
    return { iterations: MAX, blocker: `exceeded ${MAX} iterations without reaching a stopping point` }
  }
  const status = await agent(PROMPT, { label: `iter-${iteration}`, model: MODEL, schema: STATUS })
  if (!status) {
    log(`ralph-loop stopped: iteration ${iteration} returned no result.`)
    return { iterations: iteration, blocker: `iteration ${iteration} returned no result` }
  }
  if (status.blocker) {
    log(`ralph-loop stopped: ${status.blocker}`)
    return { iterations: iteration, blocker: status.blocker }
  }
  log(`iter ${iteration}: ${status.summary}`)
  tasksLeft = status.tasksLeft
}
log(`ralph-loop reached its checkpoint after ${iteration} iteration(s).`)
return { iterations: iteration, blocker: null }
