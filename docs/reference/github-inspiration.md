# Deep-dive — `chrysa/my-assistant` (package `lifeos`)

**What it is (1 phrase):** Early scaffold of a cross-platform (Linux/Windows) floating AI-assistant
desktop app — today a headless Click CLI core (Pydantic-TOML config + plugin enable flags +
Sentry init); the PySide6 overlay, system-monitoring, messaging/AI/service plugins are all
declared but not yet implemented.

**Stack:** Python 3.14, Pydantic v2 / pydantic-settings, httpx (async), psutil, rich, click,
python-dotenv, sentry-sdk. Optional extras: PySide6 (`[ui]`), discord.py (`[discord]`). MIT license,
hatchling build. Ruff + mypy strict.

**Relevance note:** this is an application scaffold, not a novel library. The valuable references
are all mature OSS that already solved the exact subsystems this repo has only stubbed: a plugin
registry with enable/disable, multi-provider AI routing, and a frameless always-on-top overlay.
All four sources below are **MIT (permissive, copyable)** — no copyleft in the shortlist.

---

## szczyglis-dev/py-gpt

- **owner/repo:** szczyglis-dev/py-gpt
- **stars:** ~1.9k
- **activity:** actively maintained (commits through 2026-08)
- **licence:** MIT (verified from LICENSE) — **permissive, copiable**
- **language:** Python (PySide6)
- **why:** it is the closest working equivalent to lifeos' end goal — a multi-OS PySide6 desktop
  AI assistant with a plugin menu (enable/disable per plugin) and multi-provider model routing.

**Pattern / mechanism (plugin registry + provider routing):**
- Plugins inherit a base class and self-register in a plugin manager; each exposes commands that
  become available to the model only when the plugin is toggled on in the `Plugins` menu — exactly
  the `enabled` flag model lifeos already has in `config/settings.py`.
- Provider routing: native SDKs (OpenAI, Anthropic, Google, xAI) handle their own models; anything
  else falls back to an OpenAI-compatible endpoint or LlamaIndex. The app *auto-switches* to the
  compatible endpoint for non-native models — a clean strategy for lifeos' planned
  `core/assistant.py` "route prompt to best available provider".

**Portable snippet (base-plugin shape lifeos should mirror in `plugins/base.py`):**
```python
class BasePlugin(ABC):
    id: str = ""
    def __init__(self) -> None:
        self.enabled = False
    @abstractmethod
    def setup(self) -> None: ...        # never raise: wrap in try/except at registry level
    def teardown(self) -> None: ...
    def get_status(self) -> dict: return {"id": self.id, "enabled": self.enabled}
```

**Integration steps:**
1. Read py-gpt's `plugin/` base + a couple of concrete plugins for the command-registration shape.
2. Mirror the "config flag gates registration" flow lifeos already started (discord/github/notion).
3. Adopt the native-SDK-first / OpenAI-compatible-fallback routing for `core/assistant.py`.

**Gotchas:** py-gpt is a large monolith with LlamaIndex coupling — study the *shape*, don't vendor it.
Its overlay/UX assumptions are GPT-centric; keep lifeos' plugin ABC provider-agnostic (aligns with
the workspace "multi-model / local-first" standard).

---

## pytest-dev/pluggy

- **owner/repo:** pytest-dev/pluggy
- **stars:** ~1.7k
- **activity:** actively maintained (1000+ commits, powers pytest/tox/devpi)
- **licence:** MIT — **permissive, copiable**
- **language:** Python
- **why:** production-grade hook-based plugin system. lifeos currently has only `enabled` flags and
  no registration/dispatch mechanism; pluggy is the battle-tested way to add one without a bespoke
  event bus.

**Mechanism:** hook *specs* (interface) declared with `HookspecMarker`; plugin *impls* with
`HookimplMarker`; a `PluginManager` discovers, registers, and fans-out calls. Supports setuptools
entry-point auto-discovery — ideal for lifeos' optional-extra plugins (discord/ui only load if
installed).

**Portable snippet:**
```python
import pluggy
hookspec = pluggy.HookspecMarker("lifeos")
hookimpl = pluggy.HookimplMarker("lifeos")

class LifeosSpec:
    @hookspec
    def on_system_stats(self, stats): ...     # emitted by system monitor
    @hookspec
    def handle_prompt(self, prompt): ...

pm = pluggy.PluginManager("lifeos")
pm.add_hookspecs(LifeosSpec)
pm.load_setuptools_entrypoints("lifeos")      # auto-load installed plugins
results = pm.hook.handle_prompt(prompt="hi")  # every enabled plugin responds
```

**Integration steps:**
1. Add `pluggy` dependency; define a `hookspecs.py` alongside `plugins/base.py`.
2. Replace the ad-hoc enable flags with `pm.register()` gated on the config `enabled` flag.
3. Expose plugins as `[project.entry-points."lifeos"]` so extras self-register.

**Gotchas:** pluggy is call-fan-out, not async-native — wrap async plugin work yourself
(lifeos plugins are `httpx.AsyncClient`-based). Hook ordering needs `tryfirst`/`trylast`; don't rely
on registration order.

---

## BerriAI/litellm

- **owner/repo:** BerriAI/litellm
- **stars:** ~53k
- **activity:** very active
- **licence:** MIT (core SDK) — **permissive, copiable** (note: enterprise/proxy admin features
  carry a separate commercial license; the Python SDK `litellm.completion`/`Router` is MIT — verify
  the specific module before vendoring)
- **language:** Python (Rust core in newer builds)
- **why:** lifeos plans `plugins/ai/openai.py` + `plugins/ai/opencode.py` and a router in
  `core/assistant.py`. litellm already provides the unified OpenAI-format interface + Router with
  fallbacks/retry/load-balancing across 100+ providers — no need to hand-roll per-provider clients.

**Mechanism:** one `completion()` call normalizes any provider to the OpenAI schema; `Router`
adds model-list-based fallback and retry.
```python
from litellm import Router
router = Router(model_list=[
    {"model_name": "assistant",
     "litellm_params": {"model": "ollama/llama3.1"}},        # local-first default
    {"model_name": "assistant",
     "litellm_params": {"model": "openai/gpt-4o", "api_key": "${OPENAI_API_KEY}"}},
])
resp = router.completion(model="assistant",
                         messages=[{"role": "user", "content": prompt}])
```

**Integration steps:**
1. Make `core/assistant.py`'s provider abstraction a thin wrapper over `litellm.Router`.
2. Put local (Ollama/opencode) first in the model_list to honour the offline-first standard;
   API providers as fallback.
3. Keep the config-driven model list in TOML (matches lifeos' "no hardcoded values" constraint).

**Gotchas:** litellm is a heavy dependency (many transitive deps) — weigh against lifeos' current
lean footprint; you may only want the SDK, not the proxy. Enterprise-gated features are NOT MIT —
stick to `completion`/`Router`. Streaming semantics differ per provider; test streaming for the
overlay chat widget.

---

## bozdemir/claude-usage-widget

- **owner/repo:** bozdemir/claude-usage-widget
- **stars:** ~36 (small but directly on-point for the overlay mechanics)
- **activity:** active (recent commits)
- **licence:** MIT — **permissive, copiable**
- **language:** Python (PySide6)
- **why:** it is a working frameless, always-on-top, translucent, drag-to-move PySide6 OSD overlay
  — precisely the `ui/overlay.py` lifeos declares but hasn't built, and it handles the Wayland/X11
  cross-platform traps lifeos will hit.

**Mechanism / portable snippet (window flags + drag):**
```python
from PySide6.QtCore import Qt
w.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint
                 | Qt.WindowDoesNotAcceptFocus)
w.setAttribute(Qt.WA_TranslucentBackground)

def mousePressEvent(self, e):
    if e.button() == Qt.LeftButton:
        self.windowHandle().startSystemMove()   # Wayland-safe drag
```
All rendering via a single `QPainter` path (`drawRoundedRect`/`drawText`) — no per-platform shims;
opacity affects only the background fill, text stays full-alpha.

**Integration steps:**
1. Copy the flag set + `startSystemMove()` drag into `ui/overlay.py`.
2. Default `QT_QPA_PLATFORM=xcb` on Linux for reliable always-on-top (Wayland caveat).
3. Keep the overlay optional (PySide6 is an extra) — guard imports so headless still boots.

**Gotchas:** `WindowStaysOnTopHint` is unreliable on native Wayland — the widget uses the X11
notification window type as a workaround; `startSystemMove()` is the Wayland-correct drag path.
Small project — treat as a recipe, not a dependency.

---

### Licence summary
All four references are **MIT / permissive → copyable**. The only caveat: litellm's *enterprise/proxy
admin* tier is separately licensed (commercial), so restrict copying to the MIT Python SDK
(`completion`, `Router`). No GPL/AGPL/BSL/SSPL/fair-code in the shortlist — nothing needs
reimplementation for licence reasons.
