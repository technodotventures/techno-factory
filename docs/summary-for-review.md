# Techno Factory — Review Brief (v1 plan, Sep 07 2026)

Written for a reviewing agent (e.g. Neo, Head of Technology). You have no prior context: this brief is self-contained. Review for: soundness, over-engineering, missing pieces, safety gaps, and whether the sequencing gets a working factory in front of real work soonest. End with: (1) what you'd change, (2) what you'd cut for v1, (3) what you'd add.

## 1. Mission and context

Techno Ventures builds AI-native ventures. We want a proprietary **software factory** that eventually wraps Coffee (the collaborative human/team surface: docks, tasks, Kanban, Chat Coffee AI agents, projects, files, recordings, meetings→action items, skills) plus Pod/Smartware (user-owned memory/context substrate: context packs, lessons, expertise, agent-bound approvals, meeting sync). Ultimate goal: a founder talks to **Techno OS** about goals/ideas and the system actions them end-to-end, with founders in the loop for key decisions, approvals, and steering — approvals notified and decided **inside Coffee**.

Current decision (per founder, Sep 07): **leave the Coffee integration for the time being** — the factory is built standalone first; Coffee wiring slots in later through designed contracts, not a rewrite. Work is already under way: Coffee OAuth credentials saved (token exchange pending one-time consent), a prior draft backlog exists (SF-01…SF-10), and a separate `techno-factory` repo has a v0 tracer (never committed).

## 2. Research base (all primaries; caveats noted)

- **Uber** (Aug 2026): 70%+ of PRs from agents; cost equation `users × sessions × turns × requests × tokens × price` (terms 1–2 grow; 3–5 optimized; routing is ours). Levers: cheap subagent default model (highest impact); 400K-token auto-compaction; per-workload cache TTL; search-then-mount tool gateway; code-mode (script runs outside the model); grounded context graph (38s vs 20min wrong ungrounded); spend nudges at 50/80/100%. Methodology: benchmark from real work, Pareto per workload, hold model fixed when measuring our own changes. Do NOT copy the 1,000-server/24M-node scale artifacts.
- **Spotify** (engineering blog, primary): 99% weekly AI use, +76% PR frequency; Fleetshift 2.5M+ auto-merged maintenance PRs; Honk background agent verifies via CI builds; Backstage catalog exposed to agents as MCP/CLI; **golden state + Soundcheck → lint-as-active-guardrails** (agents self-correct); auto-derived context rejected 87.5% of the time (Vedder) → context is owner-curated; release "Robot" condition-checked state machine (−8h cycle). Bottleneck moves from coding to human judgment.
- **Factory.ai** (2.0 + research, Aug 2026): the loop signals→triage→change→build→test→review→secure→ship→monitor→more signals; three pillars (model independence + router, sovereign intelligence, continual learning); autonomy spectrum (droids → automations → missions). **Executable Standard of Completion (SOC)**: factory experiment, 24 ProgramBench tasks — single agent stopped at 36% parity on GDAL ("it didn't lack skill, it lacked a standard of completion"); SOC-driven system reached 90% (7-Zip 54→95, DuckDB 34→80). **Harness routing**: 58% cost cut vs frontier-always, cache-blind switching costs up to 2.37× an all-frontier baseline, validator model family ≠ implementer family. Caveats: one run/cell (no variance); system runs ~13× wall time — SOC buys completeness, not speed.
- **eve / Foreman** (Vercel template, MIT — code reviewed): four stations (Classifier/Analyst/Implementer/Reviewer); reviewer blind to implementer reasoning; factory brain (40K-char curated notes, per-repo key, reserved namespace); trust stamped once at dispatch ("nothing downstream re-derives trust from model-readable content"); approval taxonomy denied/not-applicable/user-approval with **deny-rather-than-park for unattended runs**; ship = human gate; brain writes denied for unattended (untrusted input poison risk); implementer = strongest coding model, reviewer = different vendor; `git safe.directory` sandbox pitfall; safety eval suite (prompt-injection, no-direct-push, ship-gate).
- **Bello** (MIT, Codex transport): build → supervise → review → attack → repair → accept with per-role model+reasoning; 66.3% less quota at +1.45% score (12+12 ProgramBench), +36.4% quality config, runtime-supervisor-only +9% on messy specs; FINAL_REPORT.md evidence shape.
- **Ryan Carson** (solo founder, ~25 PRs/day, 5–10 parallel agents): one task/one agent/one isolated env; evidence-PRs ("finish with evidence, not a cheerful claim"); 3 automations (recurring browser E2E, production watchdog, rubric-based improvement loop); prod creds vaulted + manually brokered ("agents must not quietly inherit the power to alter production"); $20K/month bill → route by task not habit; **"the expensive mistake is building the whole factory before you have work to feed it — start with the bottleneck you actually have"**; METR caution (measure outcomes, not PR counts).
- **Matt Pocock**: Sandcastle (sandcastle.run(): sandboxed agents, branch strategy, Docker/Podman/Vercel providers, hooks) = our executor primitive; Grill-Me (interview design concepts with dozens–100 questions BEFORE any PRD); ubiquitous language (shared-terms doc from codebase); TDD/type/browser fast feedback; deep modules + gray-box delegation + human strategic ownership.
- **Multiplayer AI Manifesto** (Sep 2026): five principles (never copy-paste; work with the door open; continuously improve; people are not routers; nothing starts from scratch) + firewall-every-agent + provider-agnostic + own your data + governance's four questions per session. Directly validates Coffee(surface)+Pod(scoped shared context).
- **Detail** (proactive bug scout, PR-or-ticket fixes; optional pilot) and **Graphify** (on-device repo graph, provenance-tagged paths; optional A/B). Both v2 pilots, not v1.

## 3. Current architecture concept

```
COFFEE (later) ── intake/decisions ─▶ TECHNO FACTORY (separate private deployable)
                                        Gateway/contracts · stations · policy · adapters
                          │                     │
                     POD/SMARTWARE         GitHub + GitLab (delivery)
                     (memory/approvals)    expresso (workflow runtime, peer)
                          └──── shared context/provenance across agents ────┘
  Feedback: E2E walkthrough · production watchdog · rubric improvement loop · monitoring→dedup→work items
```

## 4. Repo-shape verdict

- **Keep** in `techno-factory`: versioned contracts (WorkItem, Run, ActionIntent, ActionReceipt, ApprovalRequest/Decision, EvidencePack, ContextBundle, Release, LearningProposal); risk tiers R0–R4; gated actions (merge/release/deploy/credentials/infrastructure/governance = human-only); GitHub/GitLab adapters; Coffee/Pod adapter contracts.
- **Reshape**: execution layer on **Sandcastle** (or fork) instead of hand-rolled sandboxes; v1 intake = per-repo `.factory/` config + CLI; the HMAC gateway + service task DB demote to v2.

## 5. The plan (phases)

- **Phase 0 — Baseline**: commit v0 scaffold (zero commits today); test/typecheck/build gates; freeze envelopes + tiers; Sandcastle spike (branch strategy, hooks, `git safe.directory` hook, Docker provider).
- **Phase 1 — Single-repo loop** (the factory floor; one venture repo): stations as role configs — **Triage** (classify: type/priority/complexity/affected_area/actionable/needs_clarification; dedupe-first open+closed issues; repo labels only) → **Planner** (Grill-Me for design-sensitive; plan grounded in live checkout: problem_statement, approach + rejected alternative, ordered independently-verifiable steps, affected_surface w/ public contracts, risks, **acceptance-criteria checklist the Verifier applies verbatim**, test strategy, assumptions, open questions; for R2+/ambiguous: **executable SOC** before implementation, kept current; ubiquitous-language terms into context pack) → **Builder** (Sandcastle env, branch `factory/<type>-<slug>`, deviations recorded, no stubs, exact check-output record, fixed factory git identity, no mid-run questions) → **Runtime supervisor** (long/risky runs: catch drift, block dangerous actions pre-effect, restart without losing workspace) → **Verifier** (blind; real diff + re-run fastest checks; per-criterion pass/fail evidence; verdicts approve/request_changes/reject with traceability; different model family; evidence applies/passes/fails/not-applicable-with-reason) → **Adversary** (R3+ only: artifact without dev history, edge cases/invalid input/feature interactions; findings via controller) → **Gate** (evidence completeness pre-approval).
  - Evidence-first delivery (reports carry test output/screenshots/uncertainty; report shape = status, changed files, checks, remaining risks → EvidencePack v1).
  - Approvals in-factory (CLI/API, binding fields; deny-not-park for unattended; draft PRs run, human marks ready; brain/context writes = trusted callers only).
  - Security: vaulted + manually brokered prod creds, least privilege, external inputs untrusted, trust never re-derived from model content, audit log.
  - Guardrails: types/lint/tests feedback loop + browser E2E for UI work.
- **Phase 2 — Delivery**: GitHub + GitLab parity via provider-neutral ChangeRequest (native IDs; independent impls; webhook verify + dedup; missed events reconciled; worker token can't approve own output; only factory branches auto-fixed; red-CI diagnose→fix; GitLab version pinned; same scenario passes on both).
- **Phase 3 — Cost engineering**: route by task not habit; single-file MODELS config (implementer strongest, verifier different vendor); cache-aware routing; per-role reasoning; per-run+weekly telemetry with 50/80/100% nudges; routing records; providers swappable.
- **Phase 4 — Pod/Smartware**: owner-curated context packs (compile, provenance, pinned revisions, incl. ubiquitous-language doc), lessons loop, expertise, firewall semantics (explicit scoped sharing; cross-venture promotion = founder action), single serialized writer in beta.
- **Phase 5 — Feedback + pilot**: Carson's 3 automations (E2E walkthrough, production watchdog, rubric loop); monitoring/incident → one deduplicated work item (repro/severity/release-SHA/evidence; regression fails before fix passes after); Detail optional scoped pilot; pilot = one low-risk idea→GTM + held-out set (fixes/UI/docs), GitHub + GitLab independently, metrics = failures/interventions/rework/cost/latency/founder review time (never PR counts), model fixed when measuring harness, no simulated success, founders explicitly accept/revise/stop.
- **Phase 6 — Coffee surface (later)**: intake from tasks/docks; approvals decided inside Coffee (silence never approves); meetings→action items→work; Chat Coffee AI as harness (Coffee-created + BYO runners same contract); GTM handoff for `t_ad1743f9` (EXTRACT → STORY → MAKE → PROVE → SHIP → LEARN; Gates A/B).

## 6. Non-goals v1 (explicit)

No Missions/fleet parallelism (factory.ai sense); no Graphify/Detail in production (pilots only); no org-wide catalogs/fleet migrations (Spotify scale); no 1,000-tool ecosystems; no HMAC gateway + service task DB in v1; no Coffee UI changes in this repo.

## 7. Key invariants (hold these)

Silence never approves · trust decided once at dispatch · evidence over claims ("did this actually happen?") · unattended runs deny-not-park · only factory-owned branches auto-fixed · worker cannot approve/merge its own output · founder corrections supersede derived context · provider-agnostic config · every workflow/skill/context/routing change = versioned proposal → held-out eval → approval → canary → rollback.

## 8. Open decisions (founders + reviewers)

1. Pilot venture repo + risk-tier appetite.
2. Agent platform mix (which harness(es) — Sandcastle defaults to Claude Code; cloud vs local split per job type).
3. Model providers to route between (cheap + strong; validator family ≠ implementer family).
4. GitLab instance/version to pin.
5. Credential vault choice for the broker pattern.
6. Verify: is the 6-role station chain (Triage→Planner→Builder→Supervisor→Verifier→Adversary→Gate) right-sized for v1, or should Supervisor/Adversary wait for measured need? (Bello evidence says supervisor is the cheap win for messy specs; adversary has no such evidence yet.)

## 9. What exists today vs not

Exists: `techno-factory` scaffold (work envelope, HMAC, risk tiers, docs, tests — **uncommitted**); Pod/Smartware repos; research package (this session: `docs/research-mapping.md`, `docs/setup-plan.md`, SF-01…SF-10 backlog); Coffee MCP client credentials (unused, awaiting consent). Not built: any pipeline code, adapters beyond v0 tracer, kanban cards (drafted RF-01…RF-07, board write pending Coffee auth), GitLab work.
