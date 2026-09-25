export const meta = {
  name: 'simulate-fact-base',
  description: 'Simulate a fact base for story-forge: one Opus planner, one Sonnet builder per slice, one Opus assembler',
  whenToUse: 'A run of the story-forge fact-base simulation; see simulate-fact-base/process.md',
  phases: [
    { title: 'Plan', detail: 'split story-forge into slices, one brief each', model: 'opus' },
    { title: 'Build', detail: 'one builder per slice, in parallel', model: 'sonnet' },
    { title: 'Assemble', detail: 'merge the slices, draft the doc-types', model: 'opus' },
  ],
}

// args: { repo, storyForge, run, maxSlices }, all paths absolute.
// Every prompt lives in prompts/ and is read by path; this script passes parameters only.
for (const key of ['repo', 'storyForge', 'run']) {
  if (!args || !args[key] || !args[key].startsWith('/')) {
    throw new Error(`args.${key} must be an absolute path`)
  }
}
const { repo, storyForge, run } = args
const maxSlices = args.maxSlices ?? 6
const prompts = `${repo}/workstreams/system/see/story-forge/simulate-fact-base/prompts`

const params = extra =>
  [`repo: ${repo}`, `storyForge: ${storyForge}`, `run: ${run}`, ...extra].join('\n')

const PLAN_SCHEMA = {
  type: 'object',
  properties: {
    storyForgeCommit: { type: 'string' },
    slices: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          folders: { type: 'array', items: { type: 'string' } },
          fileCount: { type: 'integer' },
          kindsExpected: { type: 'array', items: { type: 'string' } },
        },
        required: ['id', 'folders', 'fileCount', 'kindsExpected'],
      },
    },
    unassignedFiles: { type: 'array', items: { type: 'string' } },
  },
  required: ['storyForgeCommit', 'slices', 'unassignedFiles'],
}

const BUILD_SCHEMA = {
  type: 'object',
  properties: {
    slice: { type: 'string' },
    kinds: { type: 'array', items: { type: 'string' } },
    nodes: { type: 'integer' },
    edges: { type: 'integer' },
    stubs: { type: 'integer' },
    undeclared: { type: 'integer' },
    doesNotFit: { type: 'array', items: { type: 'string' } },
  },
  required: ['slice', 'kinds', 'nodes', 'edges', 'stubs', 'undeclared', 'doesNotFit'],
}

const ASSEMBLE_SCHEMA = {
  type: 'object',
  properties: {
    kinds: { type: 'integer' },
    nodes: { type: 'integer' },
    edges: { type: 'integer' },
    danglingStubs: { type: 'integer' },
    conflicts: { type: 'integer' },
    projectionIsFormOfStory: { type: 'string', description: 'yes with the receipt, or no and what is missing' },
  },
  required: ['kinds', 'nodes', 'edges', 'danglingStubs', 'conflicts', 'projectionIsFormOfStory'],
}

phase('Plan')
const plan = await agent(
  `Read ${prompts}/plan.md and follow it.\n\n${params([`maxSlices: ${maxSlices}`])}`,
  { label: 'plan', phase: 'Plan', model: 'opus', schema: PLAN_SCHEMA },
)
if (!plan) throw new Error('the plan agent returned nothing')
if (plan.unassignedFiles.length) {
  throw new Error(`the plan left ${plan.unassignedFiles.length} files in no slice: ${plan.unassignedFiles.slice(0, 10).join(', ')}`)
}
if (plan.slices.length > maxSlices) {
  throw new Error(`the plan made ${plan.slices.length} slices; the limit is ${maxSlices}`)
}
log(`${plan.slices.length} slices at story-forge ${plan.storyForgeCommit.slice(0, 8)}: ${plan.slices.map(s => `${s.id} (${s.fileCount})`).join(', ')}`)

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
