export const meta = {
  name: 'ralph-loop',
  description: 'Pure Ralph loop: boot a fresh agent each iteration to grind a fixed goal to done. Disk (GOAL.md, PROGRESS.md, git) is the only memory; loop control lives in this runtime, not in any context window.',
  whenToUse: 'A well-specified, bounded goal you want ground out autonomously without holding it in one context window. Launch from the target repo or worktree — agents inherit that cwd. Seed GOAL.md (or pass args.goal) first.',
  phases: [{ title: 'Iterate' }],
}

// args (all optional):
//   goal      inline goal text; if omitted, each agent reads GOAL.md from the cwd
//   model     worker model override ('haiku' | 'sonnet' | 'opus' | ...); omit to inherit
//   maxIters  safety rail (default 50); throws if exceeded without completing
//   commit    each iteration commits its work (default true)
const GOAL   = args?.goal ?? null
const MODEL  = args?.model ?? undefined
const MAX    = args?.maxIters ?? 50
const COMMIT = args?.commit ?? true

phase('Iterate')

const STATUS = {
  type: 'object', additionalProperties: false,
  required: ['done', 'noGoal', 'summary'],
  properties: {
    done:    { type: 'boolean', description: 'true ONLY when the goal is fully satisfied, nothing left' },
    noGoal:  { type: 'boolean', description: 'true if you found NO goal — no inline goal in the prompt AND no readable GOAL.md' },
    summary: { type: 'string',  description: 'one line: what this iteration did' },
  },
}

const goalClause = GOAL
  ? `Your fixed goal:\n\n${GOAL}`
  : `Your fixed goal is written in GOAL.md — read it.`

const commitStep = COMMIT
  ? `4. Commit everything: \`git add -A && git commit -m "ralph: <what you did>"\`.`
  : `4. (Committing is disabled this run — leave changes uncommitted.)`

const PROMPT = `You are ONE iteration of a Ralph loop. You boot with NO memory of prior iterations — the files on disk in your working directory are your only state. Do NOT cd; work where you are, with relative paths.

${goalClause}

If you can find NO goal — nothing stated above and no readable GOAL.md — set noGoal=true and STOP (do nothing else). Otherwise:

1. Read PROGRESS.md if it exists — it is the running log of what past iterations did.
2. Do the SINGLE next unit of work toward the goal, small enough to finish and commit cleanly in this one iteration.
3. Append a one-line entry to PROGRESS.md: what you did, and what is next.
${commitStep}
5. Report status: done=true ONLY if the goal is now fully satisfied; otherwise done=false.`

let iteration = 0, done = false
while (!done) {
  iteration++
  if (iteration > MAX) throw new Error(`ralph-loop exceeded ${MAX} iterations without completing — stopping loud.`)
  const status = await agent(PROMPT, { label: `iter-${iteration}`, model: MODEL, schema: STATUS })
  if (!status) throw new Error(`ralph-loop: iteration ${iteration} returned no result — stopping loud.`)
  if (status.noGoal) throw new Error(`ralph-loop: no goal found — pass args.goal or seed GOAL.md — stopping loud.`)
  log(`iter ${iteration}: ${status.summary}`)
  done = status.done
}
log(`ralph-loop complete after ${iteration} iteration(s).`)
return { iterations: iteration }
