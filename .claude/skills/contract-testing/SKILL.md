# Skill: Consumer-driven contract testing

## When to invoke
Auto-invoke when: chrysa-lib is about to release a new version, adding a new consumer of `@chrysa/auth` / `@chrysa/ui` / `@chrysa/api-client`, reviewing breaking changes in a library, or designing a new package API.

## 1. Core concept

Consumer-driven contract testing (CDCT) ensures a **provider** (library) never breaks its **consumers** (apps) without being aware of it.

```
Consumer (dev-nexus, my-fridge)    Provider (chrysa-lib/@chrysa/auth)
      ↓ declares contract                    ↓ verifies contract
  contracts/auth.json  ──────────────────→  CI gate on chrysa-lib PR
```

## 2. chrysa ecosystem layout

```
chrysa-lib/
  contracts/
    consumers/
      dev-nexus/          ← copy from consumer repo (or git submodule)
        auth-contract.json
      my-fridge/
        auth-contract.json
```

Each consumer repo declares its contract in `contracts/@chrysa/auth.json`.

## 3. Consumer contract format (Pact v11 — TypeScript)

```typescript
// contracts/auth.contract.test.ts — lives in the CONSUMER repo
import { PactV4, MatchersV3 } from "@pact-foundation/pact";
import { useAuth } from "@chrysa/auth";

const provider = new PactV4({
  consumer: "dev-nexus",
  provider: "@chrysa/auth",
  dir: "contracts",
});

describe("@chrysa/auth contract", () => {
  it("AuthConfig.apiBaseUrl is a required string", async () => {
    await provider
      .addInteraction()
      .given("valid auth config")
      .uponReceiving("a login request")
      .withRequest({
        method: "POST",
        path: "/auth/login",
        headers: { "Content-Type": "application/json" },
        body: { email: MatchersV3.string("user@example.com"), password: MatchersV3.string() },
      })
      .willRespondWith({
        status: 200,
        body: {
          accessToken: MatchersV3.string(),
          user: {
            id: MatchersV3.uuid(),
            email: MatchersV3.string(),
            name: MatchersV3.string(),
          },
        },
      })
      .executeTest(async (mockProvider) => {
        const { login } = useAuth({ apiBaseUrl: mockProvider.url });
        const result = await login("user@example.com", "password");
        expect(result.accessToken).toBeDefined();
      });
  });
});
```

## 4. Provider verification (chrysa-lib CI)

Add to `chrysa-lib/.github/workflows/ci.yml`:

```yaml
- name: Verify consumer contracts
  run: npx pact-provider-verifier \
    --provider "@chrysa/auth" \
    --pact-dir contracts/consumers/
```

Or use the shared workflow:
```yaml
uses: chrysa/shared-standards/.github/workflows/contract-testing.yml@main
with:
  provider: "@chrysa/auth"
  language: typescript
  contracts-path: "contracts/consumers/**/*.json"
```

## 5. Python packages (schemathesis)

For Python packages (`@chrysa/python/auth`), generate an OpenAPI spec and validate with schemathesis:

```bash
# Generate spec from FastAPI
python -c "import json; from api.main import app; print(json.dumps(app.openapi()))" > openapi.json

# Validate consumers' expected schema
st run openapi.json --checks all --hypothesis-max-examples 50
```

## 6. Consumer onboarding checklist

When a new project starts consuming a chrysa-lib package:
- [ ] Add `@pact-foundation/pact` to dev dependencies
- [ ] Create `contracts/<provider-name>.contract.test.ts`
- [ ] Run `pact:generate` to produce `contracts/<provider>.json`
- [ ] Open PR in chrysa-lib adding your contract to `contracts/consumers/<your-app>/`
- [ ] chrysa-lib CI gate will verify your contract on every PR

## 7. Breaking change protocol

When chrysa-lib wants to change an exported API:
1. Run `npm run contract:verify` locally against all consumer contracts
2. If any contract fails → it's a **breaking change** → must bump major version
3. Notify consumers via GitHub issue before merging
4. Consumers update their code + regenerate contracts before the new major is released

## 8. Forbidden

| Anti-pattern | Fix |
|---|---|
| Releasing chrysa-lib without running contract tests | Contract test CI gate is mandatory from v1.0 |
| Consumer importing private (`_internal`) exports | Only import from the public `index.ts` |
| Consumer relying on undocumented types | Open an issue in chrysa-lib to export the type |
| Pact file committed manually (not generated) | Always generate via `pact:generate` script |
