# Run-012 — Smartware substrate: DeepSeek fallback when no managed provider is active

- **Source**: Coffee card `N9zHVtucPsjsx9RthfOkIyDT` (Pod Factory line `bfhqkkn9ofbk`) — intake from the run-011 live deploy.
- **Branch**: `factory/fix-smartware-deepseek-fallback` · worktree `/opt/data/dev-workspaces/worktrees/pod-run012` · base `origin/main` `ccba1fb`.
- **Repo**: `technodotventures/pod` (private).

## Problem

`syncSmartwareLLMConfig` (`src/services/ai-provider.ts`) decides the substrate's LLM provider from the *managed* provider set only:

```ts
const nextProvider = active?.id === 'codex' ? 'none' : active?.id ?? 'none';
const nextModel    = active?.id === 'codex' ? '' : active?.model ?? '';
```

With no managed provider connected — the normal state on the founders' box, whose only key is DeepSeek — this pins the substrate to `none`, so every dream completes with **0 lessons / 0 conversations refreshed** and the cockpit shows raw rows with no synthesis. The environment has a working `DEEPSEEK_API_KEY`; the config lane simply never looks at it.

## Change

Fall back to DeepSeek only when no managed provider is active:

```ts
const deepseekFallback = !active && Boolean(process.env['DEEPSEEK_API_KEY']);
const nextProvider = active?.id === 'codex' ? 'none' : active?.id ?? (deepseekFallback ? 'deepseek' : 'none');
const nextModel    = active?.id === 'codex' ? '' : active?.model ?? (deepseekFallback ? (process.env['DEEPSEEK_MODEL'] || 'deepseek-chat') : '');
```

Preserved semantics: codex → `none` (the embedded extractor does not speak the Codex app-server protocol); an active managed provider always wins; no key → `none`; the idempotent early return is untouched.

## Acceptance criteria (from the card — 7)

1. No managed provider + `DEEPSEEK_API_KEY` → substrate reads `deepseek` + model.
2. No managed provider + no key → stays `none`.
3. Codex active → stays `none`.
4. Active managed provider wins; idempotent early return preserved.
5. `npm run beta:gate` green.
6. Unit test covers the four branch cases and fails before the change.
7. No new env var beyond `DEEPSEEK_API_KEY` / `DEEPSEEK_MODEL`.

## Approach

- New test `src/test/smartware-llm-config.test.ts`: 6 cases — the four branch cases plus `DEEPSEEK_MODEL` honoured and idempotency. Assertions read the substrate's **effective** config (persisted `config.json`, else the in-memory config the stub holds) so the pre-fix early return is visible as a failure rather than an ENOENT.
- `red-first`: 2 of 6 fail on the unfixed base (`provider: none` vs `deepseek`); the 4 guard cases pass (they must pass on both revisions).
- Substrate stand-in: `{ getConfig: () => state }`; provider activity is seeded through the real `writeIntegrationConfig` (codex `authenticated: true`, openai `api_key`).
- **Not delegated to a worker**: the change is 12 lines with an unambiguous contract; operator-lane implementation + independent gate re-run is the honest, cheaper path. The reviewer lane is unchanged.

## Out of scope

- Surfacing the fallback in Connections/Capabilities (a spec open question; silent fallback is accepted for v1).
- Any change to `codex` handling or to the managed-provider resolution order.

## Risks

- Low. The fallback only fires when `active` is null, so no currently-working configuration changes behavior; the codex rule is explicitly guarded by a test.
- `clearProviderEnv()` does not clear `DEEPSEEK_API_KEY` (verified) — the fallback reads a key the function leaves in place by design.
