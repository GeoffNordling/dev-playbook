export const meta = {
  name: 'simulate-fact-base',
  description: 'Simulate a fact base of kinds for a target repo: one Opus planner, one Sonnet builder per slice of 3-5 kinds, one Opus assembler',
  whenToUse: 'A run of the fact-base simulation; see simulate-fact-base/process.md',
  phases: [
    { title: 'Plan', detail: 'find the kinds, group them into slices, one brief each', model: 'opus' },
    { title: 'Build', detail: 'one builder per slice, in parallel', model: 'sonnet' },
    { title: 'Assemble', detail: 'list instances by script, merge the kinds, draft the doc-types', model: 'opus' },
  ],
}

// args: { repo, target, run, maxSlices, scope }. Paths absolute; scope is a list of folders or 'all'.
// Every prompt lives in prompts/ and is read by path; this script passes parameters only.
for (const key of ['repo', 'target', 'run']) {
  if (!args || !args[key] || !args[key].startsWith('/')) {
    throw new Error(`args.${key} must be an absolute path`)
  }
}
const { repo, target, run } = args
const maxSlices = args.maxSlices ?? 10
const scope = args.scope ?? 'all'
if (scope !== 'all' && !Array.isArray(scope)) throw new Error('args.scope must be a list of folders or "all"')
const prompts = `${repo}/workstreams/system/see/story-forge/simulate-fact-base/prompts`

const params = extra =>
  [`repo: ${repo}`, `target: ${target}`, `run: ${run}`, ...extra].join('\n')

const PLAN_SCHEMA = {
  type: 'object',
  properties: {
    targetCommit: { type: 'string' },
    slices: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          kinds: { type: 'array', items: { type: 'string' } },
          folders: { type: 'array', items: { type: 'string' } },
        },
        required: ['id', 'kinds', 'folders'],
      },
    },
    unplaced: { type: 'array', items: { type: 'string' } },
  },
  required: ['targetCommit', 'slices', 'unplaced'],
}

const BUILD_SCHEMA = {
  type: 'object',
  properties: {
    slice: { type: 'string' },
    kinds: { type: 'array', items: { type: 'string' } },
    edges: { type: 'integer' },
    stubs: { type: 'integer' },
    undeclared: { type: 'integer' },
    unexpressible: { type: 'array', items: { type: 'string' } },
    doesNotFit: { type: 'array', items: { type: 'string' } },
  },
  required: ['slice', 'kinds', 'edges', 'stubs', 'undeclared', 'unexpressible', 'doesNotFit'],
}

const ASSEMBLE_SCHEMA = {
  type: 'object',
  properties: {
    kinds: { type: 'integer' },
    instances: { type: 'integer' },
    edges: { type: 'integer' },
    danglingStubs: { type: 'integer' },
    overlaps: { type: 'integer' },
    orphans: { type: 'integer' },
    conflicts: { type: 'integer' },
    declarationsSuggested: { type: 'integer' },
    storyProjectionTest: { type: 'string', description: 'pass or fail for each half, with receipts, and where any gap lies' },
  },
  required: ['kinds', 'instances', 'edges', 'danglingStubs', 'overlaps', 'orphans', 'conflicts', 'declarationsSuggested', 'storyProjectionTest'],
}

phase('Plan')
const plan = await agent(
  `Read ${prompts}/plan.md and follow it.\n\n${params([`maxSlices: ${maxSlices}`, `scope: ${JSON.stringify(scope)}`])}`,
  { label: 'plan', phase: 'Plan', model: 'opus', schema: PLAN_SCHEMA },
)
if (!plan) throw new Error('the plan agent returned nothing')
if (plan.slices.length > maxSlices) {
  throw new Error(`the plan made ${plan.slices.length} slices; the limit is ${maxSlices}`)
}
const oversized = plan.slices.filter(s => s.kinds.length > 5).map(s => `${s.id} (${s.kinds.length})`)
if (oversized.length) throw new Error(`slices over 5 kinds: ${oversized.join(', ')}`)
log(`${plan.slices.length} slices at ${plan.targetCommit.slice(0, 8)}: ${plan.slices.map(s => `${s.id} [${s.kinds.join(', ')}]`).join('; ')}`)
if (plan.unplaced.length) log(`${plan.unplaced.length} files unplaced by the plan: ${plan.unplaced.slice(0, 10).join(', ')}`)

phase('Build')
const built = await parallel(plan.slices.map(s => () =>
  agent(
    `Read ${prompts}/build.md and follow it.\n\n${params([`slice: ${s.id}`])}`,
    { label: `build:${s.id}`, phase: 'Build', model: 'sonnet', schema: BUILD_SCHEMA },
  ),
))
const missing = plan.slices.filter((s, i) => !built[i]).map(s => s.id)
if (missing.length) throw new Error(`these builders returned nothing: ${missing.join(', ')}`)

phase('Assemble')
const assembled = await agent(
  `Read ${prompts}/assemble.md and follow it.\n\n${params([])}`,
  { label: 'assemble', phase: 'Assemble', model: 'opus', schema: ASSEMBLE_SCHEMA },
)
if (!assembled) throw new Error('the assembler returned nothing')

return { plan, built, assembled }
