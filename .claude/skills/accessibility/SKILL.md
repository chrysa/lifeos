---
name: accessibility
description: 'Use when building, reviewing, or signing off ANY human-facing surface — web app, public micro-site, generated/showcase page, admin backoffice, desktop, game 2D — to make it usable by the majority of disabilities, not only the screen-reader case. Operationalises the STANDARDS.chrysa "Every site is usable by the majority of disabilities" rule into a per-category contract and a testable Definition of Done. Load it alongside ui-ux whenever accessibility is a Definition-of-Done concern, and always before declaring an a11y-bearing surface finished.'
---

# Accessibility — usable by the majority of disabilities

> Mechanises the STANDARDS.chrysa rule *"Every site is usable by the majority of
> disabilities — not only the screen-reader case."* WCAG 2.1 AA is the **floor**; the
> obligation is that a real person from each major disability category can **complete the
> product's core tasks**. This skill is the actionable per-category contract + the DoD.
> Style/token/keyboard mechanics live in `ui-ux` (do not duplicate them here) — this skill
> is the disability-coverage layer on top.
> PLACEMENT: `shared-standards/.claude/skills/accessibility/SKILL.md`.

## When to invoke
- Building or reviewing any human-facing surface (web, micro-site, showcase/generated page,
  admin, desktop, game 2D, conversational).
- Writing the Definition of Done for an a11y-bearing feature.
- Reviewing a diff/PR that touches markup, forms, media, motion, colour, or navigation.
- **No waiver by size**: a public micro-site or auto-generated page is held to the same bar
  as the app — accessibility is not skipped because a surface is small or "just a showcase".

## The five categories — each carries a testable requirement

### 1. Visual (blind · low-vision · colour-blind)
- Screen-reader operable **end to end**: semantic markup, real labels, live regions.
- Reflows to **400% zoom** and **320 px** with no loss of content or function.
- Honours `prefers-contrast`; verified contrast (≥ 4.5:1 text, ≥ 3:1 large text / UI).
- **Never encodes meaning by colour alone** — icon, text, or pattern too.

### 2. Motor (limited dexterity · no pointer · switch/voice control)
- Fully **keyboard-operable**, visible focus order, **no keyboard trap**.
- Touch targets **≥ 44 px**.
- **No drag-only, no precise-gesture-only, no hover-only reveal** — every such action has a
  click/tap/keyboard equivalent.
- **No timeout the user cannot extend** (or disable / be warned about).

### 3. Auditory (deaf · hard-of-hearing)
- **Captions** on every video, **transcript** for audio-only content.
- **No information conveyed by sound alone** — a visual equivalent for every audio cue.

### 4. Cognitive (attention · memory · literacy · dyslexia)
- **Plain language**; consistent, predictable navigation across the surface.
- Errors say **what to fix** (see the *hostile input surface* form rule).
- **No unavoidable time pressure**.
- Progress **survives reload** (see *UI state survives reload & focus*).

### 5. Vestibular / photosensitivity
- Honours `prefers-reduced-motion`.
- **No auto-playing / looping motion the user cannot stop**.
- **Nothing flashes more than three times per second.**

## Review procedure (run all five paths on the core flow)
1. **Automated** — Lighthouse a11y **≥ 90**, `eslint-plugin-jsx-a11y` clean, axe clean.
2. **Keyboard-only pass** — complete the core task with no pointer; focus always visible,
   order logical, `Esc` closes overlays, focus returns to trigger.
3. **Screen-reader smoke test** — VoiceOver/NVDA reads the core flow; names, roles, live
   regions announced.
4. **Zoom / reflow** — 400% and 320 px, no horizontal scroll trap, nothing clipped.
5. **Media** — every video captioned, every audio transcribed, no sound-only signal.
6. **Motion** — toggle `prefers-reduced-motion`; confirm motion stops and nothing flashes.
7. **Colour** — desaturate; every status/error still distinguishable without colour.

## Definition of Done (a11y layer)
Five category paths exercised on the core flow · Lighthouse ≥ 90 · axe + jsx-a11y clean ·
keyboard-only pass · SR smoke test · 400%/320px reflow OK · captions+transcripts present ·
reduced-motion honoured · no >3/s flash · no colour-only meaning · micro-site/generated page
held to the same bar. On any gap: fix, do not waive.

## Forbidden (rejected in review)
- ❌ "It passes axe, ship it" — automated tools catch ~30%; the manual passes are mandatory.
- ❌ Video/audio without captions/transcript.
- ❌ Drag-only, hover-only, or gesture-only actions with no equivalent.
- ❌ Auto-playing motion with no stop; content flashing > 3×/s.
- ❌ Meaning carried by colour alone.
- ❌ A non-extendable timeout on a task path.
- ❌ Accessibility skipped on a public micro-site or generated page.

## Deep audits
For a full audit beyond this DoD, dispatch the `Accessibility Auditor` agent (or
`Section 508 Accessibility Specialist` for US-federal 508/VPAT work). This skill is the
always-on contract; those agents are the deep-audit escalation.

## Related
`ui-ux` (style/token/keyboard mechanics) · `design:accessibility-review` · STANDARDS.chrysa
*Accessibility* + *Every site is usable by the majority of disabilities* + annexe `FRONTEND.md`.
