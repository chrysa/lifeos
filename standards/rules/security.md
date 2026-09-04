<!-- GENERATED from standards/STANDARDS.chrysa.md by scripts/gen_agent_views.py — do not edit.
Canonical source of truth is the canon; edit there, then run `make gen-agent-views` to regenerate every view.
-->
# Security, identity & sessions

> Detail for the slim core in `CLAUDE.md`. **Generated** from `standards/STANDARDS.chrysa.md` — do not edit here; edit the canon and regenerate.

- **Per-person data implies a user account — no exceptions dressed up as simplicity.** The
  moment a product stores or manipulates anything whose *value depends on who is looking*
  — preferences, saved filters and views, favourites, drafts, history, progress, notes,
  annotations, uploads, notification settings, API keys, per-person results — it has **real
  user accounts** behind the identity hierarchy above. The trigger is the data, not the size
  of the app: a "small internal tool" that remembers your filters is already storing personal
  data for several people.
  1. **Ownership is modelled, not implied.** Every per-person row carries its owner
     (`user_id` foreign key), and every read/write is scoped by it in the repository layer —
     not filtered in the UI, not trusted from a request parameter. An endpoint that returns
     another user's row because the id was guessed is the same defect whether the data is a
     medical record or a colour theme.
  2. **`localStorage` is a cache, never the system of record.** Browser storage holds what
     the user can afford to lose on a new device; anything they would be upset to lose lives
     server-side under their account. A product whose personalisation exists only in one
     browser has no personalisation — it has a cookie.
  3. **A shared password is not an account.** One credential handed to several people makes
     every action unattributable, every revocation a fleet-wide password change, and every
     export meaningless. Same for "profiles" selected from a dropdown with no authentication:
     that is a preference switch pretending to be identity.
  4. **Account plumbing is part of the feature, not a later epic** — sign-up/invite, sign-in,
     password or SSO recovery, session expiry, and **deletion of the account with its data**
     ship together with the first per-person field. Retrofitting ownership onto a table that
     already holds everyone's rows is a migration, an audit, and an apology.
  5. **Anonymous stays anonymous.** A genuinely public, read-only surface (a landing page, a
     public catalogue) needs no account — and therefore must not quietly accumulate
     per-person state either. If a feature needs to remember the visitor, it needs an account;
     "we'll just key it by browser fingerprint" is tracking, not architecture.
  This is the precondition of *portable personalisation data* (strategic pillar 3): an export
  command only means something when the data has an owner. Detail on the identity path itself:
  the rule below.

- **Identity goes through the cluster SSO first.** Every interactive product deployed in the
  cluster integrates the **common cluster SSO** as its primary sign-in. The priority protocol is
  **OpenID Connect over OAuth 2.x** (SAML only where an enterprise context requires it), and the
  connection hierarchy is fixed: **1. cluster SSO → 2. external OAuth provider → 3. local
  account**. A local account is a fallback, never the default; where present it uses a modern
  password hash (argon2/bcrypt) and MFA is enforceable through the SSO. This does **not** break
  *projects talk through versioned contracts only* or *portable data*: identity sits behind an
  adapter, so the product stays independently deployable against an alternative identity provider
  (or a standalone local mode) by configuration, without touching the domain.

- **A session is secured and it expires.** Authenticating is not the end of the security
  story: the *session* is the credential from then on, and a session that never ends is a
  password that can never be changed. Every authenticated product declares, in config, how
  long a session lives — and enforces it **server-side**, because an expiry the client is
  trusted to honour is not an expiry.
  1. **Two bounds, both mandatory.** An **idle timeout** (inactivity, ~15–30 min for admin and
     sensitive surfaces, longer for low-risk ones) *and* an **absolute lifetime** after which
     re-authentication is required whatever the activity (a working day for a normal product,
     shorter for privileged access). Idle alone lets a stolen session live forever under a
     keep-alive; absolute alone leaves an abandoned browser open all afternoon.
  2. **The session token is opaque and server-revocable.** Sign-out, password change, role
     change and account deletion **invalidate the existing sessions immediately** — a
     stateless token that stays valid until its own expiry is a revocation you cannot perform.
     Where JWTs are used, access tokens stay short-lived (minutes) and the long-lived refresh
     token is stored server-side, rotated on use, with **reuse detection** killing the whole
     family.
  3. **Cookies over `localStorage`.** A session cookie is `HttpOnly`, `Secure`, `SameSite=Lax`
     (or `Strict`), host-scoped, with `Path=/` and no broader domain than needed — so a single
     XSS cannot read it. A token in `localStorage` is readable by every script on the page,
     including the one a compromised dependency injected. State-changing requests carry CSRF
     protection.
  4. **The session id is regenerated at every privilege change** — sign-in, elevation, MFA
     completion — which is what closes session fixation. The identifier is generated by a CSPRNG,
     never derived from the user id, an email, or a timestamp.
  5. **Expiry is a first-class experience, not an error.** The app warns before an idle
     timeout, preserves in-progress work, and returns the user to where they were after
     re-authentication (see *UI state survives reload & focus*). A silent redirect to a login
     screen that discards a half-written form is a defect, not a security measure.
  6. **Sessions are observable and revocable by their owner.** An account surface lists the
     active sessions (device, location, last seen) and can end them — including "sign out
     everywhere". Session creation, renewal, expiry and revocation are logged with a
     correlation id, and the log **never** records the token itself.
  Values live in external config (`SESSION_IDLE_TIMEOUT`, `SESSION_ABSOLUTE_LIFETIME`) like
  every other constant — a timeout hardcoded in a middleware is both a *no hardcoded constants*
  violation and a security parameter nobody can tune without a deploy.

- **Every form is a hostile input surface — validate on the server, always.** A form is the
  place where an unknown person hands the product data of their choosing; the browser is their
  machine, so **nothing enforced only in the client is enforced at all**. `required`,
  `maxlength`, `type="email"`, a disabled button, a hidden field, a client-side schema: those
  are ergonomics, and every one of them is re-checked server-side against a typed schema
  (Pydantic on the backend) that is the single authority on what is acceptable.
  1. **Bind to an explicit allowlist of fields.** The handler names the fields it accepts and
     ignores the rest — no mass assignment, no spreading the payload into a model. A user who
     adds `"is_admin": true` to the request body must change nothing.
  2. **State-changing submissions are protected against cross-site forgery** — an anti-CSRF
     token for cookie-based sessions (with `SameSite=Lax|Strict`, `HttpOnly`, `Secure`), or a
     bearer token deliberately sent by the client. A `GET` never changes state, and secrets
     never travel in a URL: query strings land in browser history, logs, and referrers.
  3. **Submission endpoints are rate-limited and bot-resistant** — per-account and per-IP
     limits on anything that sends mail, creates an account, resets a password, or writes to
     the database, with lockout/backoff on repeated authentication failures. Prefer a
     timing-based or honeypot check to a CAPTCHA that punishes the accessible path.
  4. **Errors say what to fix, and nothing about the system.** Field-level messages, all
     failures returned at once rather than one per round trip, and no stack trace, SQL
     fragment, or internal path leaked to the user. Authentication failures stay generic
     ("invalid credentials"), never "unknown email" — enumeration is a data leak.
  5. **Errors are announced, not just coloured.** The invalid field is programmatically
     associated with its message (`aria-describedby`), the error summary receives focus, and
     the failure is conveyed without relying on colour alone — a form that cannot report its
     own errors to a screen reader is broken for the people most likely to be blocked by it.
  6. **The submission is idempotent and the user's work survives failure.** Double submission
     is blocked (idempotency key or POST-redirect-GET), a rejected form re-renders with the
     entered values, and a network failure does not silently discard a long draft.
  7. **What goes in the form is minimised, and what comes out is escaped.** Collect only the
     fields the feature actually needs (GDPR data minimisation), never log a payload with
     credentials or personal data, mark sensitive inputs `autocomplete="off"` only where it
     genuinely helps, and render user-supplied content escaped by default — a stored value is
     an XSS payload until proven otherwise. File fields additionally follow *if a user can
     supply a file, the product accepts an upload* — type, size and content are validated
     server-side there too.

- **Security scanning is a gate, not an afterthought — it runs in pre-commit and in CI.**
  Every repo scans for the two failure modes a human review misses: **leaked secrets** and
  **known-vulnerable code/dependencies**. The scan is wired at both the local boundary
  (pre-commit) and the shared boundary (CI), from the scaffold — never bolted on after an
  incident.
  1. **Secrets never reach a commit.** A secret scanner (gitleaks) runs in pre-commit and in
     CI; a positive is a hard failure, not a warning. `detect-private-key` and the
     `env-file-check` hook stay on. A secret that is already committed is rotated, not
     `.gitignore`d.
  2. **Code is scanned for known weaknesses (SAST).** Python code runs `bandit` (config in
     `pyproject.toml`, tests excluded) in pre-commit and CI; the container/IaC surface runs a
     vulnerability + misconfiguration scan (Trivy filesystem) in CI, and Dockerfiles are
     linted (`hadolint`). High/critical findings fail the build.
  3. **The gate is centralised, not copy-pasted.** The pre-commit hooks come from the
     `project-init` baseline and `chrysa/pre-commit-tools`; the CI jobs are **reusable
     workflows** in `chrysa/github-actions` (`secret-scan.yml`, `sast.yml`) referenced by a
     thin per-repo caller pinned to a tag. A repo does not fork the scan logic — it consumes
     the shared version.
  4. **A container release carries its provenance.** A published image additionally ships an
     SBOM (Syft), a vulnerability scan of the built image (Trivy), and a signature (Cosign) —
     the supply-chain half of *observability & production readiness*.
  5. **A control is never silently disabled.** Skipping or removing a security hook, lowering
     a severity threshold, or `--no-verify` on a security gate is a governed decision recorded
     in `DECISIONS.md`, not a convenience a single commit grants itself. A pre-existing
     unrelated failure is skipped by name (`SKIP=<hook>`), never by turning the gate off.
