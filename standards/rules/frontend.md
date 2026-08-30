<!-- GENERATED from standards/STANDARDS.chrysa.md by scripts/gen_agent_views.py — do not edit.
Canonical source of truth is the canon; edit there, then run `make gen-agent-views` to regenerate every view.
-->
# Frontend & web semantics

> Detail for the slim core in `CLAUDE.md`. **Generated** from `standards/STANDARDS.chrysa.md` — do not edit here; edit the canon and regenerate.

- **TypeScript is strict by contract.** `strict`, `noUncheckedIndexedAccess`,
  `exactOptionalPropertyTypes`, `noImplicitOverride`, `noImplicitReturns`,
  `useUnknownInCatchVariables`, `isolatedModules` are **all** enabled (plus
  `verbatimModuleSyntax` where the toolchain allows). No implicit `any`; `unknown` at
  boundaries; external data validated at **runtime** even when typed; contract types
  generated from OpenAPI/AsyncAPI, never hand-copied. One committed lockfile, frozen CI
  installs, no `latest` dependency. Detail: annexe `FRONTEND.md` §1.

- **The JS/TS package manager is `pnpm` — `npm` and `yarn` are forbidden.** Every
  Node/TypeScript repo (app, library, workspace, tooling) installs, runs scripts, and
  resolves dependencies with **pnpm**. Concretely: the committed lockfile is
  **`pnpm-lock.yaml`** (a `package-lock.json` or `yarn.lock` in the tree is a defect — delete
  it and regenerate with pnpm), workspaces are pnpm workspaces (`pnpm-workspace.yaml`) under
  Turborepo, CI installs with **`pnpm install --frozen-lockfile`** (never `npm ci`), images
  install with pnpm in the builder stage, and scripts run as `pnpm <script>` / `pnpm dlx`
  (never `npm run` / `npx`). The version is pinned via `packageManager` in `package.json` and
  provisioned by Corepack, so every machine and runner resolves the same pnpm. This makes
  *one committed lockfile* and *no host installs* concrete for the JS side: the lockfile is
  `pnpm-lock.yaml`, `node_modules` stays a pnpm-managed build output (see *dependency
  directories are a build output*), never materialised on the host. The only `npm` left
  anywhere is the registry it talks to; the command is always `pnpm`.

- **React is a presentation layer, not the domain.** `domain/` and `application/` never
  import React; no `fetch`, browser storage, or vendor SDK in `domain/`. Components and hooks
  stay pure, props/state immutable, derived state computed rather than duplicated;
  `useEffect` synchronises with an external system and does not orchestrate business logic;
  `StrictMode` on for new apps. One API client singleton behind a service layer, one cache
  library for all server state, a root error boundary, and an explicit loading/error/empty
  triad per container. Anything outside the first meaningful paint loads lazily (split routes,
  `loading="lazy"` media, on-demand heavy components) behind a **shape-accurate placeholder**
  that reserves the final dimensions — a skeleton, not a spinner, so arrival shifts no layout.
  Detail: annexe `FRONTEND.md` §2–§3, §7.

- **The frontend says when the backend is unreachable or unstable.** Silence is the worst
  failure mode: a spinner that never resolves, a list that stays empty, a form that swallows a
  submit all read as "the app is broken and lying about it". The API client classifies every
  failure into application state — `unreachable`, `unstable`, `degraded`, `unauthorised`
  (a session problem, not an outage), `offline` (the browser's fault, worded as such) — and a
  **persistent, non-blocking banner in the root shell** states it for the whole app, while each
  container still resolves its own error state. The message says what happened and what to do
  (*"Server unreachable — reconnecting in 12 s"*, never a raw status code), keeps a manual
  **Retry** available, **disables destructive or unsaved actions** instead of failing silently
  on submit, and **preserves in-progress form input** for re-submission on recovery. Reconnection
  uses bounded exponential backoff with jitter — an unbounded retry loop against a struggling
  backend is a defect — and success clears the state and refetches. The banner is a live region
  (`role="alert"` / `role="status"`) and its behaviour is tested against a network error and a
  503. A frontend Definition of Done includes its **API-down state**. Detail: annexe
  `FRONTEND.md` FE-050.

- **The frontend is reactive and real-time by default.** A human-facing surface reflects the
  true state of the system as soon as it changes — the user never stares at stale data and never
  reaches for a manual refresh to find out what happened. Server state is owned by the cache layer
  (TanStack Query) and kept fresh: a mutation invalidates or optimistically updates the queries it
  affects, and data that a *different* actor (another user, a job, a device) can change is
  **pushed, not polled** — a live transport (WebSocket / SSE) updates the UI in place, with polling
  as a bounded fallback only where a push channel is genuinely unavailable. The interface reacts
  immediately to input (optimistic UI, debounced derived state, no blocking spinner for a
  sub-second action) and reconciles with the server result, rolling back visibly on failure. Live
  updates propagate across the app's own tabs and on refocus (see *UI state survives reload &
  focus*). Real-time is **layered over a correct offline/degraded state**, not a substitute for it:
  losing the live channel degrades to the last known state with the API-down banner (FE-050), never
  to a frozen or lying screen. A surface that shows data a refresh would change is a defect. Detail:
  annexe `FRONTEND.md` FE-080.

- **UI state survives reload & focus** — human-facing surfaces persist their navigation
  and view state (active tab/section, selected sub-view, active context/filters) so a
  **manual reload keeps the current page** — the user lands exactly where they were, never
  reset to a default. Persist to `localStorage` (or the URL for shareable state), guarded
  by a validator that discards stale/removed values. Interface or state changes must
  **propagate across the app's own tabs/windows and on refocus/reload**: listen to the
  browser `storage` event and re-read on `window` `focus`, so a view opened while hidden
  never shows stale state after the user comes back. A reload that loses the user's place,
  or a change that fails to propagate on focus/reload, is a bug.

- **Everything is semantic — the markup, the data, and the URLs.** A surface must be
  understandable by a machine that never sees the pixels: a screen reader, a crawler, an
  AI agent, another service. Meaning lives in the markup and the address, never only in the
  CSS or the JavaScript.
  1. **Semantic URLs.** Resource-oriented and human-readable: lowercase, hyphenated,
     plural-noun collections, a **noun path with no verb or action**
     (`GET /invoices/42`, never `/getInvoice?id=42`, never `/page?id=7`). The path expresses
     the hierarchy (`/projects/42/settings`), the query expresses filtering/pagination/
     selection — not identity. Opaque ids stay out of the path when a stable readable slug
     exists (`/articles/semantic-urls`, optionally `/articles/42-semantic-urls`). A URL is a
     **permanent contract**: it is not renamed on a redesign, and when it must change the old
     one answers `301`, never `404`. REST shapes follow the `api-design` skill; a navigable
     view is always a real URL (see *URL-addressable frontend navigation*).
  2. **Semantic HTML.** The right element for the meaning — `<nav>`, `<main>`, `<header>`,
     `<article>`, `<section>`, `<button>`, `<a href>`, `<table>`, `<form>`, `<time
     datetime>`, `<label for>` — never a `<div>` wired as a control, never a heading level
     picked for its size. One `<h1>` per page and a heading outline with no skipped level;
     images carry meaningful `alt` (or `alt=""` when purely decorative); every input has a
     programmatic label; language is declared (`<html lang>`). **ARIA only fills gaps native
     semantics cannot express** — a native element always beats `role="button"`.
  3. **Structured, machine-readable data.** Any public or shareable page publishes
     **schema.org JSON-LD** appropriate to its type (`Article`, `Product`, `Organization`,
     `BreadcrumbList`, `SoftwareApplication`…), plus the metadata that makes a link
     self-describing: `<title>`, `meta description`, canonical link, Open Graph/Twitter
     cards, `hreflang` on localised pages, a **favicon + app icons + web app manifest**
     (`theme-color` included), and `sitemap.xml` and `robots.txt`. The structured
     data **describes what is actually on the page** — mismatched markup is a defect, not
     an SEO trick. A tab left with the browser's default globe icon is an unfinished page
     (FE-052).
  4. **Semantic code and data shapes.** Intention-revealing names over comments, typed
     contracts over free-form dicts, ISO-8601 dates and explicit units/currency in payloads,
     stable machine-readable codes on errors (see *typed errors*). A field named `data`,
     `value`, or `flag` is a naming defect.
  Mechanisation: the a11y gates already required (Lighthouse ≥ 90, keyboard, contrast) plus
  an HTML-validity/structured-data check on public pages. A page that reads correctly only
  because of CSS is not accessible, not crawlable, and not agent-readable.

- **URL-addressable frontend navigation — mandatory.** Every navigable view/route/tab/
  detail is a **real, semantic URL** (`/projects/42/settings`, not `/#` or a modal with no
  address). Navigating **must change the URL** via the router (History API `pushState`), so:
  1. the change is **recorded in browser history** — Back/Forward move between views, never
     trap or reload the app;
  2. a link is **right-clickable / middle-clickable / ⌘-clickable → open in a new tab**, which
     means it is a genuine `<a href>` (or the router's `<Link>`), **never** a `<div>`/`<button>`
     with an `onClick` that only mutates state;
  3. the URL is **deep-linkable & shareable** — pasting it in a fresh tab lands on the exact
     same view (route params + query for filters/selection/pagination), reproducible without
     prior in-app state.
  Ephemeral UI (transient toasts, open/closed of a purely local menu) may stay stateless, but
  anything a user would bookmark, share, or reload into is a route. This complements
  *UI state survives reload & focus*: persisted view-state that has an addressable identity
  belongs in the URL, not only `localStorage`.
