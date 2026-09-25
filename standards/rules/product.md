<!-- GENERATED from standards/STANDARDS.chrysa.md by scripts/gen_agent_views.py — do not edit.
Canonical source of truth is the canon; edit there, then run `make gen-agent-views` to regenerate every view.
-->
# Product surfaces

> Detail for the slim core in `CLAUDE.md`. **Generated** from `standards/STANDARDS.chrysa.md` — do not edit here; edit the canon and regenerate.

- **A public web surface is legally compliant, consent-respecting, and operable — before it
  ships.** Any surface a stranger can reach on the open web (a product front, a landing page,
  a generated micro-site) is held to a Definition of Done that goes past "it renders". The
  obligations below are non-negotiable for a public surface and marked **N/A** only for a
  surface with no public reach (an internal backoffice behind SSO, a CLI, a headless service);
  the a11y, semantic-markup, form-validation, and GDPR rules already in this canon are
  assumed and not repeated here.
  1. **The legal pages exist and are reachable from every page.** A **privacy policy**, a
     **legal notice** (mentions légales — publisher identity, host, contact), and **terms of
     use** (CGU) are published as real, addressable pages and linked from a persistent footer
     on every public page. They are not lorem-ipsum: they state what the product actually
     does with data. Sourced from the shared `legal/` templates (`mentions-legales.md`,
     `cgu.md`) and the `cgu` / `rgpd-compliance` skills, adapted per product — never invented
     ad hoc, never omitted "for now".
  2. **Cookies and trackers are opt-in, not opt-out.** No non-essential cookie, analytics
     tag, or third-party tracker fires before the user has actively consented; a consent
     banner offers *reject* as prominently as *accept*, records the choice, and the choice is
     revocable. Strictly necessary cookies (the session cookie of *cookies over localStorage*)
     need no consent and are the only ones allowed pre-consent. A pre-ticked box or a
     cookie-wall that only offers "accept" is a defect.
  3. **Applicable local law is checked, not assumed.** The jurisdictions the product serves
     are named, and the obligations they add on top of GDPR/RGPD (consent specifics, age
     gating, sector rules, accessibility law such as the EAA, mandatory notices) are recorded
     in the product's compliance notes before launch. "It works in France" is not a
     substitute for knowing where the users are. Detail: annexe `GOVERNANCE.md`, the
     `rgpd-compliance` and `legal-compliance` skills.
  4. **HTTPS is forced end to end.** Every public surface is served over TLS only: plain
     `http://` **301-redirects** to `https://`, `HSTS` is sent (`Strict-Transport-Security`,
     with a sane `max-age` and, once stable, preload), and no mixed content is loaded. TLS is
     terminated in the platform layer (*the application image never embeds a reverse proxy*);
     the product's obligation is that no reachable route answers in clear text.
  5. **Error states are custom pages that let the user report the bug.** The `404` and `5xx`
     responses render a branded, on-brand page (not the server default, not a stack trace —
     see *errors say what to fix, and nothing about the system*) that keeps the user oriented
     (a way back home, working navigation) and offers a **one-click way to report the
     problem**. The report reaches the team as a GitHub issue via the same path as
     *error-tracking → GitHub issues*, carrying enough context (route, correlation id) to be
     actionable; the user tracks it through product-level statuses only, never the Git thread
     (*bug remontée* obligation). This is the human-facing complement of the automatic
     error-tracking norm.
  6. **No broken links, internal or outbound.** A link that `404`s (or a stale outbound URL)
     is a defect caught before merge: a link-check runs in CI over the built surface, and an
     internal path that must change follows *a URL is a permanent contract* (`301`, never a
     dead end). Renaming a route without a redirect is a broken link by another name.
  7. **Pages are fast, and images earn their bytes.** The frontend meets the declared
     **performance budget** (*performance and cost budgets are declared per profile and
     enforced*): Core Web Vitals in the "good" range and a Lighthouse performance score at the
     per-profile threshold, measured in CI on the built artefact. Images are **compressed and
     served in a modern format** (AVIF/WebP with fallback), sized to their display box,
     lazy-loaded below the fold, and never shipped as a multi-megabyte original — an
     uncompressed hero image is a budget breach, not a detail.
  Mechanisation: a public-surface DoD checklist plus CI gates — TLS/HSTS and header check,
  link-checker, Lighthouse performance + a11y, image-weight budget, and a presence check for
  the legal-page routes and the consent banner. A public surface that ships missing any of
  these is a defect, not a fast follow.

- **Setup wizard & config panel** (deployable web apps/services — not libs, CLIs, utilities). A
  first-run **setup wizard** (CLI or web) covers DB, admin user, integrations, secrets and locale;
  it is **idempotent**, detects missing prerequisites with explicit fixes, and offers a CI skip
  (`SETUP_NON_INTERACTIVE=1`). On missing/invalid config at startup or runtime, the app **redirects
  to `/setup`** rather than crashing or showing a generic error. An admin **configuration panel**
  (auth-gated CRUD API) manages runtime config with a versioned audit trail, hot-reload where
  possible (else a `RESTART_REQUIRED` flag), and JSON export/import for backup and cross-env cloning.

- **A game is DRM-free and fully playable solo offline.** The single-player experience is
  complete **without a network, an account, or a licence check** — unplug the machine and the
  game still starts, saves, loads, and can be finished. **No DRM of any kind**: no licence
  server, no phone-home activation, no online entitlement check, no always-on requirement, no
  third-party wrapper gating launch. A copy someone owns keeps working when the servers are
  gone, the company is gone, or the network is down; a build that will not start offline is a
  defect, not an anti-piracy measure. Saves are **local, open and portable** (JSON/SQLite in
  the platform's user directory, copyable, not encrypted against their owner) — the
  *portable personalisation data* pillar applied to a save file. Online features (multiplayer,
  leaderboards, cloud sync, telemetry, stores) are **additive layers over a complete offline
  game**: losing one degrades a feature, never the ability to play. The offline path is
  **tested with the network disabled**, on a machine that never signed in — an offline mode
  nobody exercises is one that has already stopped working. Detail: annexe
  `ARCHITECTURE-DDD.md` AR-045.

- **Every product that is operated ships a management backoffice.** As soon as a product has
  users, content, or work that someone has to *run* — accounts to unlock, an import that
  failed, a job stuck in a queue, a flag to flip — it ships an authenticated **admin
  backoffice** covering that work. The test is blunt: **if operating the product in practice
  means SSH, `psql`, or a hand-written script, the backoffice is missing** — and the day a
  real incident lands, the operator improvises a `UPDATE` on production at 23:00.
  1. **It covers the operations the product actually needs**, not a generic table browser:
     accounts (invite, roles, deactivate, delete with their data), the domain entities support
     is asked about, moderation/quarantine where content is user-supplied, runtime config and
     feature flags (see *setup wizard & config panel*), background jobs and queues with a
     **retry** and a visible failure reason, and the deployed versions of the running pieces.
  2. **Admin power is a role, not a person.** Access is gated by an explicit permission set
     behind the identity hierarchy — never a shared login, never "the first account created",
     never an environment variable holding a master password. Sensitive operations
     (impersonation, export, deletion) are separately granted, and impersonation is announced
     in the UI and terminated by an explicit exit.
  3. **Every admin action is audited** — who, what, when, on which record, with the before and
     after. The audit trail is written by the same path that performs the action, not
     reconstructed from logs, and it is readable *in* the backoffice: an admin surface that
     cannot answer "who changed this and when" is where accountability quietly ends.
  4. **Destructive actions are confirmed, scoped and reversible** — a typed confirmation for
     the irreversible ones, soft delete or quarantine over hard delete, bulk operations bounded
     and previewed before they run. "Delete all" without a preview is an incident generator.
  5. **It shows the least data that answers the question.** A support view surfaces what the
     operator needs and masks the rest; secrets and credentials are never displayed, only
     rotated. Reading a person's data through the backoffice is itself an audited act.
  6. **It is a product surface, held to the product's standards** — same design system, dark
     mode, WCAG 2.1 AA, semantic URLs, i18n, tests and error handling. An admin panel treated
     as a throwaway becomes the least reliable part of the system, operated under stress, by
     the people with the most destructive permissions.

- **If a user can supply a file, the product accepts an upload.** Wherever the workflow
  involves a file the user already has — an import (CSV, JSON, GPX, ICS…), an avatar or image,
  an attachment or supporting document, a configuration or dataset, a log or a crash dump sent
  for support — the surface ships a **real upload path**. Telling the user to paste the
  contents into a textarea, to drop the file on the server themselves, to send it by mail, or
  to re-type what they already hold is a defect, not a simplification: it moves work onto the
  person who has the least tooling for it.
  1. **A real control, not a styled `<div>`** — a native `<input type="file">` with a
     programmatic label (accept multiple only when the flow does), reachable and operable by
     keyboard, plus drag-and-drop as an *addition* for pointer users, never as the only way in.
     Accepted formats and the size limit are stated **before** the user picks, not discovered
     through a rejection.
  2. **Feedback while it travels** — visible progress, a cancel, and a result state per file
     (accepted / rejected with the reason / retryable). Anything that can take more than a
     couple of seconds is resumable or chunked, and a failed upload never silently loses the
     user's selection.
  3. **The server trusts nothing the client says.** Type is determined by inspecting the
     content, not the extension nor the client-provided MIME; size is capped server-side;
     the filename is sanitised and never used as a filesystem path; archives are bounded
     (decompression limits). Rejections come back as typed errors with a message that says
     what to do.
  4. **Stored behind a port, not in the tree** — files go to an object store or a dedicated
     volume through a `BlobStore`-style adapter (strategic pillar 5), never into the repo,
     the web root, or a path the user can traverse. Content is served through the
     application's authorisation, or by a signed, expiring URL — never by guessable path.
  5. **What comes in must be able to come out.** Every uploaded file is listable, replaceable,
     downloadable and deletable by the user who owns it, and is included in the data export
     (strategic pillar 3). An upload with no delete and no export is lock-in with a progress bar.

- **A floating assistant where it earns its place — never as decoration.** Any human-facing
  product whose users face a **non-obvious surface** (a dense cockpit, a multi-step form or
  wizard, a query/graph/config console, an admin panel with domain jargon) ships an **in-app
  floating assistant**: a persistent, dismissible affordance that answers "what am I looking
  at / what do I do next" **in context**, without leaving the page. The value test comes
  first — a product with two screens and no jargon does not get one, and shipping an empty
  chat bubble is worse than shipping nothing. Where it is warranted, it obeys the same rules
  as the rest of the app:
  1. **Context-aware, not a generic chat box** — it receives the current route, selection and
     visible state, and its opening move is a useful suggestion about *this* screen.
  2. **Opt-in and reversible** — off by default behind a documented flag/config key
     (`ASSISTANT_ENABLED`-style), dismissible, and its position/open state persists per user
     (see *UI state survives reload & focus*). It never steals focus, never blocks the
     underlying surface, and never auto-opens on every visit.
  3. **Governed like any agent** — read-only Q&A is R0/R1; the moment it *acts* (writes, calls,
     runs, changes state) the full agentic envelope applies: versioned manifest, typed I/O,
     least privilege, risk level with proportionate confirmation and dry-run, audit trail.
     Detail: annexe `AGENTIC-CAPABILITIES.md`.
  4. **Provider-independent** — inference goes through the local port with ≥2 tested adapters
     (strategic pillar 1); no vendor SDK in the product's business code, and the assistant
     degrades to a documented help panel when no model is reachable.
  5. **Accessible and quiet** — reachable and closable by keyboard (visible focus, `Esc`
     closes), announced to assistive tech, honours `prefers-reduced-motion`, and respects the
     WCAG 2.1 AA + design-token rules like every other surface. It is lazily loaded behind a
     shape-accurate placeholder so it never delays first paint.
  6. **Scoped and honest** — it answers from the product's own data and docs, says "I don't
     know" rather than inventing, and states what it did after acting.
  A desktop/overlay assistant (the `floating-agent` pattern) follows the same rules outside the
  browser: overlay-only, dismissible, no capture of surfaces the user did not consent to.
