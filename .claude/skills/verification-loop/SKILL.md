---
name: verification-loop
description: "Self-checking loop that re-runs an objective against the work until it provably passes — define success criteria, execute, verify against them, iterate on failure. TRIGGER when: a task needs an explicit pass/fail gate before being called done, or the user asks to 'make sure it actually works' across multiple checks. DO NOT TRIGGER for: a single manual run-and-look (use the verify command), code review (use check), or debugging a known error (use hunt)."
origin: ECC
---

# Verification Loop Skill

A comprehensive verification system for Claude Code sessions.

## The Iron Law

```
NO COMPLETION CLAIM WITHOUT FRESH VERIFICATION EVIDENCE
```

Claiming work is done without running the proof is dishonesty, not efficiency.
If you have not run the verification command *in this session*, you cannot
claim it passes. Evidence before assertions, always.

## The Completion Gate

Run this gate before any status claim or expression of satisfaction:

```
1. IDENTIFY — which command proves this claim?
2. RUN      — execute the FULL command, fresh (no partial/cached runs)
3. READ     — full output, exit code, failure count
4. VERIFY   — does the output confirm the claim?
              NO  -> state the actual status WITH the evidence
              YES -> state the claim WITH the evidence
5. ONLY THEN make the claim
```

Skipping any step is lying, not verifying.

| Claim | Requires | Not sufficient |
| --- | --- | --- |
| Tests pass | Test command output: 0 failures | A previous run, "should pass" |
| Lint clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passed, "logs look fine" |
| Bug fixed | Original symptom retested: passes | Code changed, assumed fixed |
| Regression test works | Red→green cycle verified | Test passes once |
| Agent finished | `git diff` shows the changes | Agent reported "success" |
| Requirements met | Line-by-line checklist vs. the plan | "Tests pass, so done" |

## Rationalization Watch

When one of these surfaces, stop — it is the moment work ships unverified:

| What you're thinking | Reality |
| --- | --- |
| "Should work now" | Run the command. |
| "I'm confident" | Confidence is not evidence. |
| "Just this once" | No exceptions. |
| "Lint passed" | Lint does not compile or test. |
| "The agent said success" | Verify independently via the diff. |
| "Partial check is enough" | Partial proves nothing about the rest. |
| "Different wording, so the rule doesn't apply" | Spirit over letter. |

Red flags in your own output: "should", "probably", "seems to", or any
"Great!/Perfect!/Done!" *before* the evidence is on screen.

> Gate, table and Iron-Law framing adapted from obra/superpowers
> (`verification-before-completion`, MIT). Wired to the container-first
> execution rule below.

## When to Use

Invoke this skill:

- After completing a feature or significant code change
- Before creating a PR
- When you want to ensure quality gates pass
- After refactoring

## Verification Phases

> **Execution rule (NON-NEGOTIABLE):** every check runs through the repo's own
> **`make` targets, in-container** — never bare on the host (containers rule,
> `standards/rules/containers.md`). Discover the real target names from the repo's
> `Makefile` (`make help`) and use those; the commands below are the canonical
> shape, not literal names. A stack with no separate build step folds Phase 1 into
> its framework's own check command.

### Phase 1: Build / Framework Check

```bash
make build 2>&1 | tail -20   # or the framework's own check target
```

If the check fails, STOP and fix before continuing.

### Phase 2: Type Check

```bash
make typecheck 2>&1 | head -30
```

Report all type errors. Fix critical ones before continuing.

### Phase 3: Lint Check

```bash
make lint 2>&1 | head -30
make format-check 2>&1 | head -30
```

### Phase 4: Test Suite

```bash
# Runs the test suite with coverage
make test 2>&1 | tail -50

# Check coverage against the threshold the repo declares
```

Report:

- Total tests: X
- Passed: X
- Failed: X
- Coverage: X%

### Phase 5: Security Scan

```bash
# Check for secrets
grep -rn "sk-" --include="*.ts" --include="*.js" . 2>/dev/null | head -10
grep -rn "api_key" --include="*.ts" --include="*.js" . 2>/dev/null | head -10

# Check for console.log
grep -rn "console.log" --include="*.ts" --include="*.tsx" src/ 2>/dev/null | head -10
```

### Phase 6: Diff Review

```bash
# Show what changed
git diff --stat
git diff HEAD~1 --name-only
```

Review each changed file for:

- Unintended changes
- Missing error handling
- Potential edge cases

## Output Format

After running all phases, produce a verification report:

```
VERIFICATION REPORT
==================

Build:     [PASS/FAIL]
Types:     [PASS/FAIL] (X errors)
Lint:      [PASS/FAIL] (X warnings)
Tests:     [PASS/FAIL] (X/Y passed, Z% coverage)
Security:  [PASS/FAIL] (X issues)
Diff:      [X files changed]

Overall:   [READY/NOT READY] for PR

Issues to Fix:
1. ...
2. ...
```

## Continuous Mode

For long sessions, run verification every 15 minutes or after major changes:

```markdown
Set a mental checkpoint:
- After completing each function
- After finishing a component
- Before moving to next task

Run: /verify
```

## Integration with Hooks

This skill complements PostToolUse hooks but provides deeper verification.
Hooks catch issues immediately; this skill provides comprehensive review.
