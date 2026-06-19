# Skill: UX / UI / Ergonomics

> Full reference: `shared-standards/docs/UX-UI-GUIDELINES.md`. This module is the actionable,
> always-on contract loaded when building or reviewing UI.
> PLACEMENT: copy this file to `shared-standards/.claude/skills/ui-ux/SKILL.md`.

## When to invoke
Auto-invoke when building or reviewing ANY human-facing surface, not only web:
- **Web**: React components/pages, Tailwind/shadcn, forms/tables/overlays, dark mode, i18n.
- **CLI/TUI**: commands, flags, help, output, exit codes.
- **VS Code extension**: commands, webviews, theming, notifications.
- **Discord bot**: slash commands, embeds, interactive components.
- **Desktop/tray**: native apps, system tray, notifications (windows-autonome, floating-agent…).
- **Game UI (2D)**: HUD, menus, input remapping (Discordium…).
- **Agent/conversational**: assistant/agent responses (lifeos, my-assistant, coach…).
- **Alerts/notifications**: briefing/health/state alerts.

Web stack: React 19 + TS + Vite, shadcn/ui + Tailwind, TanStack Query + Zustand, react-i18next.

## Non-negotiable everywhere
- **Feedback + error recovery** — every action confirms success/failure; errors give cause + next step.
- **Reversibility** — destructive actions confirmed/undoable; dry-run where feasible.
- **i18n FR + EN** — no hard-coded user-facing strings (logs stay English).
- **Accessibility-equivalent** — WCAG 2.1 AA on web; closest equivalent per surface (keyboard, SR, contrast, colorblind, NO_COLOR…).
- **Dark mode** (web/desktop) — semantic tokens / OS theme, verified contrast.
- **No noise** — notify only what's actionable; tunable frequency.

## Surface quick rules (see docs/UX-UI-GUIDELINES.md §12)
- **CLI**: `--help` everywhere · stable flags (`--dry-run/--json/--yes/--quiet`) · errors→stderr · exit codes · progress · honor `NO_COLOR`/non-TTY.
- **VS Code**: namespaced palette commands · theme color tokens (no hex) · status bar > notifications · no keybind clashes · webviews = full web baseline.
- **Discord**: slash cmds with descriptions · ephemeral errors · ack <3s (defer) · perms+confirm on admin · label+icon not color · `/help`.
- **Desktop/tray**: OS conventions · persist window state · honor OS theme · tray Quit always present · actionable, rate-limited notifications · platform a11y API.
- **Game 2D**: readable HUD · colorblind-safe · pause/settings reachable · input remapping (kbd+pad) · feedback/juice · first-run onboarding · reduced-motion.
- **Agent**: state capabilities/limits · confirm irreversible/external actions · transparent on uncertainty/failure · concise · FR/EN · respect preferences.
- **Alerts**: signal>noise · explicit severity (label+icon) · self-contained (what/why/action/where) · dismissible/snoozable · digest over spam.

## Core rules

### Tokens — no magic values
```tsx
// ✅ semantic, theme-aware (free dark mode)
<div className="bg-background text-foreground border border-border" />
<Button variant="destructive">Delete</Button>
// ❌ never
<div className="bg-[#0f172a] text-white" style={{ borderColor: "#e2e8f0" }} />
```
- No hard-coded hex / px font sizes / arbitrary spacing. Tailwind 4/8px scale + `--radius` only.
- Color never the sole carrier of meaning (icon + text for status/errors).

### The four states — always all four
Every data view handles loading / empty / error / success. A view that only renders
"success with data" is **incomplete**.
```tsx
if (isPending) return <ListSkeleton rows={6} />;
if (isError)   return <ErrorState onRetry={refetch} message={t("errors.load")} />;
if (!data.length) return <EmptyState action={<CreateButton />} />;
return <List items={data} />;
```
- Skeleton matching final layout (not a bare spinner) for content loads.
- Empty state explains why + offers the primary next action.
- Error state: plain language + Retry. Never a raw stack trace/code.

### Accessibility (WCAG 2.1 AA)
- Contrast ≥ 4.5:1 text, ≥ 3:1 large text & UI components.
- Full keyboard operability, logical tab order, no traps.
- Visible focus everywhere: `focus-visible:ring-2 ring-ring`. Never bare `outline: none`.
- Prefer semantic HTML; ARIA only to fill gaps and kept in sync.
- Every input has a real `<Label htmlFor>`; placeholder ≠ label.
- One `<h1>`/page, ordered headings, landmarks, skip link.
- `aria-live` for toasts/dynamic updates. `<html lang>` follows locale.
- Honor `prefers-reduced-motion`.
- Tooling: `eslint-plugin-jsx-a11y` + automated axe check + **manual keyboard/SR pass (required)**.

### Dark mode
- `.dark` class on `<html>` + semantic tokens. Default to `prefers-color-scheme`,
  user override, persist, no flash-of-wrong-theme. Verify contrast in dark separately.

### i18n (FR + EN)
- All copy via `react-i18next` `t("ns.key")`. No string concatenation; ICU plurals with `{ count }`.
- Layouts tolerate +30–40% FR expansion. Dates/numbers via `Intl.*`. FR/EN catalogs in lockstep.

### Components
- shadcn/ui primitives first — keep their ARIA/focus/keyboard intact when extending.
- One primary action per view (`variant="default"`); `destructive` only for irreversible actions.
- Overlays: trap focus, `Esc` to close, return focus to trigger, accessible name.
- Forms: validate on blur/submit, errors via `aria-describedby` + `aria-invalid`, preserve input.
- Targets ≥ 44px on touch.

### UX copy
- Plain language, active voice, sentence case. Buttons name the action ("Create project", not "OK").
- Errors: what happened + what to do next. For deep copy work, defer to `design:ux-copy`.

## Forbidden patterns
- ❌ Hard-coded colors / px font sizes / arbitrary spacing in components.
- ❌ User-facing string literals in JSX (must go through i18n).
- ❌ `outline: none` without a visible replacement.
- ❌ Placeholder used as the only label.
- ❌ Data view missing empty/error/loading states.
- ❌ Color-only status/error indication.
- ❌ Dark-mode styles assumed correct without contrast verification.
- ❌ Custom widget reimplementing what a shadcn primitive already does accessibly.

## Definition of Done
Loading+empty+error+success · dark verified · keyboard pass · SR smoke test · contrast OK ·
tokens only · FR+EN aligned · responsive 320px→2xl · reduced-motion · jsx-a11y clean ·
one primary action. Full checklist: `docs/UX-UI-GUIDELINES.md` §11.

## Related Cowork skills
`design:design-system` · `design:accessibility-review` · `design:ux-copy` ·
`design:design-critique` · `design:design-handoff`.
