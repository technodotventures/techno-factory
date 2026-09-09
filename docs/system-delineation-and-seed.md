# Techno Ventures — System Role Delineation & the Starting Point (Sep 07 2026)

Purpose: define WHO owns WHAT across the whole system (Coffee, Techno OS, Techno Factory, Pod/Smartware, expresso, Hermes, delivery providers), carve the minimum expandable seed, and record which ideas from the March 2026 Autonomous Dev Handbook carry forward (with old→new mapping). This is the document to hand to a reviewer asking "what is the system, and what do we build first?"

Validation note: the March handbook's toolchain (LangGraph/Mastra, GSD, Acontext, agentgateway, ecc-agentshield, rlm, RunLedger, autoresearch) is superseded — Superseded because this environment's own Pod/Smartware, our station configs, and the Sept research cover or improve every one of its jobs (detailed mapping in §5). But its **primitives** (typed decisions, trust tiers, replayable run ledger, repo qualification, learning gates, anti-metrics, founder-visible phases) are durable and are now part of our plan.

---

## 1. Role delineation — one sentence each

**One system:** Techno OS. It is a **modular monolith** (matching the house convention: one shell, one deployment, a typed registry of independently owned feature modules) whose modules are the shell/operating layer, the decision layer, and the factory execution layer. The module boundaries are as strict as if they were services (typed artifacts, no cross-module internals), so extraction later is mechanical — but there is ONE deployable, ONE identity, ONE ops story. External systems (Coffee, Pod/Smartware, expresso, Hermes, GitHub/GitLab) are peers over typed contracts.

**Where design lives:** per-venture repo `DESIGN.md` — the canonical, versioned, agent-agnostic design-system document (tokens: palette, type, spacing; brand rules), alongside `PROJECT.md` (what/why) and `AGENTS.md` (who does what) as the repo's three canonical docs. The factory *references* it (context packs for Planner/Builder), *checks* it (Gate A on-brand check for UI/brand changes), and *produces into it* (design artifact generation for GTM). The format adopts the OpenDesign `DESIGN.md` protocol (Apache-2.0; open-design.ai, verified 94.5K stars, BYOK, agent-agnostic skills — the same portable-skill pattern this plan uses for factory skills); the OpenDesign skill/template library is an optional **Design station** (expansion trigger, not seed) — see §5 expansion list and setup-plan Phase 6.

| System | Owns | Never owns |
|---|---|---|
| **Techno OS** — shell + operating layer (the OS shell) | The venture studio's operating layer: goals & ideas in, orchestrated work out. Owns the **Decision Orchestrator** (typed decisions + escalation targets), studio programs (which ventures run, budgets, policies, ringfences), and the founder route (voice/chat/notifications — "talk to Techno OS, it actions everything"). | Pipeline internals (delegated to its Factory module). Coffee's card state. Delivery providers. |
| **Techno OS — Factory module** (bound context; codebase stays in the `techno-factory` repo, deployed as the monolith's module) | The execution plane: signed work intake, station pipeline (Triage → Planner/SOC → Builder → Supervisor → Verifier → Adversary → Gate), EvidencePacks, budgets/cost telemetry, policy (risk tiers R0–R4 × trust tiers T1–T5), and delivery adapters (GitHub PR/checks, GitLab MR/pipeline, release targets). Only the module that touches providers. | Human decisions (approve/reject) — surfaced to founders via Coffee, decided by people. UI. Memory semantics. |
| **Coffee** (external) | The collaborative human/team surface: tasks, docks, Kanban boards, projects, files, recordings, meetings (agent-attended, transcribed) → **Decision Extracts + action items**, skills, and THE place where founders review (evidence incl. feature recordings) and approve/reject/steer. **Source of record for human work state.** | Agent execution state. Pipeline truth. Memory semantics. |
| **Smartware runtime** (embedded in Coffee — proposed) | Context/memory substrate for every layer: context packs (with provenance), lessons loop, expertise (who-knows), per-agent approvals ledger, run records, session governance records — Coffee-native, Gbrain-style (hybrid search over workspace content + agent-acted records), same DB + permission model as the surface. Firewall semantics: explicit scoped sharing. |
| **Pod** (same runtime; standalone companion app) | Standalone user-owned memory companion + agent-registry/BYO bridge (portable profiles) + approvals binder (owner-triggered) — a surface for individuals and BYO; **not a required hop** for the studio loop (decision in progress; upstream = Coffee-team conversation, see the Coffee proposal set, Appendix A). | Delivery, workflow semantics, task ownership. |
| **expresso** (external, peer) | The workflow language/runtime semantics: separates what the LLM observes/decides from what the system actually executes; receipts + authority (attested, not proven; UNKNOWN is a legal state). | Memory storage, UI, provider auth. |
| **Founder's personal agent** (external) | Agent runtime + the founder's own agent (also the harness for invited agents). | The above layers' state. |
| **GitHub / GitLab** (external) | Change request home: PRs/MRs, checks, CI, branch rules. | Factory decisions, approvals (workers can't approve own output — enforced). |

## 2. Rules that make the boundaries safe (readable invariants)

1. Cross-layer communication is via **typed artifacts only** (Decision, WorkItem, EvidencePack, ApprovalRequest/Decision, ContextBundle, Release, LearningProposal) — never raw chat or merged histories.
2. **Coffee never owns pipeline state; Factory never owns human decisions; Pod never owns delivery; expresso never owns UI.**
3. Trust is decided **once at dispatch** (signed webhook / authenticated ticket), stamped into the session, never re-derived from model-readable content.
4. Silence never approves. Unattended runs **deny-not-park**.
5. Every mutating request is authenticated, authorised, project-scoped, idempotent, auditable.
6. Every layer is independently replaceable/testable — the contract above, not the implementation.

## 3. The starting point (the seed, expandable by construction)

**Principle: build the smallest slice whose layers can only grow outward.** The seed is one venture repo, one bounded feature, the factory loop — with Coffee as a *not-yet-connected* surface (deferred by founder decision) and Pod as a *not-yet-connected* substrate. Both plug into typed artifacts (Decision/WorkItem/EvidencePack), so wiring them in later touches contracts, not architecture.

**Seed steps (order matters):**

1. **Repo qualification** (from March handbook §8 — the best single idea it has): score the pilot repo Green/Yellow/Red on CI reliability (last 20 runs ≥90% / 70–89% / <70%), test coverage (≥60% / 30–59% / <30%), dependency health (0 critical+0 high / 0 critical ≤3 high / any critical), reproducibility (clean checkout passes without manual steps), structure (conventional + README / partial / opaque). **Red = no agent runs. Yellow = T1–T3 only.** One AGENT run on a Red repo corrupts the learning corpus — the handbook is right, and the reason is ours: evidence from an unqualified repo misattributes failures.
2. **`.factory/` config in the pilot repo** — canonical, runtime-agnostic (the March doc's PROJECT.md/AGENTS.md pattern, adapted): `PROJECT.md` (what/why, ≤100 lines), `AGENTS.md` (station roles, approval matrix, trust tier rules, tool permissions), runtime adapters thin and generated. Station role files live here — roles are config, not code.
3. **The loop, minimal**: CLI/issue intake → Triage (classify; dedupe-first) → Planner (SOC + acceptance-criteria checklist, grounded in the checkout **docs-first; per-ticket `out_of_scope`; ask-only-if-irresolvable**) → Builder (Sandcastle sandbox; branch `factory/<type>-<slug>`; check-output record) → Verifier (blind; real diff; re-run fastest checks; **red-is-red: failing checks reported as failures**; verdicts) → **Gate A** (evidence completeness: test output, screenshots, and **feature recording for UI changes** — no recording = auto-fail, non-UI = not-applicable-with-reason). EvidencePack = report (status / changed files / checks / remaining risks / **lockfile-artifact churn justification**) + artifacts.
4. **Governance min**: approvals via CLI/API with binding fields (designed for Coffee to wrap); R0–R4 risk tier on the work item; T1–T5 trust tier per task, no carryover; human gates on merge/release/deploy/credentials/infra/governance; prod creds vaulted and manually brokered.
5. **Measurement from session one** (metrics, not logs): autonomous completion rate, human rescue rate, merge-without-rework rate, regression rate, cycle time. Anti-metrics explicitly *not* targets early: cost-per-task (optimizing cost early degrades quality — March handbook is right on this), false-escalation rate, silent failures, raw session count.

**What expansion looks like for each seed element** (each has a named trigger, not a date):
- Supervisor station → when bounded runs start drifting/serializing (Bello evidence: supervisor is the cheap win on messy specs).
- Adversary station → R3+ / critical paths.
- GitLab adapter → when a second provider is needed (parity contract pinned).
- Pod/Smartware context packs + lessons → when cross-run memory starts to matter (context packs also replace GSD .planning/ state).
**Expansion triggers (not phases):**
- **Design station** (OpenDesign-style, Apache-2.0, BYOK, agent-agnostic skills + `DESIGN.md` systems): when brand fidelity or design-production cost becomes real — GTM assets (decks, prototypes, HTML video, marketing images) for the MAKE/SHIP stage; local daemon for brand extraction (screenshot/Figma → DESIGN.md) or server-side skill runtime for artifact generation. Until then, design = `DESIGN.md` per venture repo (included in context packs + Gate A on-brand check) — zero new dependencies.
- Feedback loop (E2E walkthrough, production watchdog, rubric loop) → when the venture has users/revenue.
- Detail pilot → when monitoring exists; Graphify A/B → when context cost or token spend demands it.
- Learning gates → ≥50 run records AND rescue rate <30%, before any automated SOP/skill propagation or autoresearch-style loop (March handbook gating — adopt verbatim).

## 4. March handbook ideas adopted (with adjustments)

| Idea (March) | Value | Adjustment for today |
|---|---|---|
| **Decision as first-class primitive** (DIRECTIONAL / RISK / TRADEOFF; thresholds for auto-execute vs escalate; escalation targets CEO/CTO; run_record_id on every decision) | Keep — it's the contract Coffee/Techno OS need; our Decision envelope adopts this 3-type shape | Escalation targets become the named founder roles; auto-execute thresholds per risk tier; run_record_id → our workId |
| **Trust tiers T1–T5, no carryover, declared in brief, enforced pre-tool** | Keep as the ACCESS axis; our R0–R4 is the WORK axis | Two orthogonal axes: `riskTier` (work) × `trustTier` (agent's access for that task). Enforced by the hook level + gateway policy. T5 = human-approved merge/deploy (matches our human gates) |
| **RunRecord with replay fields** (commit SHA, prompt-bundle hash, model, policy version, trust tier, commands-exact) | Keep — our WorkItem/Run envelope gets a `replay` block | Rename fit: replay keyed on canonical doc hashes + station config versions |
| **Repo qualification (Green/Yellow/Red, 5 dimensions, 30-min fix**) | Keep — it's the correct FIRST step of the seed | Add our rule: qualification evidence is part of the first run's EvidencePack |
| **Decision Extracts from meetings** (Coffee AI summarizes transcripts to 3–5 structured decisions/week, no raw ingestion) | Keep — improves A5 meetings→work | Schema becomes our `DecisionExtract` artifact; deferred-to-Coffee wiring |
| **Learning gates** (≥50 RunRecords AND rescue rate <30% before SOP propagation / autoresearch) | Keep verbatim | Applies to our G3 skill/SOP auto-propagation and any routing-policy auto-tuning |
| **Anti-metrics** (cost-per-task as early optimization, false escalations, silent failures, session count as progress) | Keep — prevents optimizing the wrong thing | Cost telemetry reports, but cost is never a target pre-quality-floor |
| **Quality-gate ladder** (spec-vs-diff, trust-tier enforcement, blast radius, intent fidelity, regression-risk, rollback safety; RunLedger cassettes for behavioral drift) | Keep the cartesian mapping | Maps onto our Gate A/B: spec-vs-diff = SOC checks; RunLedger cassette pattern = CI replay of known-good agent sessions; intent fidelity/regression-risk → allowed to warn/blocks |
| **Founder-visible phase table** ("what can you do in Coffee after each phase") | Keep as a communication artifact | Adapt: seed → "founder can watch a PR appear from a CLI brief"; Coffee phase → "move a card to Ready; approve in Coffee; recording attached" |
| **Agent conscience / PreToolUse hook + agentgateway token broker** | Keep as pattern | Becomes our guardrail hook + vault broker |
| **GSD .planning/ state** | Replace | Pod context packs (compile) + factory notes — same three jobs (fresh context, persistent state, cross-session synthesis), better substrate |
| **Acontext / RunLedger / Mastra / LangGraph / rlm / SkillKit / NemoClaw / LightRAG / autoresearch tools** | Partially adopt | RunLedger cassette idea → our eval harness (hold-model-fixed methodology); autorsearch → G3 loop with same 3 requirements (scalar metric, unattended eval, one mutable file); the rest → Pod/Smartware, our station configs, compaction levers, vault, expresso |
| **CLAUDE.md adapter pattern** (canonical PROJECT.md/AGENTS.md + thin per-runtime adapters, one source of truth) | Keep — matches our "roles as config, runtime-agnostic" | `.factory/` canonical; generated adapters per harness (Claude Code/Codex/Hermes) |

## 5. What we deliberately do NOT carry from March

- The LangGraph + Mastra orchestration stack (our stations are configs + Pod/Smartware + expresso semantics; March's "deterministic workflows, approvals, durable execution" is our executor's jobs table).
- The "Coffee Chat API Proxy" dependency as the intake mechanism (today: Coffee MCP/API directly; the 50-line bridge pattern survives as a thin adapter).
- Claude-Code-as-the-only execution layer (provider-agnostic per multiplayer principle; sandcastle runner + BYO harnesses).
- Phase-by-month schedule (learning gates open on data quality, not time — March's own principle; we apply it to itself).
- The two-layer "orchestration vs execution" split (their order of build: dispatch bridge before working loop; our order: working loop first, Coffee bridge last, because a factory needs evidence before it needs surfaces — Carson's "start with the bottleneck you actually have").

## 6. What exists vs what the seed needs

Exists: `techno-factory` scaffold (v0 tracer, uncommitted), Pod/Smartware repos, research package (provenance.md + setup-plan.md + this doc), Coffee MCP client creds (unused). Seed work = qualification script + `.factory/` config + station role files + Sandcastle wiring + Gate A (incl. recording capture) + CLI intake + metrics. Nothing else needs building to ship the first feature PR.
