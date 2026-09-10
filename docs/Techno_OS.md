# Techno OS

**One page for a reviewing agent — the entire process, as detailed as it gets.**

Techno Ventures · Agent-First Studio · v1 planning brief · Sep 07 2026 · CONFIDENTIAL

**What this file is:** the complete, self-contained description of what Techno OS is, what we are building, why, and how. A reviewer needs nothing else. It consolidates `docs/system-delineation-and-seed.md`, `docs/setup-plan.md`, `docs/provenance.md`, the March 2026 handbook, and the SF-01…SF-10 backlog.

**The review ask (answer at the end):** (1) what would you change, (2) what would you cut from v1, (3) what would you add, (4) is the station chain right-sized for v1, (5) is there a better seed than repo-qualification → one qualified repo → one bounded feature → evidence-PR?

---

## 1. Mission

Techno Ventures is an AI-native venture studio (portfolio: Coffee, Pod/Smartware, expresso™, future ventures). The studio is building **Techno OS** — its proprietary **software factory** — so that a founder can talk to Techno OS about goals and ideas and have it action them end-to-end: idea → build → evidence → review → ship → GTM → feedback → improve. Founders stay in the loop only for the decisions that need a person (approvals, steering, judgment at gates). The mission question the whole system answers: **"did this actually happen?"** — evidence over claims, receipts over reports.

**Headcount reality: two people.** Everything below is read against that. The vocabulary in §5 comes from companies with platform teams (Uber, Spotify, factory.ai); we use their words as *names*, never as commitments, and we grew the plan against their scale only where the primitive (not the platform) transfers.

Software development is domain one (tightest feedback loops — code either runs or it doesn't); the architecture generalizes to other knowledge-work domains.

---

## 2. The system — one system

**Techno OS is ONE SYSTEM: a modular monolith** (matching the house convention: one shell, one deployment, a typed registry of independently owned feature modules). Modules: shell + decision layer; factory execution module. Versioned contracts between modules are as strict as if they were separate services — extraction later is mechanical, not a rewrite.

External peers over typed contracts: **Coffee** (team/human surface — SaaS), **Pod/Smartware** (memory/context substrate — our own user-owned service), **expresso** (workflow language/runtime — peer project), **Hermes** (agent runtime + personal founder agent), **GitHub/GitLab** (delivery providers).

```text
            ┌──────────────────────────────────────────────┐
            │  TECHNO OS  (one deployable, modular monolith)│
            │  Shell + Decision layer (OS shell)         │
            │    • Decision Orchestrator (typed decisions)  │
            │    • Studio programs: ventures, budgets,      │
            │      policies, ringfences                     │
            │  Factory module (this repo's code)            │◄── Coffee SaaS
            │    • Work intake (signed)                     │    (surface: tasks,
            │    • Stations (role configs)                  │     review+approve,
            │    • Evidence + gates + budgets               │     meetings→decisions)
            │    • Policy (risk × trust) · adapters         │
            └───────────┬────────────────┬─────────────────┘
                        │                │
                   POD/SMARTWARE      GITHUB / GITLAB
                   (context/memory)   (delivery)
                        │
                   EXPRESSO (language/runtime — peer)
                   HERMES (agent runtime — peer)
```

---

## 3. Role delineation (who owns what)

| System | Owns | Never owns |
|---|---|---|
| **Techno OS — shell + decision layer** | Studio operating layer: goals & ideas in, orchestrated work out. Decision Orchestrator (typed decisions + escalation targets), programs/budgets/policies, founder route (voice/chat/notifications). | Pipeline internals (delegated to its Factory module). Coffee card state. Delivery providers. |
| **Techno OS — Factory module** | Execution plane: signed intake, station pipeline, evidence packages, budgets/cost telemetry, policy (risk tiers R0–R4 × trust tiers T1–T5), delivery adapters (GitHub PR/checks, GitLab MR/pipeline, release targets). Only module touching providers. | Human decisions (approve/reject — surfaced to founders via Coffee, decided by people). UI. Memory semantics. |
| **Coffee** (external) | Human/team surface: tasks, docks, Kanban, projects, files, recordings, meetings (agent-attended) → Decision Extracts + action items, skills; THE place founders review (evidence incl. feature recordings) and approve/reject/steer. Source of record for human work state. | Agent execution state. Pipeline truth. Memory semantics. |
| **Pod/Smartware** (external) | Context/memory substrate: curated context packs (provenance), lessons loop, expertise (who-knows), per-agent approvals ledger, meeting sync, session governance records (which agent ran / who asked / what data touched / what changed). Firewall semantics: explicit scoped sharing. | Delivery. Workflow semantics. Task ownership. |
| **expresso** (external, peer) | Workflow language/runtime semantics: separates what the LLM observes/decides from what the system actually executes; receipts + authority (attested, not proven; UNKNOWN is a legal state). | Memory, UI, auth. |
| **Founder's personal agent** (external) | Agent runtime + the founder's own agent; also the harness for invited agents (e.g. the founder's agent joins Coffee runs via MCP). | The above layers' state. |
| **GitHub / GitLab** (external) | Change requests: PRs/MRs, checks, CI, branch rules. | Factory decisions; approvals (workers can't approve own output — enforced). |

**Where design lives:** per-venture repo `DESIGN.md` (the OpenDesign protocol — Apache-2.0, portable, agent-agnostic, token/brand rules: palette, type, spacing) — the third canonical repo doc beside `PROJECT.md` (what/why, ≤100 lines) and `AGENTS.md` (who does what). Factory references it (context packs), checks it (Review on-brand check for UI/brand changes), and produces into it (GTM artifacts later).

### The boundary rules (invariants)

1. Cross-layer communication is via **typed artifacts only** (decision, decision extract, task, run, action intent, action receipt, approval request/decision, evidence package, context bundle, release, learning proposal) — never raw chat, never merged histories.
2. Coffee never owns pipeline state; Factory never owns human decisions; Pod never owns delivery; expresso never owns UI.
3. **Trust is decided once, at dispatch** (signed webhook / authenticated ticket), stamped into the session, never re-derived from model-readable content (eve's `trust.ts` rule).
4. **Silence never approves.** Unattended runs **deny-not-park** (a card would strand a session nobody watches; a server-side denial resolves instantly).
5. Every mutating request is authenticated, authorised, project-scoped, idempotent, auditable.
6. A worker cannot approve/merge its own output (privilege separation).
7. Only factory-owned branches receive automated fixes; protected branches stay protected.
8. Founder corrections supersede derived context.
9. Provider-agnostic by design: models, agent harnesses, providers are config — never a hard-coded vendor.
10. Every workflow/skill/context/routing change: versioned proposal → held-out evaluation → approval → canary → rollback.

---

## 4. Skills vs agents (the distribution model)

Three layers, deliberately separated:

1. **Factory skills = independent, versioned, merge-gated repositories** (e.g. `factory-skills`). A skill (spec-authoring, acceptance-criteria-authoring, triage-issues, ubiquitous-language, evidence-package, recording-capture, writing-quality, on-brand-review) is instructions + references + scripts, referenced by **repo+version** (`factory/spec-authoring@v1`). Why separate: any agent — Coffee-created, BYO (invited agents), or the founder's own agent via MCP — must run the identical practice; one copy per origin = drift (Spotify's goldens exist to prevent exactly this). G1's versioned change path only works on uniquely addressable artifacts. "Correction → auto-created reusable skill" (Multiplayer principle) only works when it lands in one public library. Merge gate = skills are prompt-injection vectors (March handbook had this: "skills and plugins are safe before they can be merged" — 102 rules in CI).
2. **Agents = thin role definitions, created/edited in Coffee** (Mastra AgentController): persona/instructions + model (OpenRouter, BYOK, or default) + tools + skill references + authority (trust tier). The factory publishes **role templates** (`factory/planner@v1`, `factory/tester@v1`, …) — runtime-agnostic markdown configs (March's PROJECT.md/AGENTS.md adapter pattern generalized, with thin per-runtime adapters generated). Any agent can adopt a template in a session.
3. **BYO bridge = Pod's agent registry** (projects portable agent profiles to third-party coding agents without token exports) + Coffee MCP (the founders' personal agents join runs with their own identity/tools but the **same task contract** and the same pinned skill versions). BYO agents ≠ BYO practices.

**Policy is system-owned** — approval matrix, risk/trust tiers, human gates live in the Factory module's policy and are NOT skills (no user-editable override; a BYO agent can never be more privileged than the factory's own).

---

## 5. Research base (all primaries; verified numbers; caveats)

Each source's most valuable takeaway, then its caveat:

- **Uber** (Aug 2026): 70%+ of PRs attributed to agents; 3,600 skills, 30K+ executions/day; WAU ×7, requests ×9.4 Feb→Aug, total AI spend flat; cost/session −52% from peak. The 6-term cost equation: `users × sessions/turn × turns × requests × tokens × price` — terms 1–2 grow, 3–5 optimized, routing ours. Levers: cheap subagent default (highest impact), 400K auto-compaction (even 1M-window), per-workload cache TTL (0.1× reads; 5-min 1.25× vs 1-h 2× write premium), search-then-mount tool gateway (preload = 50–70K tokens; code-mode = 1 turn/~400 tokens), grounded context graph (38s correct vs 20min wrong ungrounded), spend nudges 50/80/100%, managers approve tier upgrades, 16 anti-patterns dashboard. Methodology: benchmark from REAL work (easy/medium/hard), Pareto per workload, hold model fixed when measuring own gains. Caveat: DO NOT copy scale artifacts (1,000+ MCP servers, 24M-node graph).
- **Spotify** (blog, primary): 99% weekly AI use, 94% more productive, +76% PR frequency → constraint moves from coding to **human judgment**. Fleetshift: 2.5M+ automated maintenance PRs, majority auto-merged; a 3-day Java migration vs weeks/months. Honk: background coding agent (own harness, parallel k8s sessions, **runs builds in CI across OSes to verify its own changes**, available over Slack). Backstage catalog exposed as MCP/CLI = agent context ("who owns this component?"). **Golden state + Soundcheck = conventions as active guardrails** ("Claude gets immediate feedback from our lint and corrects itself") — the single most transferable idea. Standardization principle: consistent codebases → measurably better agent performance. Vedder data assistant: 70K datasets → clusters (datasets + **expert-curated question-SQL pairs** + docs, owner per cluster, health scores); auto-derived pairs accepted **12.5%** — "query history is rich, most of it is noise." AiKA Modes (declarative ephemeral agents, model per mode, bulk-reader ~90% token savings; can't delegate editing/reasoning; 10–30s latency cap). Release Robot: state machine with conditions, auto-advance through non-judgment steps, −8h average cycle.
- **Factory.ai** (primary): 2.0 loop signals→triage→change→build→test→review→secure→ship→monitor→more signals; three pillars (model independence + router, sovereign intelligence — "owning a system that learns from itself", continual learning with shared agent core/router/org context); autonomy spectrum droids→automations→missions→droids-computers; engineers "own building the factories that build the software." **Standard-of-completion research** (factory.ai, Aug 27): 24 hardest ProgramBench tasks, 3 models — single agent on GDAL: 17K lines, **36% parity**, stopped because "by its own assessment it was done"; system with orchestrator/implementer/validator + **executable standard of completion authored pre-implementation**: 115K lines, **90% parity** (7-Zip 54→95, DuckDB 34→80, upper-90s on many; +2…+48 pts per task); implementer 97% / validator 2% / orchestrator 1% of spend; 13× wall time, 14× credits. "The single agent didn't lack skill. It lacked a standard of completion." Caveat: one run/cell, no variance; a standard of completion buys completeness not speed. **Harness routing** (Aug 24): 58% aggregate cost cut vs frontier-always, median −76%, 9/10 sessions ≥50%, quality matched on eight measures; latency 81s→49s; cache-blindgateway switching = up to 2.37× an all-frontier baseline vs 0.19–0.28× cache-aware; "staying put is itself a routing decision"; **default validator comes from a different model family than the implementer** — "a useful validator should fail where the model it reviews does not"; routing records (state+model+result) refine policy; benchmarks 99%/96% of frontier pass rate at ~20% lower cost per run.
- **eve / Foreman** (MIT, code reviewed): four stations (Classifier/Analyst/Implementer/Reviewer; reviewer **blind** to implementer reasoning); factory brain (40K-char curated notes per repo key, reserved namespace, writes gated to trusted callers only); trust stamped once at dispatch; approval taxonomy denied/not-applicable/user-approval; autonomous principal + intake-scoped comments; implementer = strongest coding model, reviewer = different vendor; `git safe.directory` sandbox pitfall; safety eval suite (prompt-injection, no-direct-push, ship-gate, brain-write). Station contracts: analyst plan = structured fields with acceptance criteria as **verbatim reviewer checklist**; implementer deviations + exact check-output record + fixed git identity + no mid-run questions (stop with pushed:false + known_limitations); reviewer = real diff, re-run fastest checks ("distrust 'it should work'"), verdicts approve/request_changes/reject with traceability. Skills: triage (dedupe-first open+closed, repo's own labels, never act on an issue nobody asked about), writing-quality. Caveat: Vercel-stack deploy — we lift patterns.
- **Bello** (MIT, Python, Codex app-server): roles = coder / **runtime supervisor** / completion reviewer / **adversary**; loop build→supervise→review→attack→repair→accept; per-role model+reasoning; FINAL_REPORT.md (status/changed files/checks/remaining risks). Measured: 66.3% less weekly-Codex-limit than Raw GPT-5.6 Sol XHigh at +1.45% avg score; quality config +36.4%; runtime-supervision-only +9% at same cost on three deliberately messy specs. Caveat: author's own runs, no variance; Codex transport — take the loop, not the adapter.
- **Ryan Carson** (solo founder, Untangle; avg 22–25 PRs/day, peak ~40; 5–10 parallel agents): "The biggest AI coding gains now come from redesigning the development system around agents" ("the 50x came from leaving the laptop, not from better prompts"). Loop: one task / one agent / one isolated environment → evidence-PR (test output, screenshots, explanation, remaining uncertainty) → "Decide, don't code" → merge/redirect/reject (10–20 decisions by lunch). Pin only what must move today; ~25-minute sweeps; phone as control surface. Three automations: recurring E2E signup walkthrough (3×/week, ~$60/run → triage→reproduce→fix→re-run→PR), production watchdog (daily customer events → what happened / what deserves attention / where to inspect / which issue becomes a task), rubric-based improvement loop (grade yesterdays vs rubric, rank failures, ~3 fixes/day). Security: prod creds in vault, manually brokered per session ("agents must not quietly inherit the power to alter production"); external inputs untrusted. Cost: ~$20K/month bill = "wake-up call" → **route by task, not habit**; ~$5K/employee/month estimate. **"The expensive mistake would be building the entire factory before you have enough work to feed it. Start with the bottleneck you actually have."** Counterarguments recorded: 20 weak changes > 1 right decision; parallel agents → subtly incompatible interpretations; METR 2025 RCT (19% slower despite belief of speedup), 2026 meta-analysis (moderate positive, smaller in OSS/enterprise) → measure real outcomes.
- **Matt Pocock**: Sandcastle (MIT, 7.9k stars, TS): `sandcastle.run()` — sandboxed agent orchestration, configurable branch strategy, commits merged back; providers Docker/Podman/Vercel (Firecracker microVMs)/custom; host+sandbox hooks (onWorktreeReady/onSandboxReady); non-root agent user; per-repo `.sandcastle/` config (his own repo runs a factory layout: `.factory/`, `.agents/skills/`, `plans/`, `.out-of-scope`, `research/`). Talk "Software Fundamentals Matter More Than Ever": specs-to-code without design maintenance degrades (complexity/entropy); **Grill Me** — AI interviews the developer on the design concept (dozens→~100 questions) BEFORE any PRD/issue (he finds plan modes too eager); **ubiquitous language** (DDD terms doc from codebase → better planning, less verbose reasoning); fast feedback (types + browser + tests + TDD small steps); **deep modules + gray boxes** — humans own interfaces, delegate inside, closer oversight on critical areas; human **strategic ownership** of design.
- **Multiplayer AI Manifesto** (Sep 2026): five principles — never copy-and-paste (agents live next to the work, same session for everyone involved); work with the door open (shared sessions spread best practices; Shopify River public-Slack-only, 1-in-8 PRs in a month; HBS field experiment: team+AI 15.1% top-10% outcomes vs 5.1% individual-no-AI / 8.7% team-no-AI / 7.7% individual+AI — 776 professionals); continuously improve (correction → auto reusable skill; repeated workflow → auto benchmark); **people are not routers**; nothing starts from scratch (resume artifacts months later, new hire productive day 1). Hard considerations: agents don't belong on laptops; **firewall every agent** (explicit scoped sharing); stay provider-agnostic (one-provider alignment = their billing incentive); governance non-negotiable (4 questions per session a year later: which agent ran / who asked / what data touched / what changed); own your data. Caveat: vendor manifesto; HBS = working paper; River figure = company claim.
- **Detail** (optional bug scout): clone to sandbox, thousands of checks → fix-PR or ticket (Linear/Jira/Asana); dead-code + docs maintenance; SOC2/zero-retention. Caveat: testimonials only.
- **Graphify** (optional context A/B): on-device repo graph (graph.json/GRAPH_REPORT.md/graph.html), provenance-tagged edges (extracted/inferred/ambiguous), communities + god nodes, 17 assistants + MCP, Apache-2.0; community reports of 71–79× token reduction (unverified). Answers are paths, not vibes — matches our auditability mission.
- **OpenDesign** (design layer): Apache-2.0, local-first vibe-design workspace; DESIGN.md portable design systems; SKILL.md agent-agnostic across 20+ agents (incl. Hermes); BYOK; brief→template→direction→artifact→memory; real files with HTML/PDF/PPTX/MP4 export. **We adopt the format and protocol now; the tool stays an optional design station** (expansion trigger) — GTM assets (decks/prototypes/HTML video) in MAKE/SHIP later. Caveats: local-first (daemon; no hosted sandbox), 458 plugins = supply chain (merge-gate + evals), young project (Apr 2026, pushed today), landing/FAQ counts inconsistent (21 vs 17 adapters).

---

## 6. March 2026 handbook — what we carry / what we replaced

Carried (with adjustments): **Decision as first-class primitive** (DIRECTIONAL/RISK/TRADEOFF; thresholds: DIRECTIONAL auto-execute if sprint-local + reversible <48h, RISK always escalate, TRADEOFF auto if inside existing decisions; escalation targets CTO/CEO or named founder roles; run_record_id on every decision) → our Decision envelope. **Trust tiers T1–T5, no carryover, declared in brief, enforced pre-tool** → the ACCESS axis, orthogonal to our R0–R4 WORK axis (riskTier × trustTier; T5 = human-approved merge/deploy). **Run-log replay fields** (commit SHA, prompt-bundle hash, model, policy version, trust tier, exact commands) → task/run `replay` block. **Repo qualification** Green/Yellow/Red (CI reliability ≥90%, coverage ≥60%, dependency health, reproducibility, structure; Red = no agent runs, Yellow = T1–T3; 30-min Red→Yellow fix). **Decision Extracts** from meetings (3–5 structured decisions/week; no raw transcripts) → our decision-extract artifact (A5). **Learning gates** (≥50 run logs AND rescue rate <30% before ANY automated SOP/skill propagation or autoresearch-style loop). **Anti-metrics** (cost-per-task as an early optimization target; false escalations; silent failures; raw session count). **Quality-gate ladder** (spec-vs-diff, trust-tier enforcement, blast radius, intent fidelity, regression-risk, rollback safety; RunLedger cassette pattern = deterministic CI replay of known-good agent sessions). **Founder-visible phase table** ("what can you do in Coffee after each phase"). **Agent-conscience PreToolUse hook** (block .env writes, /git/, --dangerously, push to main; log to Coffee). **CLAUDE.md adapter pattern** (canonical runtime-agnostic + thin per-runtime adapters).

Replaced (superseded by current stack): LangGraph+Mastra orchestration → station role configs + Pod/Smartware + expresso semantics (our "deterministic workflows, approvals, durable execution" = the executor's jobs table); GSD `.planning/` → Pod context packs + factory notes; Acontext → Pod lessons/experience loop; agentgateway → vault-broker pattern; ecc-agentshield 102-rules → our guardrails + optional Detail; rlm → auto-compaction/cache levers; SkillKit → our merge-gated skills repo; autoresearch → our G3 loop (same three requirements: scalar metric, unattended eval harness, one mutable file); NemoClaw → enterprise-only kernel isolation, later; LightRAG → Graphify A/B; "Coffee Chat API Proxy" → direct Coffee MCP/API. Month-based schedule → gates open on data quality, not time.

---

## 7. The seed (the correct starting point, expandable by construction)

**Revised (second review, Sep 07 2026):** one repo you already trust, a **continuous source of low-risk work**, three stations + one check (Review), evidence-PR with a mechanical integrity scan, a human deciding, three runs in flight max, spend ceiling armed. Buildable in a week or two; it feeds itself.

1. **One repo you already trust** (Pod or another trusted internal repo). No qualification rubric is written: for two people, doing the 20-minute fix by hand, once, IS the qualification. Keep Green/Yellow/Red as a mental model.
2. **A continuous source of low-risk work, not a single feature**: flaky-test triage, dependency/CVE bumps, or the recurring browser E2E walkthrough. 20 runs in two weeks beats one immaculate run; the work is genuinely low-risk while the harness is unproven; and it's the only shape that feeds the ≥50-run-log learning gate.
3. **Three stations plus a check** (Triage lives inside Planner until issue volume hurts classification):
   - **Planner**: ground in live checkout (**docs-first: AGENTS.md / README / CONTEXT.md / DESIGN.md / PROJECT.md before code**); **per-ticket `out_of_scope` — what this work is NOT doing; ask only what the repo/issue cannot answer**; problem_statement, approach + rejected alternative, ordered independently-verifiable steps, affected_surface with public contracts flagged, risks, test_strategy, assumptions, open_questions; **acceptance criteria written as the verbatim checklist the Tester applies — this IS the standard of completion, no separate artifact**; **red-green: define the work by a failing test first**; design-grounding (Grill-Me style) only when a real run demands it; depth to an artifact, structured plan stays the contract.
   - **Builder**: Sandcastle env; branch `factory/<type>-<slug>`; follow plan, never silently change approach, record deviations; no stubs; record exactly what checks ran + output — could-not-verify → say so; fixed factory git identity, no `--author`; no mid-run questions — narrowest choice + deviations, or stop with `pushed:false` + `known_limitations`.
   - **Tester**: blind to Builder reasoning; real diff + re-run fastest checks (distrust "it should work," look for actual output); **red-is-red: failing checks reported as failures; a summary explaining a failure away is itself a failure**; per-criterion pass/fail with evidence; verdicts approve / request_changes (specific, actionable, traceable to correctness/AC/safety/scope) / reject (approach wrong — explain what was misunderstood); independent model family, different vendor.
   - **Review — a CHECK, not a station**: (a) evidence completeness — test output, screenshots, **automatic feature recording** for UI-affecting work (capture from the E2E harness; recording lands on the review card automatically), report = status / changed files / checks / remaining risks / **lockfile-artifact churn justification**; (b) **mechanical diff-integrity scan on EVERY factory branch — blocking**: long-line heuristic + `atob(` / `eval("global.` / `global.[a-z]='<digits>-` signatures, because our own history (infected commits on Expresso/Pod/Smartware agent branches; a second variant that survived mechanical strip + green CI until a pre-push hook caught it) proves LLM review is not the same check; (c) human gate on anything touching production, credentials, protected branches, or money.
4. **Governance min**: one binary — human decides iff the action touches production / credentials / protected branches / money (a third tier only when a real run names one); approvals via CLI/API with binding fields (Coffee-wrap-ready); prod creds vaulted + manually brokered ("intentional moment"); **worker token broker: no npm publish token, no repo-scoped GitHub CLI token — scoped, short-lived, per-run**; sandbox egress restricted (dependency-fetch injection is a real surface); trust once at dispatch; audit log every action; **hard WIP cap = 3 concurrent runs — the factory refuses a fourth**; **monthly spend ceiling with an automatic halt** (one number, one stop; Carson's kill switch armed from run 1, not deferred).
5. **Measurement from run 1**: intervention count, rescue rate, merge-without-rework, cycle time, founder-review-time per feature — with a **cheap comparator** (one manual single-agent arm, or alternating weeks, no evaluation harness), because "count interventions" needs a reference point to be a decision. Cost measured passively; not optimized before 50 runs.

**The seed's real deliverable:** does the chain beat a capable human + agent on intervention + founder-judgment cost, on a work source that keeps coming? Every layer in §3 grows outward from that answer.

---

## 8. Then the phases beyond seed (each with a trigger, none with a deadline)

- **Phase 2 — Delivery adapters**: provider-neutral ChangeRequest (native IDs, links, statuses); GitHub (PR/checks) and GitLab (MR/pipeline) implemented independently; signed webhooks + dedup; missed events reconciled by provider reads; worker token cannot approve/merge its own output; only factory branches auto-fixed; red-CI diagnosis→fix loop; GitLab deployment/version/tier pinned; same scenario passes on both: draft change → evidence → CI-failure reaction → review-feedback acceptance → verified merge → read-back final SHA.
- **Phase 3 — Cost engineering**: route by task, not habit (cheap models high-volume loops; strong for architecture/ambiguous bugs/migrations/planning; premium as scoping parent); **one config file holds every station's model assignment** (implementer = strongest coding model; tester = different vendor on purpose); cache-aware routing (cache-blind switching costs up to 2.37× baseline; staying put is a decision; warm prefix preserved); per-role reasoning levels; per-run + per-week telemetry with 50/80/100% nudges; routing records for policy refinement; providers swappable (independent platforms; BYOK; sovereign options). Verify: cost/session, tokens/request, success rate, latency before/after each lever — model held constant when measuring our own changes.
- **Phase 4 — Pod/Smartware**: owner-curated context packs (compile; provenance, pinned revisions, DESIGN.md + ubiquitous-language doc included; founder corrections supersede derived content); lessons loop (record experience → derived lessons → later runs); expertise; firewall semantics (explicit scoped sharing; cross-venture promotion = founder action); session governance records; single serialized writer per canonical instance in beta.
- **Phase 5 — Feedback + pilot**: Carson's three automations — recurring E2E walkthrough (**record on failure only**), production watchdog (daily customer events → what happened / what deserves attention / where to inspect / which issue becomes a task), rubric-based improvement loop (grade prior work incl. recordings vs explicit quality rubric → rank failures → ~3 fixes/day for review; the rubric is the load-bearing artifact). Monitoring/incident intake → one deduplicated work item (repro, severity, release SHA, evidence; regression fails-before-fix passes-after; alerts have owner/escalation/dedup key). Detail optional scoped pilot. **Pilot protocol**: one real low-risk idea→GTM + held-out set (fixes/UI/docs); GitHub and GitLab independently; metrics = failures/interventions/rework/cost/latency/founder review time — never PR counts; baseline vs candidate on matched tasks; model fixed when measuring harness changes; no simulated success; founders explicitly accept/revise/stop v1.
- **Phase 6 — Coffee surface (later, as agreed)**: intake from tasks/docks; **reviews happen inside Coffee with the recording attached** (evidence package + recording + one-line summary posted to the task card; founder approves from the card); approvals notified + decided inside Coffee (silence never approves); meetings → decision extracts → action items → work items; Chat Coffee AI as harness (Coffee-created + BYO runners, same contract); GTM handoff for `t_ad1743f9` (EXTRACT → STORY → MAKE → PROVE → SHIP → LEARN; Gates A/B; same recording artifacts satisfy Review — SF-07). Coffee OAuth is staged (client credentials saved; exchange pending one consent).
- **Optional design station** (OpenDesign-style): when brand fidelity/design-production cost becomes real — GTM assets (decks, prototypes, HTML video, images) in MAKE/SHIP; daemon for brand extraction or server-side skill runtime. Until then: DESIGN.md + Review check, zero dependencies.

**Explicit v1 non-goals:** no Missions/fleet parallelism (factory.ai sense); no Graphify/Detail in production (pilots only); no org-wide catalogs/fleet migrations (Spotify scale); no 1,000-tool ecosystems; no HMAC gateway + service task DB in v1 (v2, when multi-venture/Coffee demand); no Coffee UI changes in this repo; no autonomous merge/deploy/release ever (human gates).

---

## 9. Requirements (condensed; evidence map: `docs/provenance.md`; full narrative kept in the internal research archive)

- **A. Coffee surface** (later; P0 when wired): A1 capability matrix (docks/tasks/kanban/chat-AI/agents/projects/files/recordings/meetings/skills/notifications/approvals — existing/untested/adapter-required/missing) · A2 authenticated task+file round trip · A3 approval loop: propose → Coffee notification to named founder → binding decision recorded → read back; silence never approves · A4 work intake from task/dock; status/steer visible; pause/steer/resume mid-run · A5 meetings→transcript→action items→work items with provenance (meeting/recording/task IDs).
- **B. Factory core** (seed P0): B1 versioned envelopes (task/run/action-intent/action-receipt/approval/evidence-package/context-bundle/release/learning-proposal; Coffee IDs reused, no second task DB) · B2 idempotency + ordering (no duplicated work or terminal regression; read-back recovery, never blind resubmit; ambiguous non-idempotent actions stop for review) · B3 pipeline & acceptance criteria (as §7.3) · B4 budget/cost accounting + harness routing (as Phase 3) · B5 context hygiene (packs pre-compile; auto-compaction threshold; cache TTL per workload; bounded tool surface search-then-mount) · B6 owner-curated context packs (provenance; founder corrections supersede) · B7 factory brain (persistent run-level notes; Pod lessons + factory notes; not raw history) · B8 feature-recording evidence (as §7).
- **C. Delivery**: C1 provider-neutral ChangeRequest, independent impls, pinned GitLab · C2 same scenario both providers ending in verified merge + read-back SHA · C3 safety (protected branches; no self-approval; factory branches only auto-fixed; webhook auth+dedup; reconciliation reads; native rules stay additional) · C4 release gate machine (conditions → auto-advance non-judgment steps; founder signoff at Review (evidence) and Gate B (deploy), legal gate conditional; rollback only under approved runbook; release identity/environment/smoke/rollback evidence read back).
- **D. Agents**: D1 Coffee-created + BYO runner complete the same contract; advertised status/cancel/artifacts/capabilities · D2 verification separation (reviewer sees spec+real diff+evidence; self-reports never proof; failed checks can't be rewritten; each station's evidence applies/passes/fails/not-applicable-with-reason) · D3 sandbox isolation; no prod creds in untrusted builds; no privileged token in workers.
- **E. Context**: E1 same approved context across authorized agents with provenance; revoked-scope/cache returns nothing forbidden; restart/replay no duplicate observations; deletion propagates · E2 lessons loop with founder amend/delete · E3 firewall semantics (explicit scoped sharing; private-by-default for sensitive domains; cross-venture promotion = founder action) · E4 governance record per session (agent/requester/data/changed — queryable a year later, no redoing work) · E5 Graphify A/B (same model/tasks/revision; metrics incl. index cost, accepted quality, stale/missed relations, latency, reviewer time; graph falls back to search; inferred ≠ proof).
- **F. Feedback**: F1 monitoring + support → one deduped work item (repro/severity/SHA/evidence); regression before/after; alert owner/escalation/dedup key · F2 Detail pilot (scoped; reproducible findings, false positives, accepted fixes, cost/confirmed bug; retention/isolation review first) · F3 pilot protocol (as Phase 5) · F4 founders see cost/latency telemetry (statusline-style); 6-term equation is the unit of conversation.
- **G. Evolution**: G1 versioned proposal → held-out eval → approval → canary → rollback for any workflow/skill/context/routing change · G2 contracts versioned; migrations follow G1 · G3 continuous improvement loop (correction → auto-drafted SkillProposal; repeated workflow → auto benchmark with tracked score; first-try-wins prompts copied into skills; v1 seed = lessons loop) · G4 providers swappable; routing config; sovereign options allowed.

---

## 10. Status — what exists vs not

**Exists today:** `techno-factory` scaffold (v0 tracer: work intake, HMAC signing, SQLite, MCP+HTTP adapters, risk tiers, docs — **zero commits, uncommitted**); Pod + Smartware repos (memory substrate, approvals, agent registry, meetings adapter); the OS shell (voice push-to-talk, modules registry); research package (`docs/provenance.md`, `docs/setup-plan.md`, `docs/system-delineation-and-seed.md`, SF-01…SF-10 backlog); Coffee MCP OAuth client credentials (client_id+secret stored; access token pending one-time consent — **Coffee integration deferred by founder decision**).

**Not built:** any pipeline code beyond the v0 tracer; station role configs; factory skills repo; Sandcastle wiring; Review (incl. recording capture); GitHub/GitLab adapters beyond scope notes; qualification script; kanban cards (RF-01…RF-07 drafted in docs, not on the Venture Factory board — board write pending Coffee auth); GitLab parity work; evaluation harness; Pod wiring.

**Fleet caveat (ops):** Deployment-side provider credentials are stale (401s; tooling quota spent) while the desktop app still works — ops should rotate provider keys before the first run; this will bite any agent run on outside the desktop app.

---

## 11. Open decisions (founders + reviewers)

1. ~~Pilot venture repo + risk-tier appetite~~ — **resolved: own repo (Pod or another trusted internal repo) for the seed; venture repo for Phase 5 pilot.**
2. Agent platform mix (which harness(es); Sandcastle defaults to Claude Code; cloud vs local split per job type).
3. Model providers to route between (cheap + strong; validator family ≠ implementer family).
4. ~~GitLab instance/version/tier to pin~~ — **deferred: GitLab is a trigger, not v1 work (GitHub is the house provider).**
5. Credential vault choice for the broker pattern + worker-token broker details.
6. ~~Station-chain right-sizing~~ — **resolved (second review): Plan → Build → Test + Review check; Triage inside Planner; Supervisor/Adversary conditional/unbuilt.**
7. ~~Review recording strictness~~ — **resolved: automatic capture from E2E harness; fail only on required-but-unproducible.**
8. ~~Seed repo choice~~ — **resolved: own repo first.**
9. **Named operator-owner for the factory itself** (who fixes it at 11pm mid-run; with two people the failure mode is the factory becoming an unmaintained dependency neither of you owns). Proposed default: the founder; backup: the second operator.
10. **Refresh stale deployment provider credentials before run 1** (401s; tooling quota spent) — ops prereq, blocks nothing else.
11. **Hard spend ceiling number** (one number; default proposal: e.g. monthly $ cap such that two founders monitor it casually).

---

## 13. Second review (external, Sep 07 2026) — verdict & adjudication

External verdict: *"strong research and a weak plan… you have two people."* Adjudication, item by item:

**Adopted outright:** cut 7 of 10 envelopes (task, evidence package, approval remain; the rest become fields when a consumer exists) · collapse R0–R4 × T1–T5 to one binary ("touches production/credentials/protected branches/money? human decides; third tier only when a real run names one") · no qualification rubric (manual 20-min fix, once, is the qualification) · GitLab + cost engineering out of v1 (triggers; passive cost measurement; single model-per-station config only) · Grill Me / ubiquitous language / Adversary conditional or deferred · **WIP cap = 3 concurrent runs, system constraint** · **monthly spend ceiling with automatic halt** (kill switch armed from run 1) · **Review mechanical diff-integrity scan (blocking)** — long-line heuristic + `atob(` / `eval("global.` / `global.[a-z]='<digits>-` signatures, plus worker-token broker (no npm publish token, no repo-scoped GH CLI token) · named operator-owner for the factory · rotate stale provider keys before run 1 · chain = Plan → Build → Test, Review = check not station, Triage absorbed.

**Held with modification:**
- **Standard of completion** — cut as an artifact, kept as a mechanism: the evidence (Factory 36%→90%) buys the *checklist-authored-before-implementation and applied verbatim by the tester*, which is now literally the Planner contract. Different noun, same substance.
- **Baseline comparator** — no evaluation harness, agreed; but one cheap comparator survives (single-agent arm or alternating weeks) because intervention counts without a reference point are not a decision.

**The lesson we take over the method:** the doc's §5 vocabulary is inherited; §10's zero-commits vs §9's ~40 requirements was the tell. The revision now starts from the headcount (two people), and §5's ideas are *names*, not commitments.

---

## 14. Internal review (Sep 2026) — verdict & adopted changes

The internal review ran against this document (independent reviewer, Head of Technology persona). Verdict: *"The doc is genuinely good, arguably over-built for a v1."* Its five answers, and what we adopt:

**Defining question (reviewer):** the load-bearing claim is *not* the station chain — it's whether a multi-station loop produces a correct, mergeable, evidence-backed change a single capable agent wouldn't, at an affordable cost. Three facts must hold: (1) the tester (independent model family, real diff + real test output) actually catches what the builder got wrong; (2) the evidence record is tamper-evident and the human gate unconditional — an unattended run can never become a shipped lie; (3) the whole thing is cheaper in intervention + founder judgment than a good engineer. Fastest honest way: run the seed AND a single-strong-agent baseline on the same bounded feature, model held constant, decide on rescue/intervention/cost/latency/founder-review-time.

**Adopted changes (deltas to this document):**
1. **Baseline arm becomes part of the seed** (new, replaces "one bounded feature" tacit test): chain vs one capable agent, model held constant, same repo — the seed's real deliverable is whether the chain beats one good agent. Do not ship the architecture on a live venture repo before that's settled.
2. **Station chain right-sized down**: v1 default = **Triage → Plan → Build → Test → Gate**. Supervisor and Adversary are **conditional stations** (long/risky/ambiguous and R3+/critical respectively) — zero measured evidence makes them defaults. (Matches our own open decision #6; recorded as resolved.)
3. **B8 recording: automated-or-warn, not always-fail** — capture automatically from the E2E harness on every UI run (marginal cost ≈ 0); Review fails only when a required recording was required but could not be produced; warn otherwise. The recording still lands on the review card — the user's intent is preserved, the failure mode softened.
4. **Repo qualification = 20-minute pre-flight check, not a phase** (Red-no-runs stays).
5. **Cost + founder-review-time measured passively from run 1** — "don't optimize cost" ≠ "don't measure cost"; the baseline needs it.
6. **Sandbox egress restriction** (not just non-root + no prod creds): dependency-fetch prompt injection is a real surface; network policies must enforce "external input is untrusted" in the sandbox; tester and builder both sandboxed, network pin + allowlist where needed.
7. **Cut from v1**: routing engine / 6-term cost equation (Phase 3; keep a single model-per-station config file); ubiquitous-language doc (defer; one more artifact to maintain); Pod context-pack + lessons integration (defer — seed runs on plain repo files + DESIGN.md); single delivery provider in v1.
8. **Added**: red-green TDD as the acceptance-authoring step (define the bounded feature by a failing test first — tester gets an objective check, not model opinion); per-run abort path + max-token/max-cost circuit breaker (no runaway unattended runs; founder has mid-run stop).
9. **Seed repo choice**: pilot on **our own repo** (Pod or another trusted internal repo) — controlled, understood, no users at risk — and keep the real-venture repo for the Phase 5 pilot.

**Reviewer dissent kept as-is (recorded, not adopted):** "pick our own repo" — adopted. Everything else on the list above adopted. The one place the reviewer was softer than this doc's evidence (Bello +9% on messy specs for runtime-only supervision) is handled by making Supervisor conditional rather than removed — consistent with both.

---

## 15. Sources

Uber X Article 2090828118454071296 / uber.com blog · engineering.atspotify.com (Portal modes 9/2026, Code-with-Claude 6/2026, Data Assistant 6/2026, Multi-agent ads 2/2026, Release Part 2 2/2026) · vercel-labs/eve-software-factory-template README + docs + agent/ + evals/ code · factory.com/news/software-factory (6/2026) + what-it-takes-for-coding-agents-to-complete-large-software-tasks (8/2026) + model-routing-belongs-in-the-harness (8/2026) · Makson179/Bello README v0.5.1 · Ryan Carson (Greg Isenberg interview via The Neuron 7/2026; ryancarson.com/videos) · mattpocock/sandcastle + AI Engineer talk · multiplayer-ai.com manifesto · detail.dev · graphify.com · open-design.ai (nexu-io/open-design, verified: 94,539 stars, Apache-2.0, pushed daily) · Techno Ventures Autonomous Dev Handbook (March 2026) · Pod docs (README, staging integration, experience-loop, smartware-authority) · Coffee MCP OAuth notes (verified live 2026-08-28) · our techno-factory docs (architecture.md, api-v0.md, provenance.md, setup-plan.md, system-delineation-and-seed.md).
