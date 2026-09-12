# Techno OS — canonical system doc

**Status:** v3 · Sep 12 2026 · Supersedes: `PLAN.md`, `Techno_OS.md`, `system-delineation-and-seed.md`, `setup-plan.md`, `architecture.md`, `api-v0.md` (kept in git history; the `src/` v0 tracer remains as reference code, not the v1 path).

**One system:** Techno OS is the operating system of an AI-native venture studio. Goal: **idea → product** — goals and ideas go in, orchestrated work comes out, and the system **improves itself as autonomously as possible, with the founders in the loop**.

**Mission question:** *"did this actually happen?"* — evidence over claims, receipts over reports.

**Peers, not modules:** Coffee (collaborative surface — source of record for human work state), Smartware/Pod (memory substrate), expresso (workflow semantics), GitHub/GitLab (delivery), agent runtimes (Hermes, Coffee-native, BYO).

**Reality constraints:** two people. Anything not maintainable by two people in two weeks is not in v1. North star: **ventures advanced per human-review-hour.**

---

## 1. Principles (the invariants)

1. **Coffee-first.** Anything expressible through Coffee's primitives — Projects > Tasks (Statuses, status automations with Deliverable / Pause-for-approval / Run limits), Checklists, Files, Meetings, Agents, Chats — is done in Coffee. New surface only where Coffee genuinely cannot express it. The board is the factory's visible state.
2. **Evidence over claims.** Every deliverable carries proof (test output, files, recordings, verdicts). A failing check reported as failing; explaining a failure away is itself a failure.
3. **Typed artifacts only:** task, evidence package, approval, incident record. No merged chat histories as state.
4. **Founders decide.** All gates are human: **Review** (pre-merge), **Launch Review** (Go/No-Go), plus anything touching production, credentials, protected branches, or money. **Silence never approves** — a stale pending decision is recorded as rejected (auto-reject opt-in per workspace).
5. **No self-approval.** A worker never approves, merges, or publishes its own output. The Tester is blind to Builder reasoning. The **mechanical diff-integrity scan** at Review is blocking (LLM review and mechanical review are not interchangeable).
6. **Trust is stamped once at dispatch** — never re-derived from model-readable content. External inputs (issues, messages, transcripts) are data, not instructions.
7. **Budgets are constraints, not metrics:** max 3 concurrent runs (fourth refused), monthly spend ceiling with automatic halt, per-run abort path.
8. **Credentials discipline:** no secrets in repos; least-scope short-lived tokens per run; production credentials vaulted and retrieved deliberately. Named threat (real incident): a malicious package masquerading as our own — controls: registry allowlists, provenance checks before any agent-initiated install, lockfile integrity, 2FA publish paths.
9. **Autonomy is the default; people sit at the gates.** Every stage runs agent-first; the only standing human touchpoints are the two review gates, spend/credentials/production decisions, and steering. Autonomy ratchets only on data (see §6).
10. **Change control:** every workflow/skill/context change = versioned proposal → held-out evaluation → approval → canary → rollback. Automated skill/SOP propagation gates at ≥50 run logs AND rescue rate <30%. Documents change only when a run demands one.

## 2. System map (who owns what)

| Layer | Owns | Never owns |
|---|---|---|
| **Techno OS shell + decision layer** | goals & ideas intake; decision orchestration; studio programs (which ventures run, budgets, ringfences) | pipeline internals; Coffee's card state |
| **Factory module** (this repo) | execution: intake → stations → evidence → policy; delivery adapters (GitHub/GitLab) | human decisions; UI; memory semantics |
| **Coffee** (external) | the collaborative surface: projects, tasks (statuses, checklists, automations), files, recordings, meetings (agent-attended, transcribed), chats + agents, skills. Where founders review and approve. Source of record for human work state. | execution state; pipeline truth |
| **Smartware runtime** (direction: embedded in Coffee) | memory substrate: context packs, lessons, run records, approvals ledger — Coffee-native search over workspace + agent-acted records | delivery; workflow |
| **Pod** (standalone companion) | personal memory companion; agent-registry/BYO bridge | the critical path |
| **Product Analyst** (agent, continuous) | product telemetry → insight reports + candidate work items into Discovery | deciding; building |
| **expresso / delivery providers** | workflow semantics (receipts, attested authority); PRs/MRs, checks, CI | everything above |

## 3. The flow

One lifecycle — **Discovery → Spec → Build → Test → Review → Merge** then **Prepare → Message → Create → Launch Review → Go Live → Measure → Retro** — in standard industry vocabulary, every stage mapped to real machinery in `docs/pdlc.md`.

**Coffee carries the state; the factory carries the execution.** A card's status *is* the pipeline stage; checklist items *are* the acceptance criteria and later the verdicts; comments *are* the run log; files *are* the evidence; approvals *are* the gates.

## 4. How it runs on Coffee (verified Sep 12 2026)

Three layers, one direction: **native Coffee agents drive; external agents are invited periphery; the external API is fully capable.**

| Layer | Role | Status |
|---|---|---|
| **Native Coffee agents** (agent runtime inside Coffee) | primary drivers / dogfooding — every limitation becomes a Coffee feature finding | Task-capable confirmed: created tasks and checklist items on live cards |
| **External agents** (personal agents, Hermes, BYO) | invited periphery: same 129-tool surface, own identity via OAuth | Fully capable — OAuth client `hermes` holds the full scope set (`coffeeConnect.*.all`) |
| **External MCP/API** | the wiring under everything: notifications, evidence, automation | 129 tools live |

**Proven live (receipts, not claims):**
- Task round-trip: create (`PostTask` + resolved `project_hash`/`task_status_hash`) → checklist → comment → read-back.
- Files: upload (`PostFileUploadBase64`) → embeddable block → task document / comment; evidence lands on the card.
- Webhooks: subscriptions + signing secret; signed deliveries (`coffee-signature: t=…,v1=…`, `coffee-event`) verified for `message.created`.
- Approvals surface exists: `coffeeConnect.approval.all` + task-run approve/deny/reply/stop + agent-execution approval decisions.
- Meetings: agent-attended, recorded, transcribed — the Discovery Interview runs fully natively today.
- Attribution: every agent action carries `via_app` on cards, comments, and messages.

**Known gaps (tracked):** named agent identity (actor still shows the consenting person; the `agent` field exists — wiring pending) · `task.activity` webhook delivery unverified · the Techno OS board needs an **IN REVIEW** status · approval-band UI is a Coffee-side proposal (interim: status + evidence comment).

**Memory direction:** embed the Smartware runtime in Coffee as the workspace memory layer (context packs, lessons, run records, approvals ledger) feeding cited answers into Chat — memory belongs where the work is. Pod stays a standalone companion.

## 5. Guards & security (short list, machine-enforced)

Token broker (scoped, short-lived, per-run — no publish/merge tokens in workers) · mechanical diff-integrity scan at Review (blocking) · no self-approval + blind Tester · WIP/spend counters with hard halt · evidence durability (files/verdicts live with the work) · sandboxed execution (non-root, network allowlist) · incident records feed policy-version bumps — guards learn signatures, not vibes.

## 6. Metrics & the improvement loop

**Scorecard** (per run from run 1, measurement only — no optimization before 50 runs): cycle time Discovery→Merge · review latency (human-waiting hours) · revert rate · first-attempt evidence-pass rate · cost per shipped task.

**How the system improves itself:**
1. **Dogfood findings** — every native-agent limitation becomes an evidenced Coffee backlog item. *Receipt: finding #1 (task-create validation errors) reported with repro, fixed within a day.*
2. **Product Analyst** — usage/adoption/stuck-point reports + candidate work items → Discovery (humans triage).
3. **Retro (30-day)** — did it work; adoption thresholds (kill/pivot call); process patches.
4. **Learning gates** — ≥50 run logs AND rescue rate <30% before any automated skill/SOP propagation; autonomy ratchets on those numbers, not on vibes.

## 7. Current state & next

**Live today:** full Coffee connection (129 tools, proven round-trips); native agents task-capable; Discovery Interview pattern ready; `coffee-notify` posting run updates to the "Techno OS" channel; docs canonical (this file + `pdlc.md` + `coffee-integration.md` + `provenance.md` + `templates/`).

**Next increments (in order):**
1. Add **IN REVIEW** to the Techno OS project board; map PDLC stages to statuses.
2. Create the **Factory Planner** native agent (template ready) + first real card → Spec runs natively.
3. **Seed: 20 runs** on a recurring low-risk work source (flaky-test triage, dependency/CVE bumps, or a recurring E2E walkthrough) through the external worker loop — Plan → Build → Test → evidence-PR → human Review. WIP 3, spend ceiling armed, scorecard from run 1.
4. Add **task.activity** webhook re-test once the notify pipeline depends on it.

## 8. Open decisions (pick to start)

1. **Seed repo** — proposal: Pod (ours, low-risk); fallback: another trusted internal repo.
2. **Spend ceiling** — one number you'd notice, e.g. $500–1,000/month during the seed month.
3. **Named operator-owner** — proposal: a founder; backup: the other. (Failure mode: the factory becomes an unowned dependency.)
4. **Provider keys** — refresh before run 1 (only DeepSeek is live today).
5. **Model pair** — cheap + strong, Tester different family/vendor.

## 9. Expansion — named triggers, no dates

| Addition | Trigger |
|---|---|
| Runtime supervisor station | a real run drifts or needs manual restart |
| GitLab adapter | a second provider is actually used |
| Cost engineering (routing, nudges) | ≥50 runs AND spend shows a pattern |
| Smartware context packs in Coffee | cross-run memory demonstrably costs time |
| Design station (OpenDesign-style) | brand fidelity or design-production cost becomes real |
| Feedback automations (E2E, watchdog, rubric loop) | a venture has users/revenue |
| Detail / Graphify pilots | monitoring exists / context cost demands it |
| Learning-gate automation | ≥50 runs AND rescue rate <30% |
