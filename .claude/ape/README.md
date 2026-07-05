# APE v2 — Automatic Prompt Engineering

Ce dossier déploie **APE v2**, une couche de prompt-engineering automatique branchée
sur le hook Claude Code `UserPromptSubmit`.

## Fichiers

- `ape-transform-v2.md` — la **méthode** (spec lue par le modèle). Portable (GPT / Gemini
  / Ollama / Mistral) : elle décrit la logique, pas la plomberie.
- `ape_hook.py` — l'**adaptateur mince**. Triage local rapide du prompt ; n'injecte la
  spec que lorsque l'optimisation en vaut le coût (fail-open : ne bloque jamais un tour).

## Les 3 régimes

- **SILENT** — prompt déjà bien structuré (>=4/5 slots) ou trivial (`oui`, `ok`, slash
  command). Rien n'est injecté, aucune mention d'APE.
- **SUGGESTIVE** (défaut si améliorable) — 1 à 3 slots manquants, tâche peu coûteuse. Le
  prompt est optimisé, exécuté directement, avec une note finale `— APE: ...`.
- **BLOCKING** — enjeux élevés : prompt long/coûteux, placeholder non résolu, ou `!ape`.
  Le prompt optimisé est présenté et validé avant exécution.

Court-circuit manuel : `sans APE`, `raw` ou `n'optimise pas` force SILENT.

## Désactiver

Retirer l'entrée `UserPromptSubmit` pointant vers `ape_hook.py` dans
`.claude/settings.json`. Les fichiers de `.claude/ape/` peuvent rester en place.

## Avant de généraliser

**Mesurer via Mirador avant de scaler.** La spec émet une trace structurée
(`raw / regime / task_class / slots_missing / optimized / user_decision`) : c'est ce
corpus qui dira si l'APE aide réellement.
