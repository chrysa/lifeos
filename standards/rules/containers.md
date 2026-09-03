<!-- GENERATED from standards/STANDARDS.chrysa.md by scripts/gen_agent_views.py — do not edit.
Canonical source of truth is the canon; edit there, then run `make gen-agent-views` to regenerate every view.
-->
# Containers & compose

> Detail for the slim core in `CLAUDE.md`. **Generated** from `standards/STANDARDS.chrysa.md` — do not edit here; edit the canon and regenerate.

- **Everything runs in a container — the only exception is the slice of a repo genuinely bound to the host OS.** Application code, tooling, dependencies, tests, and the services a project talks to all execute inside images / compose — the container *is* the environment. A repo runs code natively **only** for the part that genuinely requires deep host access (`exempt:native`: desktop apps, OS/hardware agents, editor/IDE extensions, kernel or device work), and **only that part**: its portable pieces (deps, tests, tooling, CI) still containerise. "It is simpler on the host" is not a reason; a real host binding (a syscall, a device, a GUI toolkit, an OS API) is. The three sanctioned host tools (git, Docker, the commit gate) are the only things installed on the machine itself; everything else reaches the developer through `docker compose` / `make docker-*`. A service that could run in a container but does not is drift, not a preference.

- **External dependencies are installed in containers, never on the host.** A project's
  runtime dependencies — language packages (pip/npm/cargo/nuget), databases, brokers, caches,
  system libraries, compilers, CLIs a service shells out to — are declared in the image
  (`Dockerfile`) or in a compose service, and installed **inside the container**. `sudo apt
  install`, `pip install` into the system interpreter, a global `npm -g`, or a locally
  installed Postgres/Redis "to make it work" are **defects**: they make the machine the
  environment, so the build is unreproducible, the version drifts per-machine, and CI and prod
  no longer run what the developer ran. A missing dependency is fixed by editing the image,
  never by installing it on a developer machine. Three sanctioned host tools only, all repo-independent
  and installed **outside** any project tree: **git**, **Docker** itself, and the commit gate
  (`pipx`/`uv install pre-commit`, which provisions its own hook envs — see *the gate is
  host-native*). Everything else runs through `docker compose run` / the `make docker-*`
  targets. Host-bound repos (`exempt:native`: desktop, hardware, editor extensions) are the
  documented exception, and only for the part genuinely bound to the host OS.

- **No virtualenv in a repo — ever.** `venv/`, `.venv/`, `env/` are **forbidden** inside a
  project tree. Python runs in the Docker image (deps baked into the image layer, or a named
  volume for editable installs). A committed or on-disk virtualenv is a bug, not a setup step.
  The only sanctioned local Python is a **uv/pipx tool env stored outside the repo** (e.g.
  `~/.local`, `$UV_CACHE_DIR`), never a folder living next to the source.

- **Tool caches & deps never touch the project tree.** `__pycache__`, `.pytest_cache`,
  `.ruff_cache`, `.mypy_cache`, `.benchmarks`, `node_modules`, and pip/npm/uv download caches
  are regenerable machine artifacts — they must be **invisible in the repo working copy**.
  Enforcement is three-layered and all three are mandatory:
  1. **`.gitignore`** carries the managed canonical block (`templates/gitignore.canonical`) so
     they are never tracked. Appended, not hand-maintained.
  2. **Docker caches live in named volumes**, and every cache-dir env var points **outside**
     the bind mount so nothing is written back into the mounted source:
     ```yaml
     # docker-compose: a container that bind-mounts the repo
     services:
       tests:
         user: "${UID:-1000}:${GID:-1000}"   # host UID — NEVER `user: root`
         environment:
           PYTHONPYCACHEPREFIX: /caches/pycache
           RUFF_CACHE_DIR: /caches/ruff
           MYPY_CACHE_DIR: /caches/mypy
           PYTEST_ADDOPTS: -p no:cacheprovider  # or PYTEST_CACHE_DIR under /caches
           npm_config_cache: /caches/npm
         volumes:
           - .:/code
           - tool-caches:/caches          # named volume, persists across runs
           - node-modules:/code/node_modules   # deps in a volume, shadowing the mount
     volumes:
       tool-caches:
       node-modules:
     ```
  3. **Any container that bind-mounts a repo runs as the host UID** (`user: "${UID}:${GID}"`),
     **never `user: root`** — root-owned artifacts written into a bind mount are unremovable
     without `sudo` and are treated as a defect. Root user is allowed only for containers with
     **no** repo bind mount (e.g. `.:/code` absent).
  4. **Dependency directories are a build output, never a source artifact.** `node_modules` and
     its per-ecosystem equivalents — `vendor/` (Go/PHP), `target/` (Rust/Maven), `.gradle/`,
     `Pods/` (CocoaPods), `bin/`+`obj/` (.NET), and `.venv`/`site-packages` (already forbidden in
     the tree by *no virtualenv in a repo*) — are **generated at build time**, either baked into
     the image layer (`RUN npm ci` / `pip install` / `cargo build` in the `builder` stage) or
     mounted from a **named volume that shadows the bind mount** (`node-modules:/code/node_modules`
     above). They are **never materialised in the working copy on the host**: a `node_modules/`
     (or equivalent) sitting in the project tree is a defect — machine-specific, unreproducible,
     and it shadows the container's own install. The **lockfile is committed; the resolved tree is
     not**, and a fresh clone reaches a green `make ci` without ever running an install on the
     host (see *external dependencies are installed in containers*).
  Regenerable artifacts already in a repo are purged with `scripts/purge-artifacts.sh`.

- **Dockerfiles are multi-stage, with a `production` and a `dev` stage — mandatory.** Every
  application Dockerfile uses named build stages so a single file yields both runtime and
  developer images (`docker build --target production` / `--target dev`). Minimum stages:
  a shared `base` (interpreter + OS deps), a `builder`/`deps` (compiles/installs dependencies),
  a **`production`** target (slim runtime — no dev tooling, non-root `USER`, only the built
  artifact), and a **`dev`** target (production + test/lint/debug tooling, editable install,
  live-reload). A single-stage Dockerfile, or one missing either `production` or `dev`, is a
  defect. Compose services select the target explicitly (`build.target: production|dev|tests`).
  Canonical shape + Python 3.14 example: the `dockerfile-multistage` skill.
  *Exemption — container-collection repos:* a repo whose product **is** a set of standalone
  utility/tool container images (e.g. `usefull-containers`), not one application, is exempt from the
  `production`+`dev` two-stage rule per image — each image is single-purpose. Such images still must
  not embed a reverse proxy and still run as non-root where they bind-mount host paths.

- **App containers ship the app only — the platform layer is the owner's responsibility.** An
  application image/container **never embeds a reverse proxy** (any TLS-terminating or routing
  front). The app container exposes its own port and speaks plain HTTP;
  routing, TLS, virtual hosts, and load-balancing live in the **platform layer** (the owner's
  reverse proxy with automated TLS/ACME certificate management on the host, or `deploy/k8s/`
  ingress), out of the app image. A static
  frontend may use a minimal internal web server to serve its own built assets, but it does **not**
  proxy other services. Baking a reverse proxy into an app container is a defect (couples the app to
  infra, duplicates the platform, and breaks the ownership boundary).

- **Only a publicly useful port is published — everything else stays on the container network.**
  A `ports:` entry exists **only** for what a human or an external system outside the stack
  genuinely consumes: in practice the product's public entry point, and nothing else. Databases,
  caches, brokers and their management UIs, search engines, object storage, internal APIs,
  metrics/`/debug` endpoints and dev tooling communicate **by service name over the container
  network** (`expose:`, or nothing at all — service DNS is enough); publishing one is a defect.
  This is not hygiene, it is exposure: on a Docker host a published port is inserted into
  `nftables`/`iptables` **ahead of** `ufw`/`firewalld`, so `ports: "5432:5432"` puts the database
  on the public internet even when the host firewall denies everything. When a host-side tool
  genuinely needs access, bind the loopback explicitly (`127.0.0.1:5432:5432`) in a local
  override — never in the committed base stack. In Kubernetes the same rule reads: every
  `Service` is `ClusterIP` except the ingress-fronted entry point; `NodePort`, `LoadBalancer`,
  `hostPort` and `hostNetwork` need an ADR (a `hostPort` also bypasses `NetworkPolicy`).
  Detail: annexe `CONTAINERS-K3S.md` CT-015.

- **A compose file is minimal — declare only what the stack needs, default the rest.** A
  `docker-compose*.yml` is a description of *this* stack, not a copy of Compose's defaults. It
  declares the services, their `build.target`/`image`, `depends_on`, `environment`, volumes,
  `healthcheck` and `restart` — and **nothing Compose already does for you**. Forbidden as
  noise: an explicit `networks:` block re-declaring the default bridge and wiring every service
  to it (Compose already puts all services on a shared default network with service-name DNS —
  see the ports rule), a redundant `container_name`, a `version:` top-level key (obsolete in
  Compose v2), commented-out dead services, copy-pasted blocks that a YAML anchor or an
  `extends`/override file would fold, and env values inlined where an `.env` / `env_file`
  belongs. Environment- or developer-specific settings (a loopback port bind, a source bind
  mount for hot-reload, debug flags) live in `docker-compose.override.yml` or a `*.dev.yml`,
  never in the committed base stack. The test is mechanical: every line in the base compose
  file is one a reader could not have inferred from Compose's defaults — a line that only
  restates a default is deleted. Detail: annexe `CONTAINERS-K3S.md` CT-019.

- **Dev stage must hot-reload.** The `dev` target/service provides live auto-reload so a source edit
  is reflected without a manual rebuild/restart: the backend's autoreload runner and the
  frontend's dev server with HMR, watched via the compose
  `develop.watch` sync or a source bind mount. A `dev` image identical to `production` (no reload) is
  not a dev image. Mechanised by the `compose-dev-hot-reload` hook
  (`chrysa/pre-commit-tools`): a compose service targeting the `dev` stage with neither a bind
  mount nor a `develop.watch` sync action is flagged at commit time.

- **Local dev runs the code in-container, live, in debug mode — never the production server.**
  The local development loop is edit-on-host, run-in-container, and the three properties below
  are non-negotiable because together they make "it ran on my machine" mean "it ran the way the
  container runs it":
  1. **Sources are synchronised host ↔ container.** The code the developer edits on the host is
     the code executing in the running `dev` container, with **no rebuild step** between save and
     effect — via a source **bind mount** (`.:/app`) or Compose `develop.watch` **sync** (not
     `sync+restart` for interpreted code, which defeats the point). A dev workflow that requires
     `docker build` after every edit is a defect: it is not a dev loop, it is a slow CI loop.
  2. **The dev process is the framework's dev server with autoreload, not a production server.**
     The `dev` stage launches the app through its **autoreloading dev runner** — the framework's own
     reload-enabled dev server (backend hot-reload, frontend dev server with HMR) — so a
     source change reloads the process automatically. A **production WSGI/ASGI/static server —
     a multi-worker application server, a static or reverse-proxy server fronting built assets, an
     application server **without** autoreload, a compiled release binary — is forbidden in the `dev`
     stage**: those exist for the
     `production` target (multi-worker, no reload, no debugger), where reloading on every edit and
     exposing a debugger would be exactly wrong. The `dev` and `production` stages differ **here**,
     not only in installed tooling.
  3. **Debug mode is on in dev.** The dev process runs with the framework's debug switch enabled
     (`DEBUG=1`, `--debug`, `--reload`, `NODE_ENV=development`) — verbose errors, the interactive
     debugger/PDB attach, and autoreload — and that switch is **off in production by contract**
     (`DEBUG` false, no debugger, no stack traces to the client; a debug-on production build is a
     security defect, see *every form is a hostile input surface* and the session rules). Debug is
     a **per-environment flag read from config** (*no hardcoded constants*), never a literal baked
     into an image that ships to prod.
  In short: same sources, live, debug-on, dev runner in `dev`; a frozen copy, no reload, debug-off,
  production runner in `production`. A `dev` service that runs `gunicorn`/`serve`, needs a rebuild
  to see a change, or ships with debug off is not a dev environment. Extends *Dev stage must
  hot-reload* and is checked by the same `compose-dev-hot-reload` hook plus review.

- **Default to dev mode when starting an app locally — any other mode only when explicitly asked.** Running an app on the developer machine (yourself, an agent, a `make` target, a README's first step) starts it in the framework's **development mode** by default: the dev server, autoreload on, debug on, the dev-stage container (`target: dev`). A production/staging/prod-like local run happens **only when a mode is explicitly requested** — reproducing a prod-only bug, a perf measurement, a release smoke-test — and is stated as such. Absent an explicit mode, dev is the default; never launch the production server locally to "just run it". This is the local-run counterpart of *local dev runs the code in-container, live, in debug mode* — that rule governs *how* the dev process runs, this one fixes *which* mode is chosen by default.

- **`.dockerignore` mandatory & exhaustive** — at minimum `.git`, `node_modules`, `__pycache__`,
  `.env*`, `*.log`. Base images pin an explicit version or digest (never a bare `FROM …:latest`);
  no secret in build args or image layers (BuildKit secrets or runtime env only). Every application
  Dockerfile declares a `HEALTHCHECK`, and compose services set `restart: unless-stopped`.

## Container-runtime policy

A project runs **only in a container** unless its nature genuinely forbids it. Convenience, "easier
on the host", or "it's just a script" are **not** exemptions — when in doubt, classify `container`.
Every repo carries a `runtime:` field in `repos.yml`, machine-checked by `audit-docker-compliance.sh`:

- `container` — runs as a service. Provides Dockerfile(s) + `docker-compose*` + `HEALTHCHECK` +
  `docker-up`/`docker-down`/`docker-test` targets.
- `exempt:lib` — distributed/imported (library, plugin, pre-commit hook, GitHub Action, CLI). Runs
  in the consumer's environment; provides a `docker-test` target (CI runs the suite in a container).
- `exempt:config` — no executable runtime (config, knowledge base, deploy manifests). Nothing to run.
- `exempt:native` — bound to a host OS, device, cloud platform, or editor (desktop integration,
  hardware, Apps Script, VS Code extension, infra/Helm). Optional `Dockerfile.test` for CI.
- `pending` — pre-code scaffold; flips to `container` at first code.
