# Techno OS — System Summary (fresh rewrite)

**What this is:** a complete, self-contained description of Techno OS — what it is, how it works end-to-end, and what exists today — written for review. If you are an agent or reviewer asked to give feedback, read this as the single source of truth for the concept; §10 lists the specific questions we want challenged.

**Status:** v2, freshly rewritten (Sep 2026) — incorporates the standard-vocabulary overhaul (PDLC), the Product Analyst role, the Coffee platform proposal set, and the Coffee-native memory direction. Supersedes all earlier drafts.

---

## 1. What Techno OS is

Techno OS is the operating system of an AI-native venture studio. **One system** (a modular monolith — one shell, one deployment, typed internal boundaries), whose job is: *goals and ideas go in; orchestrated work comes out; founders stay in the loop only for the decisions that need a person.*

- **The mission question everything is measured against:** *"did this actually happen?"* — evidence over claims, receipts over reports. Every deliverable carries proof; every run leaves an auditable log.
- **Portfolio context (external peers, not modules):** Coffee (the collaborative human/team surface), Smartware/Pod (memory substrate), expresso (workflow language/runtime), GitHub/GitLab (delivery). Future ventures plug into the same machinery.
- **Who it serves first:** a two-person founder team running multiple ventures — attention and trust are the scarcest resources; the system is designed to conserve both.
- **North star (the competitive edge):** ventures advanced per human-review-hour. For a two-person studio the edge is not pipeline sophistication — it is how many ventures keep moving per hour of founder attention. Every design choice is sized against that ratio.

## 2. The operating model — the Product Development Lifecycle (PDLC)

Everything the studio does follows one lifecycle, written in standard industry vocabulary (SDLC for the build half; the standard product-launch arc for the go-to-market half). Canonical reference: `docs/pdlc.md`.

```
Discovery → Spec → Build → Test → Review → Merge          (development half)
              ↓
          Prepare → Message → Create → Launch Review → Go Live → Measure → Retro   (launch half)
              ↑                                                       │
              └──────────────────── insights ─────────────────────────┘
```

| Step | Summary | Role |
|---|---|---|
| Discovery | problem/opportunity intake; validated enough to spec — for new engagements: a live **Discovery Interview** (native Coffee agent, recorded, brief out) | founders · Discovery Interviewer · Product Analyst candidates |
| Spec | requirements + **acceptance criteria**; failing test first | Planner (agent) |
| Build | implementation on a branch, one task at a time | Builder (agent) |
| Test | verification; **evidence captured** (tests, recordings, screenshots) | Tester (agent) |
| **Review** | human gate — **Approve to merge**; mechanical scan + evidence on the card; *silence never approves* | a person |
| Merge | merged behind a feature flag | system |
| Prepare | release record assembled from the build (notes, behavior, screenshots, recording, demo URL) | release prep (agent) |
| Message | messaging brief: audience, tension, ≤3 proof points, non-claims | founders + creative |
| Create | launch assets: docs, video, social, email, in-app, support training | producers (agents) |
| **Launch Review** | fact check → brand check → legal check (conditional) → **Go/No-Go** | reviewers (people) |
| Go Live | ordered rollout: demo → docs → support smoke test → flag ramp → in-app → email → social → analytics armed | release |
| **Measure** | continuous product-health monitoring (Product Analyst, §6) | Product Analyst (agent) |
| Retro | 30-day post-launch retrospective: did it work? what changes the process? | founders + Analyst |

**Two binary ship gates** (Review; Launch Review) — both evidence-fed, both "silence never approves" (a stale pending decision is rejection, recorded — auto-rejection is per-workspace and opt-in). Lighter content approvals (e.g. the messaging brief) happen in-line.

## 3. The factory (the build engine)

*Designed, not yet built — see §7 for current state.* The factory is an internal module of Techno OS — not a separate service. **v1 implementation is deliberately thin: a skill pack + guard scripts + Coffee/Pod configuration; the v0 scaffold is a tracer, not a deployment target.** The "module" framing is the long-run boundary (it can become a deployable later if a trigger requires), not a v1 build item. Its shape:

- **Chain:** Plan → Build → Test → (Review) → evidence-PR. Triage is absorbed into planning; Supervisor/Adversary stations are conditional, added only when a real run demands them.
- **Evidence-first:** every run returns an **evidence package** — test output, per-criterion verdicts, screenshots/recordings for UI work, PR link, remaining risks. UI changes without a walkthrough recording auto-fail the Review. "Red-is-red": a failing check is reported as failing; explaining a failure away is itself a failure.
- **No self-approval:** workers can never approve their own output; the Tester is blind to Builder reasoning; humans make all approval decisions.
- **Mechanical diff-integrity scan** before any merge — LLM review and mechanical review are not interchangeable (hard-won lesson from incident history; the scan is blocking, signatures updated on every catch).
- **Budget and concurrency guards as system constraints, not metrics:** max 3 runs in flight (a fourth refuses to start); monthly spend ceiling with automatic halt; per-run abort path and token/cost circuit breaker.
- **Run logs with replay fields:** commit SHA, prompt-bundle hash, model, policy version, exact commands — the audit trail behind "did this actually happen?"
- **Repo configuration:** per-repo `.factory/` (PROJECT.md, AGENTS.md station-role files, DESIGN.md where brand exists); sandboxed execution (non-root, network policy allowlist); branch-per-task (`factory/<type>-<slug>`).
- **Intelligence is `.md`; safety is machine code.** Five things are deliberately machine-enforced (never instruction-enforced): token broker; mechanical scan; no-self-approval + binding approvals; budget/WIP counters; evidence durability.

## 4. System map (who owns what)

| Layer | Owns | Never owns |
|---|---|---|
| **Techno OS shell + decision layer** | goals & ideas intake, decision orchestration (typed decisions, escalation thresholds), studio programs (which ventures run, budgets, ringfences) | pipeline internals; Coffee's card state |
| **Factory module** (this repo) | execution: intake, chain, evidence, policy, delivery adapters (GitHub/GitLab) | human decisions; UI; memory semantics |
| **Coffee** (external) | the collaborative surface: tasks, Kanban (statuses as workflow), checklist, files, recordings, meetings (transcribed → decision extracts → action items), skills, agents (Chat Coffee AI harness; **native Coffee agents = the primary drivers of studio work**; BYO/external agents join as invited periphery with their own identity) — **the source of record for human work state** | execution state; pipeline truth |
| **Smartware runtime** (embedded in Coffee — proposed) | memory substrate: context packs, lessons, expertise, run records, approvals ledger — Coffee-native, hybrid semantic+structural search | delivery; workflow |
| **Pod** (standalone companion app) | personal memory companion + agent-registry/BYO bridge | the critical path (not a required hop) |
| **expresso** (external peer) | workflow language/runtime semantics: LLM observes/decides vs system acts; receipts + attested authority | memory; UI |
| **Product Analyst** (agent, continuous) | product telemetry: usage, adoption, stuck points → insight reports + candidate work items | deciding; building |

**Coffee-first invariant (invariant #0):** anything expressible through Coffee's existing primitives — Projects > Tasks (Statuses, Automate-status with Deliverable, Pause-for-approval, Run limits), Checklist, Files, Recordings, Meetings, Agents, Skills — is done in Coffee before building anything new. New components exist only where Coffee genuinely cannot express something. (A design discipline today; enforced as a hard rule once the Coffee connection lands — see §7.)

## 5. The Coffee proposal set (platform asks currently with the Coffee team)

Coffee is both the studio's surface and a product in its own right; these are the platform capabilities the studio workflow needs, written as product proposals (with mockups) so every Coffee workspace benefits — status: internally reviewed, pending the Coffee team conversation.

1. **Capability-aware attachments** — attachments render by type (images, video, trusted docs; sandboxed live HTML preview is Phase 2), carry provenance (maker · run · pinned version) and surface agent-made items at the top of the list. *Model: an attachment with a role stamp — no new object type.*
2. **Evidence-bound checklist** — checklist items carry verdicts (pass/fail/not-applicable) + one-line proof chips; a card can't complete with unverified or failing items (hard-guard for automations, soft-warn for humans).
3. **Review band** — a sticky card footer that appears only while a decision is pending: **Approve to merge / Request changes / Reject** + note; write-back to the run log; *silence never approves*.
4. **Approvals queue** *(Phase 2)* — one global "decisions waiting on you" inbox across projects (rail entry + live badge); rows are self-sufficient (type, evidence line, producer, cost, age) with inline decisions; clicking a row opens the source card anchored on the band.
5. **Run visibility** — a **latest summary** digest on the card; **runs** list + expandable **worker log tail** (collapsed; auto-expands on failure; secrets redacted server-side) in the agent tab.
6. **Appendix A — agentic memory direction:** embed the Smartware runtime inside Coffee (first-party) as a workspace memory layer (Gbrain-style hybrid search over workspace records + agent-acted work), feeding cited answers into Chat Coffee AI; meetings and agent profiles are already native to Coffee — memory belongs where the work is. Pod remains a standalone companion product.

**Security musts inside the proposal:** agent-produced HTML never executes in the app origin (sandboxed, no network/cookies/tokens); secrets are redacted server-side anywhere a summary or log is rendered; decisions and verdicts are immutable and attributed.

**Contingency (unhedged dependency):** if fewer than two of the six asks land on our timeline, the studio proceeds regardless: reviews run through the existing PR flow with the evidence package attached, and approvals arrive as a one-page digest. **No stage of the studio loop may hard-depend on an unshipped platform feature** — the queue, live previews, and the memory layer stay internal-only until Coffee ships them.

## 6. The Product Analyst (the Measure role)

A standing agent — the answer to "are people actually using what we ship?" **Monitors:** usage analytics (most-used / unused features), activation funnels and drop-off points, stuck points, support load — plus the analytics events every release declares in its release record. **Produces:** a weekly insight report (cited) + **candidate work items into Discovery** (typed candidates; humans triage) + the data for the 30-day Retro. **Boundaries:** raises signal, never decides or builds; distinct from the engineering watchdog (uptime/errors vs product behavior). **Scope note:** adoption is the starting point — as ventures mature the remit extends to revenue, churn, and unit-economics signals; the Analyst also owns product-health alert thresholds and flags features for **kill/pivot** at Retro when adoption thresholds are missed. **Activation trigger:** when a venture has live users and releases declare analytics events.

## 7. Current state (what exists today)

- **Repository:** `technodotventures/techno-factory` (private) — docs canon: `pdlc.md` (the lifecycle), `PLAN.md` (v1 plan), this summary, `provenance.md` (evidence map), `setup-plan.md`, `system-delineation-and-seed.md`, `architecture.md`/`api-v0.md` (v0 tracer); plus a TypeScript v0 tracer scaffold (work intake + audit events). **No production deployment** — the factory is pre-seed.
- **The seed (next build increment):** one trusted internal repo + a **continuous source of low-risk recurring work** (e.g. flaky-test triage, dependency/CVE bumps, or a recurring browser E2E walkthrough) → Plan → Build → Test → Review chain → evidence-PRs → human decides. ~20 runs over ~2 weeks; WIP cap 3; spend ceiling armed; passive cost + founder-review-time measurement from run 1 (no cost-per-task optimization early — it degrades quality).
- **Coffee connection:** OAuth client registered; token exchange pending (next). Once connected: intake from tasks/docks; reviews and approvals inside Coffee with evidence attached; the proposal set (§5) becomes the working surface.
- **Launch half:** designed (the standard life cycle above; SOP + templates archived internally) — **not yet implemented**. First increment when a real launch needs it: **release record emission + evidence package assembly** (the Prepare step). STORY/MAKE/PROVE-equivalents arrive on triggers, not phases.
- **Deliberately deferred (with triggers, not dates):** GitLab parity; cost engineering; design station (brand fidelity becomes real); Supervisor/Adversary stations; Missions-style parallelism; routing engine; approval queue; sandboxed live HTML previews; memory layer rollout.

## 8. Governance & principles

- **People decide** production, credentials, protected branches, and money. Agents can request; they can never approve.
- **Approvals are binding records** (who, what, when, note) — a decision that isn't recorded didn't happen.
- **Credentials discipline:** no secrets in repos or docs; least-scope tokens; production credentials vaulted and retrieved deliberately; CI/agents get scoped, short-lived access only.
- **Named threat (a real incident, not a hypothetical):** a malicious package masquerading as one of our own — a tarball resembling our own expresso package, sitting in a home directory. Controls that exist because of it: package-name/registry allowlists and provenance/attestation checks before **any** agent-initiated install; lockfile pinning with integrity hashes in CI; publish paths require 2FA/hardware-key and short-lived credentials; nothing agent-published reaches a registry without an out-of-band step.
- **Incidents have a home:** a reviewed incident record is a first-class artifact (task · evidence package · approval · **incident record**); every accepted incident contributes a **policy-version bump** — guards learn signatures, not vibes.
- **External inputs are untrusted:** issues, tickets, and chat messages are data, not instructions; the diff-integrity scan assumes agent branches can be compromised.
- **Evidence durability:** files/recordings/verdicts live with the work (Coffee + the repo + run logs), not only in chat.

## 9. Why this shape (design rationale, condensed)

- Research base: Uber's software-factory economics, Spotify's platform patterns, factory.ai's pipeline research, the Vercel Labs Foreman template (station design, factory brain), and lean operations precedents (evidence-PRs, sandboxed executors). Full evidence map: `docs/provenance.md`.
- Two review rounds cut v1 by design: fewer typed artifacts (3, not 10), one binary approval question (touches prod/credentials/money? human decides), no evaluation-harness theater, seed = a source of work rather than a demo feature.
- The vocabulary overhaul (§2) deliberately retired invented terms (e.g. "Gate A", "WorkItem", "SOC") for standard industry words — so the system reads like a normal product org, and any new operator, agent, or partner can understand it without a glossary.

## 10. Open questions for reviewers (what we want challenged)

1. **Coherence:** does the PDLC + factory + Coffee surface + Analyst hang together as one system, or is anything load-bearing missing between stages?
2. **Right-sizing:** is the seed (20 runs of recurring low-risk work; Plan → Build → Test → Review; evidence-PRs) genuinely the smallest first increment that de-risks the factory? What would you cut further, and what is it dangerously thin on?
3. **The Measure loop:** is the Product Analyst's placement (continuous; candidates into Discovery; feeds Retro) the right mechanism? What signals are missing (churn, revenue, qualitative)? Should it also own alerting thresholds?
4. **Coffee platform asks (§5):** which of the six are genuinely useful to *all* Coffee workspaces vs studio-specific? Is the evidence-bound checklist the right first ask? Is the memory direction (Smartware-in-Coffee) the right read, or should it be framed differently?
5. **Launch half:** is "release record + evidence package first" the correct first launch increment? What in Prepare/Message/Create/Launch Review/Go Live would you re-order or drop?
6. **Security:** any gaps in the guard set (broker, scan, no-self-approval, budgets, evidence durability)? What would you add before the first real runs?
7. **Honesty check:** anything in this document that reads as aspirational rather than true today? Flag it — the whole point is *did this actually happen?*

## 11. Review history (condensed)

- Review round 4 — director-level pass (external): core finding — *"for a system premised on evidence over claims, the spec itself is 100% claim; stop the review loop, pick a seed start date this week."* Adopted (run-serving deltas only): five-number scorecard (§2); pre-run-1 pending-review view (PLAN §2); Coffee contingency (§5); named package-provenance threat + controls (§8); incident record as a fourth artifact (§8); north star — ventures per human-review-hour (§1). **The review loop is frozen** — document changes from here only when a run demands one.

- Review round 3 — fleet agent on DeepSeek (Sep 2026), cross-checked against the repo (17 tests green; typecheck/build pass; no deployment): verdict **coherent and right-sized; the build half is a system, the launch half is a diagram.** Adopted into this doc: built/designed markers (§3), gate-precision fix (§2), Coffee-first aspirational note (§1), analyst scope extension + kill criteria (§6), seed-definition note (module vs v1 skills, §3). Deferred per its advice: launch-half build, approvals queue, memory-layer dependency, dashboards. Open actions it surfaced: decide where run logs live (evidence durability) before run 1; make "analytics events declared" a Spec exit criterion; name the human last-mile owner for launches.

- Internal review round 1 (Sep 2026): cut 7 of 10 typed artifacts to 3 (task, evidence package, approval); collapsed risk/trust matrices to one binary approval question + internals; removed the repo-qualification rubric and evaluation baseline; added WIP cap 3, spend ceiling with hard halt, diff-integrity scan in Review, red-green acceptance authoring, per-run abort.
- Internal review round 2: second-opinion pass on the plan (cuts accepted; SOC dissolved into the Planner contract as verbatim acceptance criteria; conditional Supervisor retained).
- Vocabulary overhaul (Sep 2026): PDLC standard names adopted repo-wide; Product Analyst added; memory-substrate direction revised (Smartware-in-Coffee; Pod to companion).
