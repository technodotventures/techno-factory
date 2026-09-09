# Techno Software Factory — Research Map & Key Requirements (v1)

Status: research phase deliverable, Sep 07 2026. Companion to `docs/architecture.md` (v0 tracer) and the implementation backlog (`SF-01…SF-10`). This document adds the research consensus and the v1 requirement set; the SF backlog remains the build-order plan and is extended below where research changes it.

Purpose: define a proprietary software factory for Techno Ventures that wraps Coffee's existing features (docks, tasks, Kanban, Chat Coffee AI agent harness, projects, files, recordings, meetings → tasks, skills) plus Smartware/Pod as the multiplayer context substrate — simple enough for v1 to ship, architected to evolve (idea → GTM → feedback → more capable).

---

## 1. Reference review — what each source teaches us

### 1.1 Uber — "Running a Software Factory Efficiently at Uber Scale" (Aug 2026, primary: X article by @udaykiran via @UberEng; full extraction on file)

Verified numbers: 70%+ of PRs attributed to local/cloud agents; 3,600+ agent skills across the SDLC; 30K+ skill executions/day; weekly active users ×7 and agentic requests ×9.4 from Feb→Aug while total AI spend was stable since April; cost per 1K requests −34% from peak; cost per session −52% from June peak (model held constant).

The 6-term cost equation (their Figure 4): `total spend = users × sessions/user × turns/session × requests/turn × tokens/request × price/token`. Terms 1–2 should GROW (adoption); terms 3–5 are the optimization budget; term 6 is vendor-set but *routing* is ours.

Levers (their magnitudes, portable methodology):
1. **Subagent default model** — highest-impact lever: top model decomposes/evaluates, cheap model executes.
2. **Context hygiene** — auto-compaction at 400K tokens even for 1M-window models; reasoning effort Medium; tiny summaries post-code-mode.
3. **Cache TTL per workload** — reads 0.1× input rate; 5-min TTL write premium 1.25× vs 1-h 2×; interactive = 1h, subagents = 5min.
4. **Tool gateway** — 1,000+ MCP servers projected as CLI commands, search-then-mount. Standard MCP preload ≈ 50–70K tokens (100+ tools) re-sent every turn; SaaS bundles 22K/49 tools. Code-mode measured: 1 turn / ~400 tokens vs 3–7 turns / up to 1.43M tokens.
5. **Grounded context graph** — 24M nodes / 80M edges / 86 node types / 117 edge types across 30+ systems; NL queries. Grounded: 38s correct. Ungrounded: 20 min, 3 errors, wrong conclusion.
6. **Governance** — statusline live cost counter; shared harness spend tier + managed-agent tiers; Slack nudges at 50/80/100% of expected spend; manager approval for tier upgrades; 16 anti-patterns in session dashboard; fleet of managed agents (uReview review, self-healing CI, on-call triage, bug debugging, maintenance) with human reviews/escalations.

Methodology to copy: benchmarks built FROM REAL WORK, graded easy/medium/hard; Pareto frontier per workload (precision/recall/F1 + cost + latency); one harness serving any model; hold the model fixed when measuring our own changes. Their quote: *"the methodology of benchmarking real work and optimizing for accuracy and cost is universally applicable."*

DO NOT copy (scale artifacts): 1,000+ MCP servers, 24M-node graph, bespoke internal platform, 3,600 skills. Harvest primitives, not the platform. Their roadmap (maturity timeline for us): managed-agent fleet metrics → dynamic model routing → deeper context-graph integration → real-time trace monitoring → auto-mining "papercuts" to generate skill updates.

### 1.2 Spotify — best practices (primary source: engineering.atspotify.com; note: the linked X post was actually an Uber summary; the real Spotify sources are the engineering blog)

- **Adoption**: 99% of engineers use AI coding tools weekly; 94% report higher productivity; **+76% PR frequency** — and the constraint moves from coding to **human decision-making** (more PRs to review → review triage, auto-merge safe changes, focus judgment where it matters).
- **Fleet Management / Fleetshift**: years of deterministic automation across thousands of components; **2.5M+ automated maintenance PRs merged, vast majority auto-merged** (no human in loop); cross-service Java migration took 3 days vs weeks/months. For us: the migration/fix pattern is the "factory floor" work, not feature work.
- **Honk (background coding agent)**: Claude Agent SDK in Spotify's own harness, many parallel sessions on k8s, trusted tools including **running builds in CI across OSes to verify its own changes**; available over Slack (mention mid-conversation → PR). v2 adds shared sessions/multiplayer + agent orchestration (Chirp). For us: factory agents run in Coffee (docks/tasks) and are triggered by Coffee context, not a new chat surface.
- **Backstage as agent context**: internal developer portal/catalog — every component's owner, docs, and services exposed to agents via **MCPs and CLI**. Agents answer "who owns this?" like humans do. (≈ our Coffee skills/swagger + Pod "who knows" expertise lookup.)
- **Golden state + Soundcheck**: recommended technologies/practices per component type; self-assessment UI; combined with static analysis/lint these become **active guardrails — "when Claude works in our codebase and uses a pattern we know isn't optimal, it gets immediate feedback from our lint and corrects itself."** This is the single most valuable transferable idea for us: encode our conventions so agents self-correct.
- **Standardization principle** ("fewer technologies we're world-leading in, the faster we go"): consistent codebases → measurably better agent performance; fragmented codebases → worse. Agents get better by having lots of consistent code to reference.
- **Vedder data-assistant context layer**: 70K+ datasets / 1.4T data points/day → clusters with (a) datasets+profiling, (b) **expert-curated Q-SQL pairs**, (c) docs. Auto-derived pairs: experts accepted **12.5%** — "query history is rich, most of it is noise, and the signal doesn't label itself." Each cluster has a health score; owners decide curation effort; every conversation feeds back. For us: **model reasoning over context — but founders/experts decide what's true.** Our context packs must be owner-curated, not auto-mined.
- **AiKA Modes (Portal, Sep 2026)**: declarative ephemeral agents ("Lambda for agents"): instructions + model + parameters + MCP tools; callable from CLI/API; public/private. The bulk-reader/code-writer pattern: hooks block expensive reads (>350 lines) → delegate to a cheap-model mode → **~90% token savings**; can't delegate editing (line-number unreliability) or reasoning (missed thread-safety bug); 10–30s latency, 30s cap. "Modes turn model routing from a systems-engineering problem into a configuration problem." → our router config, not our platform.
- **Release "Robot"**: state machine (5 states + paused/cancelled); a backend service checks conditions and advances stages; **−8h average release cycle**; dashboard aggregates ~10 systems into one decision surface (pre-aggregated every 5 min); shipping only after release gates (ITGC + signoffs). → our Gate A/B machine, conditions → auto-advance, founders only on the judgment gates.

### 1.3 Eve / Foreman (vercel-labs/eve-software-factory-template + ask-foreman.dev)

- Four stations, each its own agent/instructions/sandbox/tools: **Classifier** (triage: type/priority/complexity/actionable; asks the requester when not actionable) → **Analyst** (plan + acceptance criteria from a live checkout) → **Implementer** (executes in its own sandbox, verifies with the repo's own checks, pushes branch) → **Reviewer** (independent judgment on the real diff; **sees only the pushed branch, never the Implementer's reasoning**).
- **Factory brain**: persistent notes about the repo every run starts from (≈ Pod context packs, but scoped to the repo).
- Work arrival: label `factory`, @mention, Linear agent sessions, dev TUI (local runs untrusted — GitHub changes wait for approval), red-CI self-fix on its own branches, orienting comment on outside PRs ("a summary, not a review").
- Agent config: compaction at 75% of context window; per-session output cap 100K; model chosen per station.
- For us: the station pattern + "reviewer blind to implementer reasoning" + "verify with the repo's own checks" map directly onto our verifier requirement.

### 1.4 Factory.ai / factory.com (Factory 2.0, June 2026 — "From coding agents to software factories")

- **The loop**: signals (bug reports, conversations, feedback, requirements) → triage → planned change → build → test → review → secure → ship → monitor → more signals. "Almost no one has meaningfully instrumented this loop to be fully AI-driven."
- **Three pillars**: (1) **Model independence** + Router (choose per task, or rule/auto routers); (2) **Sovereign intelligence** (hosted/BYO-key/self-hosted/EU/air-gapped; **"owning a system that learns from itself"** — every session/review/incident feeds back and the capability stays inside the walls); (3) **Continual learning** — all SDLC stages on shared agent core/router/org context so a security finding informs review, a deployment triggers a doc update, an incident correlates with the PR that caused it.
- **Autonomy spectrum** (maturation, not all-at-once): simple Droids + skills → Automations (recurring, shared objective/memory) → Missions (multi-agent, hours–days, parallel tracks) → Droid Computers (remote persistent). Choose level by human-guidance requirement, information sensitivity, agent readiness.
- The identity shift: *"engineers own building the factories that build the software,"* with governance, safety, and business outcome ownership.
- For us: v1 sits at the Droids+Automations end; Missions (parallel multi-agent across a day) is explicitly v2+; sovereignty = our stack stays ours (Coffee + Pod + our factory, self-hosted).

### 1.5 Detail (detail.dev) — proactive bug scouting (optional v1 A/B)

Clones the repo to a secure sandbox, runs thousands of checks, sends a **PR with a fix** or a **ticket** (Linear/Jira/Asana) assignable to whoever has most context; also dead-code cleanup and internal-docs maintenance ("agents depend on skills and READMEs nobody is paying attention to"). SOC 2 Type II, zero data retention, BYO-factory. Community evidence (testimonials — treat as claims, not benchmarks): OpenRouter, Notion, Semgrep, Mastra, Amp, Vanta, Profound; OSS hits on tailscale (7 flagged/5 fixed), kubernetes-client, next.js, temporalio.
For us: feedback-loop node, not runtime observability. v1 = basic monitoring + dedup to Coffee tasks; Detail = optional pilot on a scoped repo.

### 1.6 Graphify (graphify.com) — context substrate option

On-device; one run of `/graphify .` → `graph.json` + `GRAPH_REPORT.md` + `graph.html` (graph, god nodes, communities); provenance-tagged edges (extracted/inferred/ambiguous) — answers are auditable **paths**, not similarity vibes; works in 17 assistants + MCP server; Apache 2.0; Karpathy "LLM wiki" lineage. Community claims of 71–79× token reduction (reports, not verified by us — treat as claims).
For us: matches our mission ("did this actually happen? / what path proves this?"). v1: context packs via Pod compile; v2: A/B graph-assisted retrieval vs canonical search, same model, same tasks.

### 1.7 Coffee + Pod (our existing ecosystem — decided implementation context)

- **Coffee** (metcoffee.ai; our workspace) is the collaborative human/team surface. Verified surface (Aug 2026 probe): Streamable-HTTP MCP at `/api/mcp` with OAuth 2.0 dynamic client registration + PKCE (S256; loopback redirect; full scopes; apex-host resource binding exact-match; consent screen marks self-registered clients "unverified"; token endpoint `/api/v1/oauth/authorize/code`; errors are `{success:false, errors:[...]}` shaped; 429-backs off). Features per product: docks, tasks, Kanban boards, Chat Coffee AI (agent harness; create/bring agents), projects (house documents + tasks), files (storage/sharing), recordings (screen recordings shareable to agents), meetings (agent-attended, recorded, transcribed, **action items auto-created as tasks**), skills storage, notifications/approvals surfaced here.
- **Pod (Smartware runtime)**: standalone user-owned memory companion; same object store + memory/event layer; generic HTTP + MCP surfaces. Key routes: collections/objects, `observe`, `query`, `context` (bounded peer cards + lessons + conversations + cited claims), `expertise` (evidence-backed "who knows"), `compile`, `dream` (owner-triggered maintenance), sessions (`start/checkpoint/end`), **agent action `propose/approve/reject`** (approval binding), agent registry with **portable profiles** (Hermes/Codex/Claude Code/OpenClaw/Kimi, no token exports, preview + rolled-back imports), experience loop (`pod_record_experience` → derived cited lessons), Coffee adapter (`/coffee/connect` → bound client tokens; `/coffee/sync/meetings`, `/coffee/meetings/:id/brief`, `/coffee/meetings/:id/capture` — notes/decisions/tasks/followups; **follow-ups are drafts requiring human approval before any external write**; owner-only endpoints; `GET /pod/approvals`).
- **Our v0 (techno-factory)**: typed work envelope (org/workspace/project/thread/actor/agent/origin/correlation/idempotency), idempotent submission (201/200/409), HMAC auth with 5-min window + persisted nonces + project grants, risk tiers R0–R4, HTTP + MCP adapters over ONE application service, authority v0 = accept work + read-only audit, no execution/publish/merge/release. Boundaries: Coffee = authoritative collaborative surface; personal agent surface separate; promotion across boundaries only explicit; secrecy never in repo.

### 1.8 Multiplayer AI Manifesto (multiplayer-ai.com, Sep 2026)

A "North Star" for true multiplayer AI — no vendor satisfies all five today. It is the best statement of why Coffee (open work surface) + Pod (shared context substrate) is the right shape:

1. **Never copy-and-paste** — agents live next to the work; everyone involved chats with the SAME agent; agents use every tool a human uses. (We: agents live on Coffee docks/tasks; context via Pod, not screenshots/links of transcripts.)
2. **Work with the door open** — shared sessions spread best practices fast; Shopify's River is public-Slack-only and reached ~1-in-8 PRs co-authored within a month ("learning on the shop floor"); HBS field experiment (776 professionals): team + AI achieved 15.1% top-10% solutions vs 5.1% individual-no-AI, 8.7% team-no-AI, 7.7% individual+AI. (We: run sessions on shared surfaces by default; private by exception, not rule.)
3. **Continuously improve** — a great prompt teaches others; a correction auto-creates a reusable skill; a repeated workflow auto-tracks a benchmark (week-1/5/9 team-performance curves). (We: Pod lessons loop today; auto skill-proposal + auto benchmark from repeats = v2 requirement G3.)
4. **People are not routers** — never ask a human a question an agent can already answer; chasing updates and relaying = agent work; humans keep judgments. (We: approval gates are only for actions/decisions that need a founder — the factory does the chasing and reporting, per our founder-in-loop design.)
5. **Nothing starts from scratch** — cloud sessions resume months later; every artifact (doc/plan/PR) has a resumable agent session; a new teammate is productive day 1. (We: Pod sessions + context packs + Coffee artifact links; milestone/resume as v2.)

Hard considerations that become requirements: **agents don't belong on laptops** (agent runs happen server-side); **firewall every agent** (scoped sharing — Dana's inbox isn't repeatable to Marcus; she must share explicitly — exactly our Pod actor/scope model); **stay provider-agnostic** (model shifts weekly; one-provider alignment = that provider's billing incentives; e.g. Uber burned its 2026 AI budget in 4 months on Claude Code — our router config, sovereign models); **governance is non-negotiable** (4 questions about any session a year later: which agent ran, who asked, what data touched, what it changed — audit black box); **own your data** (learnings, skills, evals stay ours).

### 1.9 Factory Research — executable standard of completion + harness routing (Aug 2026)

Two primary research posts that change requirements, not just inspiration:

**"What it Takes for Coding Agents to Complete Large Software Tasks"** (Factory Research + Theo Luan, Aug 27 2026; 24 hardest ProgramBench tasks, 3 models, single-agent vs orchestrator/implementer/validator system):
- The failure mode: requirements state what must be true — they don't measure whether the work achieves it. An agent decomposes, validates each piece in the context that produced it, then "decides it was done." Every local judgment can be reasonable while parts of the whole stay unmeasured. GDAL single-agent: solid 17K lines of C++, **36% behavioral parity** — it did not run out of time or budget, it stopped because by its own assessment it was done.
- The fix: an **executable standard of completion (SOC) authored before implementation** — an inventory of what must be established + procedures for establishing each part + current evidence those procedures pass. Held to it: same model, same budget class → **90% parity, 115K lines**; 7-Zip 54→95%, DuckDB 34→80%, system held the upper 90s on many tasks; per-task frontier gains +2 to +48 points. System spend on gdal: implementer 97%, validator 2%, orchestrator 1%.
- **"The single agent didn't lack skill. It lacked a standard of completion."** The SOC must be derived from the outcome BEFORE implementation narrows attention, must stay current ("it must not quietly collapse around whatever has already been built"), and may be refined as the system learns. Human teams rarely do this because the conformance-suite cost is per-project; agents change the tradeoff because they also can maintain the standard.
- Caveat: one run per cell, no variance estimates; system runs cost 13× wall time and ~14× credits — the standard pays off in completeness, not speed/cost.

**"Why model routing must be in the harness"** (Abhay Singhal, Aug 24 2026):
- Production result: routing in the harness cut aggregate cost **58%** vs frontier-for-every-call (median session −76%, 9/10 sessions ≥50%) while matching frontier on eight production quality measures; median turn latency 81s→49s.
- Why the harness and not the gateway: a gateway sees a request; the harness owns task state — what happened, the warm cache, what a switch costs, how much work remains. **Cache blindness is the killer**: a cache-blind gateway's switching can cost 2.12–2.37× an all-frontier baseline (turns 61–200) while cache-aware routing sits at 0.19–0.28×; "staying put is itself a routing decision"; the same switch can be cheap at turn 5 and expensive at turn 90 (cache expiry, compaction). Model-family switches also discard encrypted reasoning content and rebuild prompt/tool interfaces — another reason the choice belongs where the request is built.
- The right model moves with the work (flaky-test: efficient model explores, frontier diagnoses the race, efficient finishes). Jobs: harness writes worker specs (purpose/prerequisites/completion conditions) + model per job; reviewers are separate jobs and **Factory's default validator comes from a different model family than the implementer** ("a useful validator should fail where the model it reviews does not").
- Routing records (session state at choice + model + result) refine policy; outcomes tighten the credit link — a worker passes/fails against its own completion conditions, so each result attaches to fewer model choices. Benchmarks: 99% of frontier pass rate on Terminal-Bench 2, 96% Legacy-Bench at ~20% lower cost per successful run.

### 1.10 Ryan Carson & Matt Pocock — the one-person factory in practice (Jul–Aug 2026)

Both are solo/harness-first operators, and their shared lesson is about the loop, not the platform. Primary sources: Ryan Carson's Greg Isenberg interview (via The Neuron explainer + ryancarson.com/videos, and "Untangle" $20K-agent-press reporting) and Matt Pocock's Sandcastle repo + AI Engineer talk.

**Ryan Carson (Untangle: 22–25 PRs/day average, ~40 peak; 5–10 parallel cloud agents):**
- Thesis: "The biggest AI coding gains now come from redesigning the development system around agents, rather than finding a smarter prompt." — "The 50x came from leaving the laptop, not from better prompts." His earlier 3-local-checkouts setup became the ceiling; cloud isolated envs per task unlocked 5–10 concurrent agents.
- The loop: **one task, one agent, one isolated environment** → the agent returns a PR with *evidence* (test output, screenshots, explanation, remaining uncertainty) — "finish with evidence, rather than a cheerful claim" → human reviews and decides ("Decide, don't code"; 10–20 decisions by lunch; reviewing makes the manager MORE technical) → merge / redirect / reject → next job. Judgment is the scarce resource, typing is cheap.
- Keeping 10 agents from eating his brain: pin only the work that must move today; sweep pinned threads on a ~25-minute cadence; phone as a control surface; priorities on a paper to-do outside the agent interface; ship the work that survives review.
- Three automations that replaced daily-meeting reviews (all async, all compress to a human-reviewable summary): **(1) recurring end-to-end signup test** (browser agent, 3×/week, ~$60/run, catches what unit tests can't: visible buttons, real journeys) → on failure: triage agent → reproduce → fix → re-run → PR → report; **(2) production watchdog** (9am daily: yesterday's customer events → what happened / what deserves attention / where to inspect / which issue should become a task, deep-linked into the production UI); **(3) self-improvement loop** (grade yesterday's conversations against a rubric → rank failures → child agents prepare ~3 fixes/day for review). The rubric is the load-bearing part — an explicit definition of quality.
- Security: prod write creds live in a vault, never permanently exposed to agents; retrieved manually per session to create "an intentional moment" — *"Agents should not quietly inherit the power to alter production"*; short-lived creds, least privilege, read-only where possible, separate environments, human approval for destructive actions, audit logs, allowlists, isolated envs; and external inputs (support tickets, issues, chats) are treated as untrusted instructions.
- **Cost**: a ~$20K/month token bill was "the wake-up call" that forced model routing: *route by task, not by habit* — cheap models for high-volume loops (~$5/session), strong models for architecture/ambiguous bugs/migrations/planning, premium as the parent that scopes and delegates, independent platforms to route across providers; estimate ~$5K/employee/month for serious AI engineering.
- **"The expensive mistake would be building Carson's entire factory before you have enough work to feed it. Start with the bottleneck you actually have."** — i.e. our "v1 simple" instinct is echoed by the best-documented solo factory.
- Honest counterarguments (recorded in the same article): 20 weak changes can create more work than one correct decision; parallel agents can produce subtly incompatible interpretations; METR's 2025 RCT (19% slower despite belief of speedup), 2026 meta-analysis (moderate positive, smaller in OSS/enterprise). → Fortifies our decision to measure real outcomes and founder review time, never count PRs.

**Matt Pocock (Sandcastle + "Software Fundamentals Matter More Than Ever"):**
- **Sandcastle** (MIT, 7.9k stars, TS): `sandcastle.run()` — sandboxed agent orchestration with a configurable branch strategy, commits merged back; providers: Docker, Podman, Vercel (Firecracker microVMs), custom (bind-mount / isolated); host+sandbox hooks (onWorktreeReady, onSandboxReady — setup, installs, sudo as needed); non-root agent user; per-repo `.sandcastle/` config, `.agents/` skills, `.out-of-scope` (→ **ADOPTED** as per-ticket `out_of_scope` in the WorkItem contract — scan-only before Sep 09 2026, see PLAN §2), `plans/`; provider-agnostic CLI agents (Claude Code by default). His own repo literally runs a "factory" layout (`.factory/`, `.agents/skills/pre-release`, `plans/pi-session-samples`, `ideas/`, `research/`).
- **The talk** (Counter to specs-to-code): repeated generation without design maintenance produces progressively worse implementations — complexity/software entropy (Ousterhout). Practical rules: (1) establish a **design concept first** — a "Grill Me" skill where the AI interviews the developer on the plan (dozens → up to 100 questions, exploring branches, resolving dependencies) BEFORE any PRD/issues; he finds Claude Code's plan mode too eager; (2) give the model the codebase's **ubiquitous language** (DDD) — scan the codebase for terminology → a shared-terms doc that both humans and AI consult; improves planning, cuts verbose reasoning; (3) **fast feedback**: static types + browser access + tests + TDD small steps ("implementation can move faster than feedback can guide it"); (4) **deep modules** with simple interfaces and **gray-box delegation** — humans design and own interfaces, delegate implementation inside them, keep closer oversight of critical areas (e.g. financial); (5) human **strategic ownership** of system design, with modules/interfaces explicit in PRDs.

**What changes for us (verdict on repo shape):**
- Keep: the contracts (WorkItem/Run/Evidence/Approval/Release envelopes, risk tiers R0–R4, human gates, pod/coffee adapters later) — those are the differentiator nobody above ships.
- Reshape: execution layer on proven primitives — **Sandcastle for the sandbox runner** (branch strategy, hooks, providers) instead of hand-rolled worktree/sandbox code; v1 intake = per-repo `.factory/` config + CLI, NOT the bespoke HMAC gateway (demote gateway+service task DB to v2, when multi-venture/Coffee demand justifies it); Planner gains **Grill-Me + ubiquitous-language steps** for design-sensitive work; guardrails = types/lint/tests **+ browser E2E** feedback; Phase-5 feedback loop = Carson's three automations (E2E walkthrough, production watchdog, rubric-based improvement loop); security adds the vault-broker + "external input is untrusted" rule.
- Do NOT: build the full factory before there's a single live venture repo feeding it. Start with the bottleneck we actually have.

### 1.11 Eve's actual `agent/` code + Bello — implementation patterns worth lifting (Sep 2026)

The eve README tells half the story; the code and subagent instructions carry the other half (fetched from `agent/` + `evals/` of vercel-labs/eve-software-factory-template, MIT). Bello (Makson179/Bello, MIT, Python, Codex app-server transport) is a working reference implementation of supervised coding runs.

**Eve `agent/` — what to lift, verbatim-style:**
- **One file for all model assignments** (`lib/models.ts`): every station reads `MODELS.<agent>`; ids are gateway strings, no provider SDKs wired in. **Implementer gets the strongest coding model; Reviewer is a different VENDOR on purpose (independent review)** — echoes Factory's family≠family rule. Or this becomes our Phase 3 routing config.
- **Trust is decided once, at dispatch** (`lib/trust.ts`): stamped on the signed webhook (`author_association` OWNER/MEMBER/COLLABORATOR); *"Nothing downstream re-derives trust from model-readable content."* Unattended runs run as a fixed service principal (`github:foreman-factory`) that can never collide with a real actor, stamped with the intake issue number at dispatch (never from model input) so injected instructions can't make it comment elsewhere.
- **Approval policy taxonomy**: `denied` vs `not-applicable` vs `user-approval`, applied per action class. For unattended runs, **deny rather than park** — nobody is watching an autonomous turn, so an approval card would strand the session forever; a server-side denial resolves instantly. Ship (marking a PR ready) is the human gate: parks for every human, denied for autonomous. Draft PRs run (they can't merge). The **factory brain can't be written by unattended runs — "a labeled issue's body is untrusted input that must not be able to poison the shared brain"** (matching our B6 owner-curated rule, with an enforcement mechanism).
- **Factory brain mechanics** (`lib/factory-brain.ts`): 40K character bound ("short curated durable notes, not a transcript"), keyed by a hash of the target repo (scoped per codebase, no raw owner/repo in paths), read/write under a **reserved namespace** so general-purpose blob tools can't side-channel read or overwrite it.
- **Sandbox pitfall**: `git safe.directory` must be set in the sandbox (`onSession` hook) because the sandbox FS is owned by the builder uid, not the session user — without it, every git command aborts with "dubious ownership" and the turn silently runs with no working tree. Same hazard applies to any sandcastle-based runner — put the hook in the config early.
- **Subagent instruction contracts** (the concrete station specs we should copy the shape of):
  - *Analyst*: plan grounded in a live checkout (name only files that exist; record the repo's own lint/typecheck/test commands, package manager, style); produce problem_statement / approach + the rejected alternative / ordered independently-verifiable steps / affected_surface with public contracts flagged / risks / **acceptance_criteria as an objective checklist the reviewer uses verbatim** / test_strategy / assumptions / open_questions / artifact_id. Structured plan = the contract; depth goes to an artifact.
  - *Implementer*: branch `factory/<type>-<slug>`; revision runs must address EVERY finding (fix or record a deviation and why); never silently change the approach; record exactly what checks ran and what they produced; could-not-verify → say so; never configure git identity or pass `--author` (fixed factory identity); no questions mid-run — narrowest reasonable choice + `deviations`, or stop with `pushed: false` + `known_limitations`.
  - *Reviewer*: fresh eyes, never fixes ("you produce findings"); review with `git diff` on the real diff, never the summary; **re-run the fastest checks — distrust "it should work," look for actual output**; review order correctness → acceptance criteria (per-criterion pass/fail with evidence) → safety → scope (unrelated changes, deviations) → verification adequacy → quality (advisory only); verdicts `approve` / `request_changes` (specific, actionable, traceable to correctness/AC/safety/scope) / `reject` (approach wrong; explain what was misunderstood).
  - *Classifier*: type/priority/complexity/affected_area/actionable/needs_clarification with specific questions; text-only (no repo access); decisive with noted assumptions; ask only when building the wrong thing is a real risk.
- **Skills**: `triaging-issues` (dedupe FIRST searching open AND closed issues with multiple wordings; duplicate = same underlying cause not same symptom; label with the repo's own vocabulary only, fewest labels; ask-or-proceed defaults to proceed when intent is clear; close only confirmed dup/already-fixed/off-topic/spam with a comment explaining; repro-request = engagement line + smallest actionable list + specific questions + what happens next; **never take a triage action on an issue nobody asked you about**); `writing-quality` (kill AI tells, plain English, front-load, concrete, match voice) and `github-linear-bridging` (one clear issue per issue, backlinks both ways, mirror only meaningful state — not labels/comments) map to our GTM/prose quality and to Coffee↔GitHub bridging later.
- **Evals covered** (`evals/`): routing (classifier-first, labels-follow-classification, needs-clarification) and safety (no-direct-push-to-main, prompt-injection, factory-brain-write-parks/denied, ship-gate-approve-resume, write-requires-approval, read-only-question). Its safety evals are the shape of our D2/E4 contract tests; the injection tests belong in trial Phase 1 gating.

**Bello (Makson179/Bello) — role decomposition with measured numbers:**
- Loop: **build → supervise → review → attack → repair → accept**; roles = coder (disposable sandbox, no access to original workspace), **runtime supervisor** (watches the live run: catches hallucinations/drift, blocks dangerous actions BEFORE they reach project/production, restarts a failing generation without losing the workspace), **completion reviewer** (fresh context; checks whether requested behavior is actually present with evidence; confirmed gaps → coder), **adversary** (gets the finished artifact WITHOUT the dev history, tries to break it via edge cases/invalid input/feature interactions; a separate controller checks findings before they reach the coder). Every role gets its own model AND reasoning level; review/adversary pass counts and order configurable; configurations can be quality-first or price-first; task inspection + config recommendation built in.
- Measured results (v0.5 README, primary): 12+12 matched ProgramBench runs — best config used **66.3% less of a weekly Codex limit than Raw GPT-5.6 Sol XHigh while scoring 1.45% higher**; the same benchmark says 2.966× consumption and +1.45% avg for the balanced config; the deeper/quality config scored **+36.4% vs Raw Codex** across nine matched runs; on three deliberately messy/contradictory specs, **runtime-only supervision scored ~9% higher at the same cost and time** (long-run drift conditions). Ends with `.supervisor/FINAL_REPORT.md` (status, changed files, checks, remaining risks) — mirrors our EvidencePack shape; an advisory PLAN.md from a strong model + cheap execution config is supported.
- For us: (a) **runtime supervisor** = new station duty in v1 for long/risky runs (R2+), not just an optional extra; (b) **adversary pass** on critical paths (R3+) — findings pass through a controller before returning to the builder; (c) per-role model+reasoning config + config advisor = B4/P3 concrete form; (d) FINAL_REPORT.md shape = v1 EvidencePack; (e) caveat: Bello is Codex-specific transport (app-server JSON-RPC); we take the loop, not the adapter — Sandcastle or our executor provides ours.


---

## 2. Architecture map (v1)

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ COFFEE (meetcoffee.ai)  — human/team surface, founders in the loop       │
│  docks · tasks · Kanban · Chat Coffee AI (agents) · projects · files     │
│  recordings · meetings (agents attend, transcript → actions → tasks)     │
│  skills · notifications & approvals                                       │
└───────────────▲───────────────────────────────┬──────────────────────────┘
        approval/decision | notifications       │ work intake (task/dock/meta)
                 │                              ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ TECHNO FACTORY (techno-factory — separate private deployable)            │
│  Gateway: signed work intake · project grants · idempotency · audit      │
│  Pipeline (station agents, each own sandbox + checks + budget):          │
│   Triage → Plan(AC) → Build → Verify(blind review) → Evidence → Gate     │
│  Governance: risk tiers R0–R4 · founder gates (merge/release/deploy/     │
│    credentials/infra/governance) · budget + cost accounting              │
│  Memory-of-the-factory: context packs, lessons, run histories            │
│  Adapters: GitHub (PR/checks) · GitLab (MR/pipeline) · release targets   │
└───────────────┬───────────────────────────────┬──────────────────────────┘
                ▼                               ▼
   ┌──────────────────────────┐      ┌──────────────────────────────────┐
   │ POD / SMARTWARE          │      │ EXPRESSO (peer)                  │
   │ memory substrate:        │      │ workflow language/runtime —      │
   │ context packs, lessons,  │      │ LLM observes/decides, system     │
   │ expertise, approvals     │      │ acts; "did this actually happen?"│
   │ (bindings), agent        │      │ verification-first               │
   │ profiles, meeting sync   │      └──────────────────────────────────┘
   └───────────▲──────────────┘
               │ shared context/provenance (multiplicayer across agents)
   ┌───────────┴──────────────────────────────────────────────────────────┐
   │ RUNTIMES: Chat Coffee AI agents (in-app) · founder's personal agent ·         │
   │ external BYO runners (Coos/Codex etc.) — same WorkItem contract      │
   └──────────────────────────────────────────────────────────────────────┘
   Feedback loop: monitoring/incidents → dedup → Coffee tasks → pipeline;
   optional Detail (proactive bug scout) & Graphify (graph context) as A/B probes.
```

Ownership (unchanged from architecture.md): Coffee owns UI/team model; factory owns contracts/idempotency/adapter/policy; Pod/Smartware owns memory protocol; expresso owns workflow runtime; personal agent surface separate.

---

## 3. Key requirements (v1)

Priority: P0 = v1 must-have; P1 = v1 if cheap / v2 otherwise. Acceptance criteria are concrete and testable.

### A. Coffee surface integration (P0) — extends SF-01
- **A1** Capability matrix: for docks, tasks, Kanban boards, Chat AI/agent registration, projects, files, recordings, meetings (transcripts/action items), skills, notifications, approvals — label each surface existing/tested, existing/untested, adapter-required, or missing, with the actual MCP tool/REST endpoint, pagination, rate limits, idempotency, and retention behavior. (Probe via Coffee MCP `tools/list` + docs.)
- **A2** Authenticated round trip: create/read a task and attach a file in an approved project; read a Kanban board; read a meeting's transcript/action items.
- **A3** Approval loop: factory-proposed decision → Coffee notification to the named founder → decision recorded (approve/reject with binding fields) → read back; **silence never approves**.
- **A4** Work intake: a Coffee task (optionally on the Venture Factory board) triggers factory work; status/steer visible in Coffee; founder pause/steer/resume works mid-run.
- **A5** Meetings→tasks: a Coffee meeting attended by an agent yields transcript + action items; factory receives them as input work with provenance (meeting id, recording id, task ids).

### B. Factory core (P0) — extends SF-02/SF-03
- **B1** Versioned envelopes: WorkItem, Run, ActionIntent, ActionReceipt, ApprovalRequest/Decision, EvidencePack, ContextBundle, Release, LearningProposal. Coffee IDs are reused; no second task database.
- **B2** Idempotency + ordering: duplicate/delayed/reordered events never duplicate work or regress terminal state; crash-after-remote-success recovers via read-back, not blind resubmission; ambiguous non-idempotent actions stop for review.
- **B3** Pipeline v1: four stations (Triage/Classifier, Planner/Analyst, Builder/Implementer, independent Reviewer—blind to Builder reasoning) + evidence + Gate A. Each station: own agent config (model, budget, sandbox, tools) as data. **The Planner authors an executable Standard of Completion (SOC) — inventory of checks + evidence procedures — BEFORE implementation; SOC is versioned, kept current, and never silently collapses around what's already built** (Factory research: single-agent GDAL stopped at 36% "done"; SOC-driven reached 90%).
- **B4** Budget/cost accounting v1 (Uber lever 1+2+6; Factory harness-routing): per-run tokens/cost/limits tracked on the work item; cost equation displayed; expected-spend nudges (50/80/100%); tier upgrade → founder approval. Subagent default model = cheap; planner/routing = strong; routing is CARRIER-HARNESS config, not gateway config (cache-aware: a switch that drops the warm prefix costs 2×+ vs staying; staying put is itself a decision); **validator model family differs from implementer family**; routing records (state+model+result) are collected for policy refinement.
- **B5** Context hygiene v1 (Uber lever 2/3): context packs compiled before spawn (Pod compile); auto-compaction threshold; cache TTL policy (interactive vs subagent); tool surface bounded (search-then-mount, not full preload).
- **B6** Context packs are owner-curated (Spotify Vedder lesson: auto-derived context accepted 12.5%): pack = approved spec/decision/project links + pinned revisions + founder-approved glossary; provenance on every claim; founder corrections supersede derived content.
- **B7** Factory brain: persistent run-level notes (what's built, what's known-broken, conventions) — Pod lessons + factory notes, not raw history.
- **B8** Feature-recording evidence (UI-affecting changes): EvidencePack includes a screen recording of the feature walkthrough (happy path + one recovery path, 60–120s, steps + assertion summary) from the browser E2E run against preview/staging; Gate A auto-fails a UI change with no recording; non-UI = not-applicable-with-reason; record-on-failure only for recurring automations (cost guardrail); one artifact set feeds review, the GTM handoff (SF-07 happy/recovery recordings) and the rubric loop.

### C. Delivery adapters (P0) — SF-04
- **C1** Provider-neutral ChangeRequest with native IDs/links/statuses; GitHub (PR/checks) and GitLab (MR/pipeline) implemented **independently**, pinned GitLab deployment/version.
- **C2** Same scenario on both: draft change request → evidence → CI-failure reaction → review-feedback acceptance → verified approved merge → read-back final SHA.
- **C3** Safety: protected branches stay protected; worker never approves/merges its own output with a privileged token; only factory-owned branches receive automated fixes; webhooks authenticated + deduped; missed events reconciled by provider reads; native branch rules/code-owner reviews remain additional, unoverridden constraints.
- **C4** Release gate v1: gate conditions as a state machine (Spotify Robot pattern): conditions checked → auto-advance through non-judgment steps; founder signoff at Gate A (evidence) and Gate B (deployment), legal gate conditional; rollback under approved runbook only; release identity/environment/smoke/rollback evidence read back.

### D. Agents (P0) — SF-05
- **D1** Both a Coffee-created agent and one external/BYO runner complete the same bounded WorkItem contract; runner advertises status/cancel/artifacts/capabilities; unsupported capabilities explicit.
- **D2** Verification separation: reviewer/verifier sees approved spec + real diff + evidence; agent self-reports are never proof; failed checks cannot be rewritten as passed; "did this actually happen?" is an explicit read-back step.
- **D3** Sandbox/isolation: isolated branch/worktree; no production credentials in untrusted build execution; no privileged token in workers.

### E. Context substrate (P0 scoped, P1 full) — SF-06
- **E1** Two authorized agents consume the same approved project context with provenance; cross-venture/revoked-scope queries return nothing forbidden (incl. cache); restart/replay doesn't duplicate observations; deletion propagates.
- **E2** Lessons loop: completed attempts record experience; derived lessons surface in later runs (`pod_context`/`pod_expertise`); founders can amend/delete lessons.
- **E3** Firewall semantics (manifesto): sharing is explicit and scoped; a session's data is not repeatable to a participant who lacks the grant; private-by-default for sensitive domains, shared-by-default for work (door open); cross-venture promotion requires a founder action.
- **E4** Governance record per session (non-negotiable): which agent ran, who requested, what data it touched, what it changed — queryable a year later without redoing the work (coverage in receipt/evidence pack).
- **E5** Graphify A/B (P1): same model/tasks/revision, canonical search vs graph-assisted; metrics: index cost, accepted solution quality, stale/missed relations, latency, reviewer time; graph falls back to search; inferred edges ≠ proof.

### F. Feedback & measurement (P0) — SF-09 + SF-10
- **F1** Basic monitoring/error/uptime + support intake → normalized bug signal → **one deduplicated Coffee task** with reproduction, severity, release SHA, affected-user evidence → same verified-fix pipeline. Alerts: owner, escalation, dedup key. Regression test fails before fix, passes after.
- **F2** Detail pilot (P1): scoped repo access; measurable reproducible findings, false-positive rate, accepted fixes, cost per confirmed bug; retention/isolation review before private-code sharing.
- **F3** Pilot evaluation (the Uber methodology): ONE real low-risk feature idea→market + held-out set (fixes, UI changes, docs); GitHub and GitLab tested independently; track failures, interventions, rework, cost, latency, founder review time (not PR counts); report compares baseline vs candidate on matched tasks, model fixed when testing harness changes; no simulated success.
- **F4** Cost/latency telemetry visible to founders (statusline-style): per-run and per-week; the 6-term equation is the unit of conversation.

### G. Evolution machinery (P0 minimal, P1 full) — SF-10
- **G1** Workflow/skill/context/routing changes require: versioned proposal → held-out evaluation → approval → canary → rollback.
- **G2** Contracts versioned; old versions supported during migration; breaking changes follow the same proposal path.
- **G3** Continuous improvement loop (manifesto): agent correction → auto-drafted reusable SkillProposal; repeated workflow → auto-created benchmark with tracked score; prompts that nail it first try are copied into skills/landmarks for future runs. (v2; lessons loop is the v1 seed.)
- **G4** Providers stay swappable: no hard-coded vendor integration; routing decisions are config (Uber lever 1, factory.ai pillar 1); sovereign/self-hosted options allowed for sensitive work.

### v1 cut line (explicit non-goals — "get out of the gates")
- Missions/fleet multi-agent parallelism across days (factory.ai Missions) — v2.
- Graphify and Detail in production — v1 is scoped optional pilots only.
- 1,000-tool ecosystems, org-wide catalog, fleet migrations at Spotify scale, 24M-node graphs — never copied; harvest primitives.
- Advanced orchestration platform, second coordinator, second task DB — v0/v1 stays one service.

---

## 4. Evolution path (maturity timeline, from Uber roadmap + factory.ai spectrum)

- **v1**: Coffee intake → 4-station pipeline → GitHub (+GitLab adapter) → founder gates in Coffee → basic telemetry → pilot eval → feedback loop (monitoring → dedup tasks).
- **v2**: dynamic model routing with per-agent Pareto benchmarks; deeper Pod context (expertise, lessons, curated packs); Graphify/Detail A/B wins promoted; Meetings→tasks loop hardened; multi-agent missions for parallel tracks; GitLab production parity.
- **v3**: real-time trace monitoring; auto-mining papercuts from traces → skill updates; cross-projects context graph decision support; evaluation-driven autonomy level selection (droid/automation/mission per task class).

---

## 5. Kanban cards (Venture Factory board)

Research-derived task set, SF-01…SF-10 kept as-is; new cards: RF-01 Research → Requirements map (this doc + Coffee capability audit), RF-02 Coffee MCP auth + capability probe, RF-03 Pipeline station spec (4 stations, **executable Standard of Completion authored pre-implementation**, blind verifier + evidence + gates), RF-04 Cost accounting + harness routing config (cache-aware; validator family ≠ implementer family; routing records), RF-05 Guardrails (linters/checks as agent feedback — Spotify golden-state pattern), RF-06 Pilot evaluation protocol (Uber methodology + held-out set; include stop-early/SOC comparison), RF-07 Multiplayer conformance (door-open defaults, firewall semantics, governance record, skill/benchmark loop). Each card carries: priority, dependencies, acceptance criteria, and source links.

---

## 6. Sources (with verification notes)

| Source | What verified | Caveat |
|---|---|---|
| UberEng X Article 2090828118454071296 / uber.com blog | 70%+ agent PRs etc.; full numbers in skill fact sheet | X article login-walled; numbers cross-checked vs Chinese summary + skill's primary extraction |
| engineering.atspotify.com (5 posts: Portal modes 9/2026; Code with Claude talk 6/2026; Data Assistant 6/2026; Multi-agent ads 2/2026; Release part 2 2/2026) | All numbers above from primary posts | 12.5% curation acceptance, 2.5M PRs, −8h release: primary source figures |
| vercel-labs/eve-software-factory-template + ask-foreman.dev | Four stations, factory brain, triggers, agent config, local-runs-untrusted | Template itself is MIT; eve stack is Vercel-specific (we take the pattern, not the stack) |
| factory.com/news/software-factory (Jun 15 2026) + /product/droids | Loop, three pillars, autonomy spectrum | Vendor framing; testimonials unverified |
| factory.com/news/what-it-takes-for-coding-agents-to-complete-large-software-tasks (Aug 27 2026) + factory.com/news/model-routing-belongs-in-the-harness (Aug 24 2026) | SOC experiment (24 ProgramBench tasks: single 36% vs SOC-system 90% parity on GDAL; header numbers verified from primary post) + router-in-harness (58% cost cut, cache-blindness costs 2.12–2.37× baseline) | One run per cell (no variance); system = 13× wall time — SOC buys completeness, not speed |
| detail.dev | Fix-PR/ticket model, enterprise claims | Testimonials are claims; no independent benchmark |
| graphify.com | Outputs, provenance, on-device, 17 assistants | 71–79× token savings are community reports |
| multiplayer-ai.com (Manifesto, Sep 2026) | Five principles + considerations; HBS team+AI 15.1% top-10%; Shopify River 1-in-8 PRs; governance four questions | Vendor manifesto; HBS study is a working paper; River number is a company claim |
| Ryan Carson (Greg Isenberg interview via The Neuron Jul 2026 + ryancarson.com/videos) + Matt Pocock (Sandcastle repo, AI Engineer talk) | One task/one agent/one env loop + evidence-PR; three automations (E2E test, production watchdog, rubric-based improvement loop); $20K/mo bill → route by task; prod creds vaulted & manually brokered; Sandcastle executor (branches, hooks, Docker/Podman/Vercel); Grill-Me design interview; ubiquitous language; deep modules + strategic ownership | The Neuron is an explainer of the interview (secondary — numbers cross-checked vs 40-PR/15-agent press reporting); Carson figures are his operating estimates ($5K/employee/mo, ~$60 E2E run); Sandcastle is MIT but young (Aug 2026, 1,193 commits) |
| vercel-labs/eve-software-factory-template `agent/` code + `evals/` (fetched Sep 2026) + Makson179/Bello README (v0.5.1) | Eve: single-file MODELS map (reviewer = different vendor), trust stamped once at dispatch, deny-not-park, brain 40K bound + reserved namespace, git safe.directory pitfall, station instruction contracts (analyst AC as verbatim reviewer checklist; implementer deviations/verification record; reviewer diff-first + re-run checks + verdicts), triage/writing/bridging skills, 8 safety evals. Bello: build→supervise→review→attack→repair→accept; per-role model; 66.3% less quota at +1.45% score; runtime-supervisor +9% on messy specs; FINAL_REPORT.md | Bello numbers = author's own 12+12 ProgramBench runs (no variance); eve template is a Vercel-stack deploy (we lift patterns, not the stack); both MIT |
| Coffee MCP OAuth doc (verified live 2026-08-28) + Pod docs (staging integration, README routes, experience-loop, authority gate) | Coffee MCP endpoint/flow; Pod routes incl. approvals, meetings sync, agent registry | Pod routes from README/docs of the local repo; Coffee REST surface beyond MCP not yet probed (RF-02) |
| techno-factory docs/architecture.md + api-v0.md; AGENTS.md | repo boundary, v0 contract, risk tiers | — |
