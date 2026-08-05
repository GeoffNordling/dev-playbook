export const meta = {
  name: 'traverse',
  description: "One issue's machine phases through the software factory: the build arc publishes the carrier and lands the issue at the review stop; the judgments arc settles the semantic gate in judged rounds. A clerk label read picks which.",
  whenToUse: 'The issue overwatch reaches a machine phase (`phase:build` or `phase:judgments`). Pass one plain string, "<owner>/<repo> <issue-number>". Returns a DONE or ESCALATE payload; recovery is always relaunch.',
  phases: [
    { title: 'Dispatch', detail: "a clerk reads the issue's labels fresh; the label picks the arc" },
    { title: 'Build', detail: 'one builder node builds, commits, and publishes the carrier' },
    { title: 'Judgments', detail: 'fixer rounds against the semantic gate, judges nested per round' },
    { title: 'Reap', detail: "the reaper removes the run's throwaway worktrees and branches" },
  ],
}

// ---------------------------------------------------------------------------
// A NOTE ON THE LANGUAGE, for a Python reader
//
// This is JavaScript. `const x = ...` binds a name once; `` `text ${expr}` `` is
// an f-string; `xs.map(f)` is a comprehension; `(a) => a + 1` is a lambda;
// `a?.b` is `a.b if a is not None else None`; `a ?? b` is `a if a is not None
// else b`; `throw new Error(m)` is `raise RuntimeError(m)`. The whole script
// body runs inside an async function, so top-level `await` is legal.
//
// The runtime built-ins used below — agent(), workflow(), phase(), log(), and
// the `args` global — are supplied by the Workflow runtime, not by JavaScript.
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// WHAT THIS SCRIPT MAY AND MAY NOT DO
//
// A workflow script is deterministic and has NO shell, NO filesystem, and NO
// network. So every fact about the world arrives as an agent's return value and
// every act on the world is an agent's act:
//
//   - Labels are the clerk's, never this script's. While a run is live the
//     clerk is the issue's one label writer.
//   - Commits and pushes are the builder's and the judgment-facilitator's, each
//     authorized by its own agent type at the git-authority hook. Nothing here
//     grants authority and no brief below asserts any.
//   - Cleanup is the reaper's.
//
// Node briefs therefore carry DATA ONLY — repo, issue number, verdicts,
// commands, carrier state. The procedure each node follows lives in its agent
// definition under dotfiles/dot-claude/agents/, read at session start. A brief
// that re-spelled the procedure would be a second copy of it, free to drift.
//
// Models are NOT passed: each definition's frontmatter pins its own, and a
// ruled pin is not this script's to override. Effort IS pinned here, per node
// type, because it is a property of the job rather than of the agent.
// ---------------------------------------------------------------------------

const JUDGED_ROUND_CAP = 3

// Effort per node type (the human's picks, 2026-08-05). Reading and reaping are
// mechanical; building and fixing are not.
const EFFORT = {
  clerk: 'low',
  reaper: 'low',
  builder: 'xhigh',
  'judgment-facilitator': 'xhigh',
}

// Which node types run behind the harness write fence. A fenced node is spawned
// with `isolation: 'worktree'` and cannot write outside its own worktree — that
// containment is the harness's, not this script's, and it is why a node's brief
// never needs to police placement. The reaper is deliberately NOT fenced:
// cleaning up other worktrees reaches outside any one of them by nature.
const FENCED = new Set(['builder', 'judgment-facilitator'])

// ---------------------------------------------------------------------------
// Arguments
// ---------------------------------------------------------------------------

// The Workflow tool serializes whatever it is handed, so `args` always arrives
// as a string (or undefined when omitted) — probed, and the same contract the
// other workflows in this directory carry. Ours is one plain line.
const ARG_SHAPE = '"<owner>/<repo> <issue-number>"'

function parseArgs(raw) {
  if (raw == null)
    throw new Error(`traverse: args is required — pass ${ARG_SHAPE}`)
  if (typeof raw !== 'string')
    throw new Error(`traverse: args must be a string, got ${typeof raw}`)
  const fields = raw.trim().split(/\s+/).filter((f) => f !== '')
  if (fields.length !== 2)
    throw new Error(`traverse: args must be exactly ${ARG_SHAPE}, got ${JSON.stringify(raw)}`)
  const [repo, issue] = fields
  if (!/^[^/\s]+\/[^/\s]+$/.test(repo))
    throw new Error(`traverse: "${repo}" is not an <owner>/<repo> handle`)
  if (!/^[0-9]+$/.test(issue))
    throw new Error(`traverse: "${issue}" is not an issue number`)
  return { repo, issue }
}

const { repo: REPO, issue: ISSUE } = parseArgs(args)
const HANDLE = `${REPO}#${ISSUE}`
const CARRIER = `issue-${ISSUE}`

// ---------------------------------------------------------------------------
// Schemas
//
// Every node returns through harness schema enforcement, and every schema
// requires `status: done|escalate` — a node cannot end ambiguously. The escalate
// payload's fields ride every schema too, because a node's own account is the
// only account of a failure the launcher ever gets.
// ---------------------------------------------------------------------------

const ESCALATE_FIELDS = {
  status: {
    type: 'string',
    enum: ['done', 'escalate'],
    description: 'done when you finished the brief as written; escalate when you did not.',
  },
  reason: {
    type: ['string', 'null'],
    description: 'One line naming what stopped you. Null when status is done.',
  },
  brief: {
    type: ['string', 'null'],
    description:
      'What the person deciding needs in order to decide: what you were doing, what happened, and the call you need. Null when status is done.',
  },
  cwd: { type: ['string', 'null'], description: 'Your working directory. Null if you never established one.' },
  branch: { type: ['string', 'null'], description: 'The branch you were on. Null if none.' },
  sha: { type: ['string', 'null'], description: 'HEAD at the moment you stopped. Null if none.' },
}

const ESCALATE_KEYS = Object.keys(ESCALATE_FIELDS)

function nodeSchema(extraProperties) {
  return {
    type: 'object',
    additionalProperties: false,
    required: [...ESCALATE_KEYS, ...Object.keys(extraProperties)],
    properties: { ...ESCALATE_FIELDS, ...extraProperties },
  }
}

const SCHEMA = {
  clerk: nodeSchema({
    labels: {
      type: 'array',
      items: { type: 'string' },
      description: 'Every label on the issue, verbatim, as of your last read.',
    },
    detail: { type: 'string', description: 'One line: what you read, or the move you made.' },
  }),
  reaper: nodeSchema({
    removed: { type: 'array', items: { type: 'string' }, description: 'Each worktree path and branch you removed.' },
    alreadyGone: { type: 'array', items: { type: 'string' }, description: 'Each brief-named leaving that was already cleaned.' },
    detail: { type: 'string', description: 'One line: what the sweep came to.' },
  }),
  builder: nodeSchema({
    worktree: { type: 'string', description: 'The absolute path of the worktree you worked in.' },
    detail: { type: 'string', description: 'One line: what you built and whether you published the carrier.' },
  }),
  'judgment-facilitator': nodeSchema({
    worktree: { type: 'string', description: 'The absolute path of the worktree you worked in.' },
    plan: {
      type: ['string', 'null'],
      description: 'The stdout of `judgments-run plan`, byte-exact and whole. Null only when status is escalate.',
    },
    fixed: { type: 'array', items: { type: 'string' }, description: 'The id of each refuted verdict you fixed.' },
    escalated: { type: 'array', items: { type: 'string' }, description: 'The id of each verdict you escalated instead of fixing.' },
    detail: { type: 'string', description: 'One line: what this round came to.' },
  }),
}

// ---------------------------------------------------------------------------
// The node call, and the error lane
// ---------------------------------------------------------------------------

// The harness swallows an agent's error into a bare `null` (probed), so a null
// carries no failure text at all and cannot be told apart from a crash. One
// retry covers the transient case — chiefly the auto-mode classifier, whose
// gating is stochastic, so a blocked node is a normal operational event rather
// than a factory defect. A second null is not survivable state to guess at: the
// throw names the node so the run's failure is self-describing.
async function node(agentType, brief, label, phaseTitle) {
  const options = {
    agentType,
    label,
    phase: phaseTitle,
    effort: EFFORT[agentType],
    schema: SCHEMA[agentType],
    ...(FENCED.has(agentType) ? { isolation: 'worktree' } : {}),
  }
  for (let attempt = 1; attempt <= 2; attempt++) {
    let result = null
    try {
      result = await agent(brief, options)
    } catch (e) {
      log(`traverse: ${label} threw on attempt ${attempt}: ${e?.message ?? e}`)
    }
    if (result != null) return result
    if (attempt === 1) log(`traverse: ${label} returned null — retrying once`)
  }
  throw new Error(
    `traverse: ${HANDLE} — the ${label} node (agentType ${agentType}) returned null twice. ` +
      `The harness swallows an agent error into null, so the node's own account is lost. ` +
      `Recovery is relaunching the traverse, which re-reads the labels and resumes from origin/${CARRIER}.`,
  )
}

// ---------------------------------------------------------------------------
// Return payloads
//
// An escalation is the run's RETURN VALUE, never a throw: the launcher posts it
// verbatim as a comment on the issue, so it has to survive as data. On any
// node's escalate the run stops where it stands — no further nodes, no reap,
// labels untouched.
// ---------------------------------------------------------------------------

// The state block is a REPORT, NOT A GUARANTEE. The harness auto-removes an
// unchanged worktree when its agent ends, so a path here may already be dead by
// the time anyone reads it. Consumers tolerate that; nothing acts on it blind.
// `status` is destructured out deliberately: a node's own lowercase `escalate`
// must never reach the spread below, where it would overwrite the uppercase
// marker the launcher parses. Whatever else the node returned rides along — its
// detail, labels, or fixed ids are exactly the context an escalation wants.
function escalation(nodeName, result) {
  const { status, reason, brief, cwd, worktree, branch, sha, ...rest } = result
  return {
    status: 'ESCALATE',
    issue: HANDLE,
    node: nodeName,
    reason: reason ?? null,
    brief: brief ?? null,
    state: {
      cwd: cwd ?? null,
      worktree: worktree ?? null,
      branch: branch ?? null,
      sha: sha ?? null,
    },
    ...rest,
  }
}

function done(arc, detail) {
  return { status: 'DONE', issue: HANDLE, arc, detail }
}

// ---------------------------------------------------------------------------
// Briefs — data only
// ---------------------------------------------------------------------------

const head = () => [`repo: ${REPO}`, `issue: ${ISSUE}`]

const clerkRead = () => [...head(), 'instruction: read'].join('\n')

const clerkMove = (from, to) => [...head(), `instruction: ${from} -> ${to}`].join('\n')

// The builder needs to know whether the carrier already exists: if it does, this
// is a rework pass and the node adopts published work before building; if not,
// this is a first build and the node's push is what gives the carrier birth.
//
// This script cannot establish that fact. It has no shell, and the clerk — the
// only node running before the builder — touches labels and nothing else by its
// own definition. Nor do the labels answer it: `phase:build` reads identically
// on a first build and on a rework relaunch. So the brief settles the question
// with a deterministic probe rather than an assertion this script would be
// guessing at. `git ls-remote` is a read, and a command in a brief is data.
const buildBrief = () =>
  [
    ...head(),
    `carrier branch: ${CARRIER}`,
    `carrier exists on origin: establish it with \`git ls-remote --heads origin ${CARRIER}\` before anything else.` +
      ` Output means it exists — a rework pass, so adopt it. No output means it does not — a first build, and your push is what creates it.`,
  ].join('\n')

// The entry round carries neither a record command nor verdicts: its job is the
// plan alone. Every later round carries exactly what the prior round's judges
// returned, and nothing else — the node fixes what the verdicts name.
const fixerBrief = (verdicts) => {
  const lines = [...head(), `carrier branch: ${CARRIER}`]
  if (verdicts == null) {
    lines.push('round: entry — no record command and no refuted verdicts. The fresh plan is your whole job.')
    return lines.join('\n')
  }
  lines.push(`record command: ${verdicts.record ?? 'none — nothing passed in the prior round'}`)
  lines.push(`refuted verdicts (${verdicts.refuted.length}):`)
  lines.push(JSON.stringify(verdicts.refuted, null, 2))
  if (verdicts.crashed.length)
    lines.push(`judgments that crashed unruled (not refutations — they were never judged): ${verdicts.crashed.join(' ')}`)
  return lines.join('\n')
}

const reaperBrief = (prefixes) => [`repo: ${REPO}`, 'prefixes:', ...prefixes.map((p) => `  ${p}`)].join('\n')

// ---------------------------------------------------------------------------
// Reaping
// ---------------------------------------------------------------------------

// The harness names a workflow agent's worktree `wf_<runId>-<n>` and its branch
// `worktree-wf_<runId>-<n>` (probed). Both prefixes go to the reaper: sweeping
// only the worktree form would leave one harness branch standing per changed
// tree, since that branch name does not begin with the directory name.
//
// The run prefix is taken from a path a node actually REPORTED, never guessed,
// and it is cut at the LAST dash before the trailing index — cutting at the
// first dash would widen the prefix to every run whose id shares a leading
// segment, and the reaper deletes exactly what a prefix names.
function runPrefixes(worktreePaths) {
  const prefixes = new Set()
  for (const path of worktreePaths) {
    if (typeof path !== 'string' || path.trim() === '') continue
    const base = path.replace(/\/+$/, '').split('/').pop()
    const match = /^(wf_.+-)\d+$/.exec(base)
    if (!match) {
      log(`traverse: worktree "${path}" is not harness-named wf_<runId>-<n> — leaving it alone`)
      continue
    }
    prefixes.add(match[1])
    prefixes.add(`worktree-${match[1]}`)
  }
  return [...prefixes]
}

async function reap(worktreePaths) {
  const prefixes = runPrefixes(worktreePaths)
  if (prefixes.length === 0) {
    log('traverse: no reapable prefixes reported — nothing to reap')
    return null
  }
  phase('Reap')
  return await node('reaper', reaperBrief(prefixes), 'reaper', 'Reap')
}

// ---------------------------------------------------------------------------
// The plan gate
// ---------------------------------------------------------------------------

// Zero jobs is green: every judgment the repo declares is already cached as a
// pass against the current content. Deciding that is mechanical, so it is done
// here in plain code rather than by a model — and a plan this script cannot
// read is fatal, never assumed green. Judgments are never softened to pass.
function jobCount(planString) {
  if (typeof planString !== 'string' || planString.trim() === '')
    throw new Error(`traverse: ${HANDLE} — the judgments round returned no plan; \`judgments-run plan\` stdout is what decides green`)
  let plan
  try {
    plan = JSON.parse(planString)
  } catch (e) {
    throw new Error(`traverse: ${HANDLE} — the round's plan is not JSON (${e.message}); it must be \`judgments-run plan\` stdout, byte-exact`)
  }
  if (plan === null || typeof plan !== 'object' || !Array.isArray(plan.jobs))
    throw new Error(`traverse: ${HANDLE} — the round's plan has no "jobs" array; this script and judgments-run have drifted apart`)
  return plan.jobs.length
}

// The nested judgments run returns the object judgments.js builds. Anything else
// means the runtime's nesting contract has moved under us, and the next round's
// brief would carry nonsense — so it throws here instead.
function checkVerdicts(verdicts, round) {
  if (verdicts === null || typeof verdicts !== 'object' || Array.isArray(verdicts))
    throw new Error(`traverse: ${HANDLE} — round ${round}'s nested judgments run returned ${typeof verdicts}, not a verdict object`)
  for (const key of ['passed', 'refuted', 'crashed'])
    if (!Array.isArray(verdicts[key]))
      throw new Error(`traverse: ${HANDLE} — round ${round}'s verdicts are missing the "${key}" array`)
  return verdicts
}

// ---------------------------------------------------------------------------
// Dispatch — the first act is always a fresh label read
// ---------------------------------------------------------------------------

// Label state passed by the launcher is never trusted, because trusting it is
// what would make recovery an investigation. Reading the labels at run start
// instead makes RELAUNCH THE UNIVERSAL RECOVERY: a relaunched run acts on where
// the issue actually stands, so the human's answer to any failure is one launch.
function arcOf(labels) {
  if (!Array.isArray(labels)) return null
  const phaseLabels = labels.filter((l) => typeof l === 'string' && l.startsWith('phase:'))
  if (phaseLabels.length !== 1) return null
  const name = phaseLabels[0].slice('phase:'.length)
  return name === 'build' || name === 'judgments' ? name : null
}

log(`traverse: ${HANDLE}, carrier ${CARRIER}`)

phase('Dispatch')

const read = await node('clerk', clerkRead(), 'clerk:read', 'Dispatch')
if (read.status === 'escalate') return escalation('clerk', read)

const arc = arcOf(read.labels)
log(`traverse: labels [${read.labels.join(', ')}] → arc ${arc ?? 'none'}`)

// ---------------------------------------------------------------------------
// The build arc
// ---------------------------------------------------------------------------

if (arc === 'build') {
  phase('Build')
  const built = await node('builder', buildBrief(), 'builder', 'Build')
  if (built.status === 'escalate') return escalation('builder', built)
  log(`traverse: build done — ${built.detail}`)

  const moved = await node('clerk', clerkMove('phase:build', 'phase:pr-review'), 'clerk:move', 'Build')
  if (moved.status === 'escalate') return escalation('clerk', moved)

  const swept = await reap([built.worktree])
  if (swept?.status === 'escalate') return escalation('reaper', swept)

  // The traverse ends here by design. The review stop that follows — /open-pr,
  // the audit tracks, the human's one verdict — is the sequencing session's,
  // and the judgments arc is entered only by that human's approve verdict.
  return done('build', `built and published origin/${CARRIER}; the issue now stands at phase:pr-review`)
}

// ---------------------------------------------------------------------------
// The judgments arc
// ---------------------------------------------------------------------------

if (arc === 'judgments') {
  phase('Judgments')
  let verdicts = null
  const trees = []

  // One iteration past the cap: the last pass is a fixer round whose job is to
  // record the final judged round's passes and re-plan. If THAT plan still has
  // jobs, the gate is genuinely red and the run escalates with the refutations.
  for (let round = 1; round <= JUDGED_ROUND_CAP + 1; round++) {
    const fix = await node('judgment-facilitator', fixerBrief(verdicts), `judgments:round-${round}`, 'Judgments')
    if (fix.status === 'escalate') return escalation('judgment-facilitator', fix)
    trees.push(fix.worktree)

    const jobs = jobCount(fix.plan)
    log(`traverse: round ${round} — ${jobs} uncached judgment(s); fixed [${fix.fixed.join(', ')}]`)
    if (jobs === 0) break

    if (round === JUDGED_ROUND_CAP + 1)
      return escalation('judgments-red', {
        reason: `the judgment gate is still red after ${JUDGED_ROUND_CAP} judged rounds`,
        brief:
          `The semantic gate on ${HANDLE} did not close in ${JUDGED_ROUND_CAP} judged rounds. The refuted verdicts are below, ` +
          `and the work stands on origin/${CARRIER}. Judgments are never softened to pass, so the call is yours: the artifact ` +
          `needs a fix the rounds could not make, or a judgment itself is wrong and its declaration needs changing.`,
        worktree: fix.worktree,
        cwd: fix.cwd,
        branch: fix.branch,
        sha: fix.sha,
        refuted: verdicts?.refuted ?? [],
      })

    // The nested call spends the one legal nesting level, and the plan travels
    // as a string, byte-identical — the child re-validates it before a single
    // judge spawns, so a mangled transit fails there rather than half-running.
    verdicts = checkVerdicts(await workflow('judgments', fix.plan), round)
    log(`traverse: round ${round} judged — ${verdicts.passed.length} passed, ${verdicts.refuted.length} refuted, ${verdicts.crashed.length} crashed`)
  }

  const swept = await reap(trees)
  if (swept?.status === 'escalate') return escalation('reaper', swept)

  // No onward label move: the issue sits at phase:judgments through the human's
  // final read and merge. The sequencing session's close-out follows this DONE.
  return done('judgments', `the judgment gate is green on origin/${CARRIER}`)
}

// ---------------------------------------------------------------------------
// Neither arc — refuse to guess
// ---------------------------------------------------------------------------

return escalation('dispatch', {
  reason: `the issue is not at a machine phase — labels [${read.labels.join(', ')}]`,
  brief:
    `A traverse run serves ${'`phase:build`'} or ${'`phase:judgments`'} and nothing else, and ${HANDLE} carries neither. ` +
    `Nothing was touched — no node ran past the label read, and no label moved. Either the issue is at the review stop ` +
    `(the sequencing session's, not a run's) or its phase label is missing or doubled and needs setting by hand.`,
})
