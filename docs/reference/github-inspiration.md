# lifeos — Deep-dive technique

**But (1 phrase).** `lifeos` est un assistant IA flottant multi-OS (Linux/Windows) à architecture par plugins — aujourd'hui un **scaffold headless** : CLI Click + loader de config TOML Pydantic + résolution de plugins activés + run-loop de logging + init Sentry ; l'overlay PySide6, le monitoring psutil et les plugins (Discord / AI / Notion / GitHub) sont **planifiés mais non implémentés**.

> État réel du repo : seuls `cli.py`, `app.py`, `config/settings.py`, `observability/` existent. Tout le reste décrit dans `CLAUDE.md` (`core/assistant.py`, `plugins/**`, `ui/**`) est du plan. Deps runtime : pydantic, pydantic-settings, httpx, psutil, rich, click, python-dotenv, sentry-sdk. Extras : PySide6 `[ui]`, discord.py `[discord]`. Python **>=3.14**.

Données GitHub **LIVE au 2026-08-15**. Toutes les sources ci-dessous sont des **deps directes déjà déclarées** de lifeos (ou l'API que lifeos consomme) → références de premier plan, pas des analogues lointains.

---

## opencode (AI provider backend consommé par lifeos)

- **Repo** : `anomalyco/opencode` (ex-`sst/opencode`) · **197745★** · pushed 2026-08-15 (très actif) · TypeScript · **MIT ✅ copiable**
- **Rôle pour lifeos** : `plugins/ai/opencode.py` (planifié) = client HTTP du serveur `opencode serve` (REST, port 4096). lifeos ne vendorise pas opencode, il **parle à son API HTTP** → la licence importe surtout pour copier des schémas de requête/réponse, pas du code.
- **Mécanisme réel** : `opencode serve` expose un serveur HTTP local ; on POST un prompt à une session et on lit la complétion (souvent en streaming SSE). C'est le pattern « local AI daemon » — lifeos route les prompts vers ce provider quand il est up, sinon fallback OpenAI-compatible.
- **Snippet portable (client httpx async pour `plugins/ai/opencode.py`)** :
  ```python
  import httpx

  class OpenCodeClient:
      def __init__(self, base_url: str = "http://127.0.0.1:4096", timeout: float = 30.0):
          self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout)

      async def health(self) -> bool:
          try:
              r = await self._client.get("/")
              return r.status_code < 500
          except httpx.HTTPError:
              return False  # provider indisponible → l'orchestrateur bascule sur OpenAI

      async def complete(self, prompt: str, session_id: str) -> str:
          r = await self._client.post(f"/session/{session_id}/message",
                                      json={"parts": [{"type": "text", "text": prompt}]})
          r.raise_for_status()
          return r.json()["parts"][-1]["text"]
  ```
- **Intégration** : implémente l'ABC provider de `core/assistant.py` ; `health()` sert au routing « meilleur provider disponible ». Respecte la contrainte CLAUDE.md (httpx.AsyncClient + timeout explicite).
- **Gotchas** : (1) l'API opencode bouge vite (197k★, push quotidien) — **pinner et tester les endpoints**, ne pas coder en dur le schéma. (2) port 4096 doit être configurable via TOML (pas de constante en dur — règle lifeos). (3) opencode est TS/Node : lifeos ne l'embarque pas, l'utilisateur doit lancer `opencode serve` séparément → documenter la dépendance externe.

## discord.py (plugin messaging)

- **Repo** : `Rapptz/discord.py` · **16137★** · pushed 2026-07-27 · Python · **MIT ✅ copiable**
- **Rôle** : extra optionnel `[discord]` → `plugins/messaging/discord.py` (webhook sender + bot channel monitor). Contrainte CLAUDE.md : le plugin doit **skip gracieusement si `discord.py` absent**.
- **Mécanisme réel** : `discord.Client`/`commands.Bot` ouvre une gateway WebSocket et dispatch des events (`on_message`) via une event loop asyncio ; les webhooks (`discord.Webhook`) sont un chemin HTTP-only sans gateway, parfait pour du fire-and-forget.
- **Snippet portable (import optionnel + webhook async)** :
  ```python
  try:
      import discord
      HAS_DISCORD = True
  except ImportError:            # extra [discord] non installé
      HAS_DISCORD = False

  async def send_webhook(url: str, content: str) -> None:
      if not HAS_DISCORD:
          return  # skip gracieux — jamais de crash (règle lifeos)
      import aiohttp
      async with aiohttp.ClientSession() as s:
          wh = discord.Webhook.from_url(url, session=s)
          await wh.send(content)
  ```
- **Intégration** : hérite de `BasePlugin` ; `setup()`/`teardown()` en `try/except` (plugin failure ne doit jamais crasher l'app). Le bot monitor tourne comme worker asyncio séparé.
- **Gotchas** : (1) discord.py tire **aiohttp**, pas httpx → deux clients HTTP dans le process ; garder aiohttp confiné au plugin discord. (2) le bot (gateway) exige `intents` + un token bot ≠ webhook ; le monitor de channel a besoin du `message_content` intent (privileged). (3) l'event loop discord.py doit cohabiter avec la loop lifeos — lancer via `asyncio.create_task`, pas `client.run()` (qui bloque/possède la loop).

## psutil (system monitor)

- **Repo** : `giampaolo/psutil` · **11263★** · pushed 2026-08-14 · Python/C · **BSD-3-Clause ✅ copiable**
- **Rôle** : dep directe → `plugins/system/monitor.py` (planifié) : monitor async émettant `SystemStatsEvent`. Clé multi-OS : psutil abstrait Linux **et** Windows (contrainte « no platform-specific code »).
- **Mécanisme réel** : `psutil.cpu_percent(interval=...)` échantillonne ; `virtual_memory()`, `disk_usage()`, `sensors_*` renvoient des namedtuples. psutil est **synchrone/bloquant** → l'envelopper dans un thread executor pour ne pas bloquer la loop async.
- **Snippet portable (monitor async non-bloquant)** :
  ```python
  import asyncio, psutil

  async def sample_stats() -> dict[str, float]:
      loop = asyncio.get_running_loop()
      # cpu_percent(interval=None) est non-bloquant (delta depuis dernier appel)
      cpu = psutil.cpu_percent(interval=None)
      mem = await loop.run_in_executor(None, psutil.virtual_memory)
      return {"cpu_pct": cpu, "mem_pct": mem.percent}

  async def monitor_loop(emit, period: float = 2.0):
      psutil.cpu_percent(interval=None)  # 1er appel = amorçage, ignoré
      while True:
          await emit(await sample_stats())
          await asyncio.sleep(period)
  ```
- **Intégration** : `emit` = event emitter de `BasePlugin` → `SystemStatsEvent` consommé par `ui/components/system_panel.py`. `period` configurable via TOML.
- **Gotchas** : (1) `cpu_percent(interval=None)` renvoie 0.0 au **premier** appel (pas de delta) — amorcer. (2) `sensors_battery`/`sensors_temperatures` **absents sur Windows** → `getattr`/try-except par capacité, sinon casse la contrainte cross-OS. (3) éviter `interval>0` dans une coroutine (sleep bloquant).

## Click (CLI)

- **Repo** : `pallets/click` · **17627★** · pushed 2026-08-15 · Python · **BSD-3-Clause ✅ copiable**
- **Rôle** : dep directe → `cli.py` déjà implémenté (`--config`, `--ui/--headless`, `--enable`, `--debug`, `--version`). Point d'entrée `lifeos = lifeos.__main__:main`.
- **Mécanisme réel** : décorateurs `@click.command`/`@click.option` construisent un parseur ; `multiple=True` accumule les `--enable` en tuple ; `type=click.Path` valide le chemin config.
- **Snippet portable (flags lifeos, aligné sur l'existant)** :
  ```python
  import click

  @click.command()
  @click.option("--config", type=click.Path(exists=False, path_type=Path), default=None)
  @click.option("--ui/--headless", default=True, help="Overlay flottant vs headless")
  @click.option("--enable", "enabled", multiple=True, help="Force un plugin (répétable)")
  @click.option("--debug", is_flag=True)
  @click.version_option()
  def main(config, ui, enabled, debug):
      settings = load_config(config)
      Application(settings, enable_ui=ui, debug=debug).run()
  ```
- **Intégration** : déjà en place ; `--enable` doit **overrider** les flags TOML au moment de résoudre `enabled_plugins()`.
- **Gotchas** : (1) mypy strict + décorateurs Click → override `disallow_untyped_decorators=false` sur `lifeos.cli` (déjà fait dans pyproject). (2) `--ui` loggue un warning et retombe headless tant que l'overlay n'existe pas (comportement actuel voulu).

## pydantic-settings (config)

- **Repo** : `pydantic/pydantic-settings` · **1422★** · pushed 2026-08-15 · Python · **MIT ✅ copiable**
- **Rôle** : dep directe. **Écart notable** : `config/settings.py` actuel utilise `BaseModel` + `tomllib` manuel, **pas** `BaseSettings`. L'interpolation `${ENV_VAR}` promise dans CLAUDE.md n'est **pas encore câblée**.
- **Mécanisme réel** : `BaseSettings` fusionne sources (init > env > dotenv > file) via `settings_customise_sources` ; `TomlConfigSettingsSource` charge un TOML nativement ; les secrets viennent de l'env, jamais du code.
- **Snippet portable (TOML + env, remplace le tomllib manuel)** :
  ```python
  from pydantic_settings import BaseSettings, SettingsConfigDict, TomlConfigSettingsSource

  class Settings(BaseSettings):
      model_config = SettingsConfigDict(env_prefix="LIFEOS_", env_nested_delimiter="__")
      plugins: PluginsConfig = PluginsConfig()

      @classmethod
      def settings_customise_sources(cls, settings_cls, init, env, dotenv, secret):
          toml = TomlConfigSettingsSource(settings_cls, DEFAULT_CONFIG_PATH)
          return (init, env, dotenv, toml)  # env > toml pour les secrets
  ```
- **Intégration** : migre `load_config` vers `BaseSettings` pour satisfaire « secrets via `${ENV_VAR}` » et « pas de secrets dans le code ». Garde le fallback « fichier absent = defaults ».
- **Gotchas** : (1) `TomlConfigSettingsSource` ne fait **pas** l'interpolation `${VAR}` — l'ordre des sources (env au-dessus de toml) est le vrai mécanisme ; pour du vrai `${VAR}` inline il faut un validator custom. (2) ne pas mélanger `BaseModel` (actuel) et `BaseSettings` sur le même arbre.

## httpx (client HTTP transverse)

- **Repo** : `encode/httpx` · **15423★** · pushed 2026-03-29 · Python · **BSD-3-Clause ✅ copiable**
- **Rôle** : dep directe. Contrainte CLAUDE.md : **tous** les appels HTTP (opencode, openai, notion, github) via `httpx.AsyncClient` avec timeout explicite (défaut 30s).
- **Mécanisme réel** : `AsyncClient` = pool de connexions réutilisable ; `timeout=httpx.Timeout(...)` granulaire (connect/read/write) ; supporte le streaming (`client.stream`) pour les complétions AI token-par-token.
- **Snippet portable (base commune des clients de service + streaming)** :
  ```python
  import httpx

  class ServiceClient:
      def __init__(self, base_url: str, token: str, timeout: float = 30.0):
          self._c = httpx.AsyncClient(
              base_url=base_url,
              headers={"Authorization": f"Bearer {token}"},
              timeout=httpx.Timeout(timeout),
          )
      async def aclose(self): await self._c.aclose()

  async def stream_chat(client: httpx.AsyncClient, payload: dict):
      async with client.stream("POST", "/v1/chat/completions", json=payload) as r:
          async for line in r.aiter_lines():
              if line.startswith("data: "):
                  yield line.removeprefix("data: ")   # SSE OpenAI-compatible
  ```
- **Intégration** : classe de base partagée par `plugins/ai/openai.py`, `services/notion.py`, `services/github.py` ; `aclose()` appelé dans `teardown()`.
- **Gotchas** : (1) un `AsyncClient` par plugin, **réutilisé** (pas un par requête) — sinon fuite de sockets. (2) toujours `aclose()` dans `teardown()`. (3) timeout jamais `None`.

## notion-sdk-py (service Notion — référence, PAS forcément dep)

- **Repo** : `ramnes/notion-sdk-py` · **2176★** · pushed 2026-08-14 · Python · **MIT ✅ copiable**
- **Rôle** : `plugins/services/notion.py` (planifié : search/create/update pages, API v1). lifeos ne liste **pas** ce SDK en dep (il vise httpx maison) → sert de **référence de mapping d'endpoints** et de gestion pagination, réimplémentable en httpx.
- **Mécanisme réel** : wrapper fin sur l'API REST Notion v1 (`Client.pages.create`, `databases.query`) avec header `Notion-Version` obligatoire ; pagination cursor `next_cursor`/`has_more`.
- **Snippet portable (client httpx maison, aligné contrainte lifeos)** :
  ```python
  class NotionClient:
      def __init__(self, token: str):
          self._c = httpx.AsyncClient(
              base_url="https://api.notion.com/v1",
              headers={"Authorization": f"Bearer {token}",
                       "Notion-Version": "2022-06-28"},
              timeout=httpx.Timeout(30.0))

      async def search(self, query: str) -> list[dict]:
          r = await self._c.post("/search", json={"query": query})
          r.raise_for_status()
          return r.json()["results"]
  ```
- **Intégration** : token via `${NOTION_TOKEN}` (env, jamais en code). Comme MIT, on peut copier des bouts du SDK, mais la contrainte « httpx.AsyncClient » pousse à réimplémenter léger.
- **Gotchas** : (1) header `Notion-Version` requis et versionné — le mettre configurable. (2) le SDK officiel est sync ; ici on veut async → réimpl httpx plutôt que wrapper.

## sentry-python (observabilité)

- **Repo** : `getsentry/sentry-python` · **2202★** · pushed 2026-08-15 · Python · **MIT ✅ copiable**
- **Rôle** : dep directe → `lifeos/observability/` déjà présent (init Sentry).
- **Mécanisme réel** : `sentry_sdk.init(dsn=...)` installe des hooks (excepthook, logging integration) qui capturent exceptions + breadcrumbs et les envoient au DSN. `traces_sample_rate` contrôle le tracing perf.
- **Snippet portable (init garde-fou, no-op si DSN absent)** :
  ```python
  import sentry_sdk

  def init_observability(dsn: str | None, debug: bool = False) -> None:
      if not dsn:
          return  # pas de DSN → no-op, l'app tourne quand même
      sentry_sdk.init(dsn=dsn, traces_sample_rate=0.0,
                      send_default_pii=False,  # OWASP: pas de PII/secret dans les logs
                      debug=debug)
  ```
- **Intégration** : DSN via `${SENTRY_DSN}` ; `send_default_pii=False` pour respecter « no secrets in logs ». Appelé tôt dans `Application.__init__`/`run`.
- **Gotchas** : (1) `send_default_pii` par défaut peut fuiter des données — le forcer à False. (2) le `before_send` doit scrubber les tokens plugins. (3) DSN optionnel → toujours guarder.

## rich (rendu terminal / logging)

- **Repo** : `Textualize/rich` · **57073★** · pushed 2026-06-23 · Python · **MIT ✅ copiable**
- **Rôle** : dep directe. Usage headless : logs lisibles (`RichHandler`), tables de statut plugins, panels de config résolue. Complète le run-loop de logging actuel de `app.py`.
- **Mécanisme réel** : `RichHandler` s'accroche au `logging` stdlib et colorise/formate ; `Console` rend tables/panels avec détection de largeur TTY.
- **Snippet portable (logging Rich pour le core headless)** :
  ```python
  import logging
  from rich.logging import RichHandler

  def configure_logging(debug: bool) -> None:
      logging.basicConfig(
          level=logging.DEBUG if debug else logging.INFO,
          format="%(message)s", datefmt="[%X]",
          handlers=[RichHandler(rich_tracebacks=True, show_path=debug)])
  ```
- **Intégration** : branché sur `--debug` de `cli.py` ; remplace le logging brut de `app.run()`. Utile pour afficher `enabled_plugins()` en table.
- **Gotchas** : (1) `rich_tracebacks=True` peut afficher des variables locales contenant des secrets → `suppress`/`show_locals=False` en prod. (2) sous Windows, activer `Console(force_terminal=...)` si sortie redirigée.

## openai-python (provider OpenAI-compatible — référence)

- **Repo** : `openai/openai-python` · **31378★** · pushed 2026-08-15 · Python · **Apache-2.0 ✅ copiable (attribution NOTICE)**
- **Rôle** : `plugins/ai/openai.py` (planifié : chat completions OpenAI-compatible + stream). lifeos vise httpx maison, mais ce SDK est la **référence du schéma chat/completions** et du protocole SSE de streaming.
- **Mécanisme réel** : `AsyncOpenAI().chat.completions.create(..., stream=True)` renvoie un async-iterator de `ChatCompletionChunk` ; sous le capot = POST `/v1/chat/completions` avec `Accept: text/event-stream`, chunks `data: {json}` terminés par `data: [DONE]`.
- **Snippet portable (parse SSE OpenAI-compatible en httpx, sans le SDK)** :
  ```python
  import json

  async def chat_stream(client, model: str, messages: list[dict]):
      payload = {"model": model, "messages": messages, "stream": True}
      async with client.stream("POST", "/v1/chat/completions", json=payload) as r:
          r.raise_for_status()
          async for line in r.aiter_lines():
              if not line.startswith("data: "): continue
              data = line.removeprefix("data: ")
              if data.strip() == "[DONE]": break
              delta = json.loads(data)["choices"][0]["delta"].get("content")
              if delta: yield delta
  ```
- **Intégration** : deuxième provider derrière l'ABC de `core/assistant.py` ; `base_url` configurable → couvre OpenAI, groq, ollama, LM Studio (tous OpenAI-compatible) = aligné sur le **standard IA multi-model/local-first** de chrysa.
- **Gotchas** : (1) Apache-2.0 exige de conserver le fichier NOTICE si on copie du code — la réimpl httpx l'évite. (2) sentinelle `[DONE]` non-JSON à filtrer. (3) `base_url` configurable = clé du local-first (ne pas coder api.openai.com en dur).

---

## Synthèse licences

| Source | Licence | Verdict |
| --- | --- | --- |
| opencode | MIT | ✅ copiable (mais consommé via API HTTP, pas vendorisé) |
| discord.py | MIT | ✅ copiable |
| psutil | BSD-3 | ✅ copiable |
| Click | BSD-3 | ✅ copiable |
| pydantic-settings | MIT | ✅ copiable |
| httpx | BSD-3 | ✅ copiable |
| notion-sdk-py | MIT | ✅ copiable (réf ; réimpl httpx préférée) |
| sentry-python | MIT | ✅ copiable |
| rich | MIT | ✅ copiable |
| openai-python | Apache-2.0 | ✅ copiable (garder NOTICE si copie de code) |

**Aucune source copyleft/restrictive (GPL/AGPL/Elastic/FSL/fair-code) dans le périmètre** → rien à réimplémenter pour raison de licence. Seul point d'attention : Apache-2.0 (openai-python) impose l'attribution NOTICE en cas de copie de code — évité par la réimpl httpx que la contrainte CLAUDE.md impose déjà.

**Note interne/pas d'équivalent** : la couche `plugins/base.py` (BasePlugin ABC + event emitter), l'orchestration provider de `core/assistant.py` (routing « meilleur provider dispo »), et l'overlay PySide6 frameless always-on-top sont du **code applicatif propre à lifeos** sans lib de référence unique — pour l'overlay Qt, réfs utiles : `Rapptz/discord.py` non pertinent ici ; regarder la doc Qt/PySide6 (`Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint`) plutôt qu'un OSS dédié.
