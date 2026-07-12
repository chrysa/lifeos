# Skill: Council — Decide With an Adversarial Panel

## When to invoke
Auto-invoke on a **high-stakes decision with genuine uncertainty**: "should I X or Y",
"pressure-test this", "arbitre entre", "dois-je faire X ou Y", "aide-moi à trancher",
architecture/stack/tooling calls, prioritization calls. Explicit trigger: "council this",
"run the council".

**Do NOT convene** for factual lookups, trivial yes/no, or decisions with no real
trade-off — answer directly instead.

## How it works
Put the decision through a panel of opinionated personas run as **real parallel subagents**
(genuinely independent), have them peer-review each other anonymously, then a chairman
synthesizes a clear call. Goal is **clarity, not consensus** — the chairman may overrule the
majority when the reasoning supports it.

## Profiles (persona presets)
Detect the domain, or honor `--tech` / `--prio` / `--produit`.

- **tech** (default): Architecte pragmatique · Sécu-OWASP · Perf/coût · Dette & simplicité · Ops/faisabilité
- **prio**: Impact business · Effort/risque · Coût d'opportunité · Utilisateur/terrain · Exécutant
- **produit** / generic: Contrarian · First-principles · Expansionist · Outsider · Executor

## Flow
1. **Enrich** — fold relevant project context (files, `git log`, memory) into the question, without biasing it.
2. **Frame** — restate the decision neutrally, identical wording for every persona.
3. **Panel** — spawn the 5 personas as parallel subagents, isolated contexts, 150–300 words each. They don't see each other.
4. **Peer-review** — anonymize answers as Persona A–E; each persona critiques the others' *arguments* (not identities). Skip only for low-stakes calls, and say so.
5. **Chairman** — synthesize converge / clash / blind spots / one clear recommendation + first step.
6. **Verdict** — markdown in terminal. On request: "→ Notion" persists the decision, "→ artifact" renders an HTML page.

## Verdict shape
```
## 🏛️ Verdict — <decision>
**Profile:** <tech|prio|produit>  ·  **Recommendation:** <one line>
### Converge
### Clash        <axis>: Persona A/C say X ; B/D say Y
### Blind spots
### Call & first step
```

## Rules
- Use subagents for real independence — don't roleplay all five yourself.
- Same framing for everyone; enrichment is context, not a thumb on the scale.
- Peer-review critiques arguments, never personas.
- The chairman states a decision. "It depends" is a failure, not a verdict.
