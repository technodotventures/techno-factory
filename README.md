# Techno OS — Factory Module

This repository is the **factory module of Techno OS** — Techno Ventures' one system: Coffee is the collaborative surface, Pod/Smartware is the shared state substrate, and this module is the founder-controlled software factory that runs on top of both (Planner → Builder → Verifier, evidence-first, human at the gate).

**One system, not a separate deployable.** The factory is an internal module: skill packs + guard scripts + Coffee/Pod configuration. The bundled `src/`/`test/` TypeScript scaffold is the v0 tracer (work-intake + audit events), not a standalone service.

## Repository boundary

- `docs/` — the canonical documents (see below).
- `src/`, `test/`, `tsconfig*.json` — v0 tracer scaffold (accepts project-scoped work requests, persists work + audit events; HTTP and MCP adapters).
- `.env.example` — placeholder configuration only. **Never commit real credentials.**

## Docs (read order)

| File | What it is |
| --- | --- |
| `docs/PLAN.md` | Canonical v1 plan: invariant #0 (Coffee-first), seed, guards, security |
| `docs/Techno_OS.md` | Self-contained review brief of the whole system (~12 sections + change log) |
| `docs/research-mapping.md` | Research base (Uber, Spotify, factory.ai, eve/Foreman, Carson/Pocock, Bello, Multiplayer) + requirements A–G |
| `docs/setup-plan.md` | Phase 0–6 setup plan (Sandcastle executor, per-repo `.factory/` config, evidence wiring) |
| `docs/system-delineation-and-seed.md` | Role delineation (Coffee / Techno OS / Factory), 10 boundary invariants, the seed |
| `docs/architecture.md` · `docs/api-v0.md` | v0 tracer architecture + API surface |
| `docs/summary-for-review.md` | Earlier review summary (superseded by `Techno_OS.md` where they conflict) |

## Design invariants (summary)

1. **Coffee-first** — anything expressible through Coffee's existing primitives (Projects > Tasks > Docs > Agents; task Statuses, Automate-status with Deliverable, Pause-for-approval, Run limits) is done in Coffee before building anything new.
2. **Evidence, not claims** — the mission question is *did this actually happen?*; every deliverable carries proof (test output, recordings, scans, links).
3. **People make the judgment calls** — a human decides anything touching production, credentials, protected branches, or money; approvals happen in Coffee; silence never approves.
4. **The factory is bounded** — WIP cap (3), spend ceiling with hard halt, no worker approves its own output, mechanical diff-integrity scan at the gate, no self-approval; intelligence is `.md`, enforcement is machine code.
5. **Extend, don't multiply** — new capabilities are skills + tools with eval gates; new object types only where Coffee genuinely can't express it.

## Status

- Phase 0 (baseline commit) — docs + v0 tracer scaffold; zero production deployment. Next: seed a source of recurring low-risk work; the loop comes before the Coffee bridge, evidence before surfaces.
