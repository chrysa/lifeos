export const meta = {
  name: 'chrysa-feature',
  description: 'Feature delivery: spec+plan with critique (design) or implement+verify+review (build)',
  whenToUse: 'Called by /wf-feature. mode=design before the human gate, mode=build after spec+plan approval.',
  phases: [
    { title: 'Spec', detail: 'general-pm writes reports/specs/<feature>.md via /spec' },
    { title: 'Plan', detail: 'general-solution-architect writes reports/plans/<feature>.md via /plan' },
    { title: 'Critique', detail: 'three independent critics challenge spec+plan' },
    { title: 'Implement', detail: 'fullstack agent applies the approved plan via /implement (TDD)' },
    { title: 'Verify', detail: 'make test + make lint loop until green (max 3 rounds)' },
    { title: 'Review', detail: 'code-reviewer + security-auditor (+ architecture on large diffs)' },
  ],
}

// args: { feature: string, mode: 'design' | 'build' }
const FEATURE = args && args.feature
const MODE = args && args.mode === 'build' ? 'build' : 'design'
const MAX_VERIFY_ROUNDS = 3
const LARGE_DIFF_LINES = 300

const ISSUES_SCHEMA = {
  type: 'object',
  properties: {
    issues: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
          where: { type: 'string' },
          problem: { type: 'string' },
          suggestion: { type: 'string' },
        },
        required: ['severity', 'where', 'problem'],
      },
    },
  },
  required: ['issues'],
}

const VERIFY_SCHEMA = {
  type: 'object',
  properties: {
    green: { type: 'boolean' },
    diffLines: { type: 'number' },
    failures: { type: 'array', items: { type: 'string' } },
  },
  required: ['green', 'diffLines', 'failures'],
}

const CRITIC_LENSES = [
  'scope & risk: missing acceptance criteria, hidden scope, irreversible steps, rollback',
  'architecture & chrysa standards: layer boundaries, contracts, ADR needed, containers-only, no hardcoded constants',
  'testability: every acceptance criterion maps to a test, edge cases, test data, CI cost',
]

// Fall back to the default workflow subagent when a repo does not ship the named agent.
async function runAgent(prompt, opts) {
  try {
    return await agent(prompt, opts)
  } catch (error) {
    log(`agentType ${opts.agentType} unavailable, using default subagent`)
    return agent(prompt, { ...opts, agentType: undefined })
  }
}

async function design() {
  phase('Spec')
  await runAgent(
    `Run the /spec skill for feature "${FEATURE}". Write reports/specs/${FEATURE}.md. ` +
      'Return the spec path and its acceptance criteria as a short list.',
    { agentType: 'general-pm', label: 'spec' },
  )
  phase('Plan')
  await runAgent(
    `Run the /plan skill for feature "${FEATURE}" from reports/specs/${FEATURE}.md. ` +
      `Write reports/plans/${FEATURE}.md. Flag any decision that needs an ADR (/adr-new). Return the plan path.`,
    { agentType: 'general-solution-architect', label: 'plan' },
  )
  phase('Critique')
  const critiques = await parallel(
    CRITIC_LENSES.map((lens, i) => () =>
      agent(
        `Critique reports/specs/${FEATURE}.md and reports/plans/${FEATURE}.md through this lens only: ${lens}. ` +
          'Read-only: do not edit files. Report concrete issues; return an empty list if none.',
        { schema: ISSUES_SCHEMA, label: `critic-${i + 1}`, phase: 'Critique' },
      ),
    ),
  )
  const issues = critiques.filter(Boolean).flatMap((c) => c.issues)
  return {
    mode: 'design',
    spec: `reports/specs/${FEATURE}.md`,
    plan: `reports/plans/${FEATURE}.md`,
    blockers: issues.filter((i) => i.severity === 'blocker'),
    issues,
    next: 'HUMAN GATE: approve spec+plan, then run mode=build',
  }
}

async function verifyLoop() {
  let last = null
  for (let round = 1; round <= MAX_VERIFY_ROUNDS; round++) {
    last = await runAgent(
      'Run the verification-loop skill: `make test` and `make lint` (in containers, never on the host). ' +
        'If anything fails, fix the code (never the test expectations unless the test is wrong) and re-run. ' +
        'Report green, the diff size in changed lines (`git diff --stat` vs the base branch) and remaining failures.',
      { agentType: 'test-runner', schema: VERIFY_SCHEMA, label: `verify-${round}`, phase: 'Verify' },
    )
    if (last && last.green) return last
    log(`verify round ${round}/${MAX_VERIFY_ROUNDS} still red`)
  }
  return last
}

function reviewers(diffLines) {
  const list = [
    { type: 'code-reviewer', focus: 'correctness, tests, AGENTS.md conventions' },
    { type: 'security-auditor', focus: 'secrets, input validation, authz, injection, unsafe deserialisation' },
  ]
  if (diffLines > LARGE_DIFF_LINES) list.push({ type: 'general-solution-architect', focus: 'layer boundaries, ADR coverage' })
  return list
}

async function build() {
  phase('Implement')
  await runAgent(
    `Run the /implement skill for feature "${FEATURE}" following the APPROVED reports/specs/${FEATURE}.md ` +
      `and reports/plans/${FEATURE}.md. TDD: failing test first. Do not commit, do not push.`,
    { agentType: 'general-fullstack-developer', label: 'implement' },
  )
  phase('Verify')
  const verdict = await verifyLoop()
  if (!verdict || !verdict.green) {
    return { mode: 'build', green: false, failures: verdict ? verdict.failures : ['verify agent died'], findings: [] }
  }
  phase('Review')
  const reviews = await parallel(
    reviewers(verdict.diffLines).map((r) => () =>
      runAgent(`Review the uncommitted diff (review-changes skill). Focus: ${r.focus}. Read-only.`, {
        agentType: r.type,
        schema: ISSUES_SCHEMA,
        label: r.type,
        phase: 'Review',
      }),
    ),
  )
  return {
    mode: 'build',
    green: true,
    diffLines: verdict.diffLines,
    findings: reviews.filter(Boolean).flatMap((r) => r.issues),
    next: 'Fix blocker/major findings, run /security-review, then /commit and open the PR with its Shortcut story',
  }
}

// The slug becomes a file path (reports/specs/<slug>.md): restrict it to a safe charset.
if (!FEATURE || !/^[a-z0-9][a-z0-9-]{0,63}$/.test(FEATURE)) throw new Error('args.feature must be a kebab-case slug')
return MODE === 'build' ? await build() : await design()
