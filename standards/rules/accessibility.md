<!-- GENERATED from standards/STANDARDS.chrysa.md by scripts/gen_agent_views.py — do not edit.
Canonical source of truth is the canon; edit there, then run `make gen-agent-views` to regenerate every view.
-->
# Accessibility

> Detail for the slim core in `CLAUDE.md`. **Generated** from `standards/STANDARDS.chrysa.md` — do not edit here; edit the canon and regenerate.

- **Dark mode** mandatory from V1. **Accessibility** WCAG 2.1 AA — Lighthouse a11y score **≥ 90**,
  full keyboard navigation (Tab/Esc/visible focus), contrast ≥ 4.5:1 (3:1 large text), screen-reader
  tested on critical flows (signup, login, checkout).

- **Every site is usable by the majority of disabilities — not only the screen-reader case.**
  WCAG 2.1 AA is the floor; the obligation is that a real person from each major disability
  category can actually complete the product's core tasks. The categories are named and each
  carries a concrete, testable requirement:
  1. **Visual** (blind, low-vision, colour-blind) — screen-reader operable end to end (semantic
     markup + labels + live regions), reflows to 400% zoom and 320 px with no loss of content or
     function, honours `prefers-contrast`, and **never encodes meaning by colour alone** (icon,
     text, or pattern too).
  2. **Motor** (limited dexterity, no pointer, switch/voice control) — fully keyboard-operable
     with a visible focus order and no keyboard trap, touch targets **≥ 44 px**, no action that
     requires a drag, a precise gesture, or a hover-only reveal, and no timeout the user cannot
     extend.
  3. **Auditory** (deaf, hard-of-hearing) — captions on every video, transcript for audio, and
     no information conveyed by sound alone (a visual equivalent for every audio cue).
  4. **Cognitive** (attention, memory, literacy, dyslexia) — plain language, consistent and
     predictable navigation, errors that say what to fix (see *every form is a hostile input
     surface*), no unavoidable time pressure, and progress that survives reload (see *UI state
     survives reload & focus*).
  5. **Vestibular / photosensitivity** — honours `prefers-reduced-motion`, no auto-playing or
     looping motion the user cannot stop, and nothing that flashes more than three times a second.
  A public micro-site or generated page is held to the same bar as the app — accessibility is not
  waived because a surface is small, auto-generated, or "just a showcase". The Definition of Done
  for any human-facing surface includes exercising these five paths, mechanised by the a11y gates
  already required (Lighthouse ≥ 90, axe/keyboard/contrast) plus manual screen-reader and
  keyboard-only passes on the core flow. Detail: annexe `FRONTEND.md`, the `accessibility` skill
  (per-category contract + testable DoD), and the `ui-ux` skill.
