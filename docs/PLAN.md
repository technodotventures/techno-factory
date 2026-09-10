# Techno OS — The Plan (v1, post-review · Sep 07 2026)

One system, two people, three stations. Every word of this plan is what we actually build before any expansion; everything after the seed is a trigger with a name, not a phase with a date.

Supersedes: `docs/setup-plan.md` (earlier phase plan), SF-01…SF-10 (kept as background), the first-review draft of `docs/Techno_OS.md` §7·§8. Consensus sources: research (see `docs/provenance.md`), March handbook adopted-primitives list, Internal review + second review (both recorded in `docs/Techno_OS.md` §13–§14).

---

## 0. What we are

**Techno OS** = one deployable (modular monolith; home shell = the OS shell) + external peers: Coffee (human/team surface), Pod/Smartware (context/memory substrate), expresso (workflow language), Hermes (agent runtime), GitHub/GitLab (delivery). The factory is a bounded module of the OS — its own codebase (`techno-factory` repo), shipped as the monolith's module, with contracts strict enough that extraction later is mechanical.

**The mission question:** *"did this actually happen?"* — evidence over claims; receipts over reports; the factory is not believed, it is checked.

**Headcount reality: two people.** Names from platform companies (stations, tiers, envelopes, gates) are vocabulary, not commitments. If a mechanism can't be maintained by two people in two weeks, it is not in v1.

## 1. The invariant list (short, because short survives maintenance)

0. **Coffee-first.** Anything expressible through Coffee's existing primitives — Projects > Tasks > Docs > Agents; task **Statuses**; **status automations** (agent action on status entry, with Name/Purpose, Work type, Agent, Deliverable definition, **Pause for approval**, Run limits); Docks; meetings → tasks; approvals — is expressed there. New surfaces/artifacts are introduced only when Coffee cannot express it. Techno OS is the orchestration layer *underneath* Coffee (decision + factory pipeline + Pod memory + budget/policy); the visible surface is Coffee. The personal founder console (voice/pocket) is a separate personal surface, not the studio UX.
1. Cross-layer communication is typed artifacts only — in v1 that is **task, evidence package, approval** (fields over artifacts; nothing else exists yet).
2. Trust is decided once at dispatch; nothing downstream re-derives it from model-readable content.
3. Silence never approves. Unattended runs deny-not-park.
4. A worker never approves, merges, or publishes its own output (token broker: no npm publish token, no repo-scoped GitHub CLI token in any worker — scoped, short-lived, per-run).
5. Only factory-owned branches receive automated fixes; protected branches stay protected.
6. The Tester is blind to Builder reasoning and re-runs the checks itself.
7. **The Review gate's mechanical diff-integrity scan is blocking** — LLM review and mechanical review are not interchangeable (per Expresso/Pod/Smartware history).
8. Founder corrections supersede derived context; providers stay swappable (models, harnesses = config).
9. Systems bounds: **max 3 concurrent runs** (fourth refused), **monthly spend ceiling armed with automatic halt**, every run has an abort path.
10. Any change to workflow/skill/context/routing requires: versioned proposal → held-out evaluation → approval → canary → rollback.

## 2. The seed (build now; ~2 weeks; 20 runs)

**Final framing (Coffee-first):** the visible surface is Coffee; the brain is a **skill pack**; the enforcement is **guard scripts**; the memory is **Pod**. The "factory module" reduces to: `factory-skills` repo (skill pack + scripts), Coffee/Pod configuration, and one narrow credential-broker path. No service, no job DB, no gateway, no separate envelope store in v1 — Coffee's tasks/statuses/automations/approvals carry the state; Pod carries memory and evidence.

**Shape:** one repo you already trust → a continuous source of low-risk work → Plan → Build → Test → Review (a check, not a station) → a human decides → evidence-PR. WIP cap 3. Spend ceiling armed. Measured from run 1.

**Work source (not a feature):** flaky-test triage, dependency/CVE bumps, or the recurring browser E2E walkthrough — in Pod or another trusted internal repo (seed repo pending final choice; proposal: Pod — it is ours, low-risk, and already produces meeting/task-shaped data for the M&A loop; another trusted internal repo is the fallback).

**Build order (each step small, each verify-able):**

1. **`.factory/` config in the seed repo** — `PROJECT.md` (what/why, ≤100 lines), `AGENTS.md` (station role files: planner, builder, tester + approval matrix + permission rules), `DESIGN.md` only if the repo has brand (else skip). Runtime adapters (Claude Code/Codex/Hermes) generated thin. No other state files.
2. **Runner wiring on Sandcastle** — `sandcastle.run()` per task; branch strategy `factory/<type>-<slug>`; Docker provider; hooks: `git safe.directory` + sandbox egress policy (restricted network; explicit allowlist where a run needs it); non-root agent user.
3. **Stations as role configs, not code** —
   - *Planner*: grounds in live checkout (real files, real commands; **docs-first: AGENTS.md / README / CONTEXT.md / DESIGN.md / PROJECT.md before code**); outputs the plan as structured fields, **including acceptance criteria as the verbatim checklist the Tester applies** (this is the standard of completion — checklist before implementation, no separate artifact); **red-green: the work is defined by a failing test first**; **`out_of_scope` — ticket-level non-goals: what this work is NOT doing (system-level v1 non-goals exist in §8; per-ticket ones did not)**; approach + rejected alternative; affected surface with public contracts flagged; risks; test strategy; assumptions; open questions (**ask only what the repo/issue cannot answer**). Depth to an artifact; the structured plan is the contract.
   - *Builder*: executes the plan; deviations recorded, never silent; no stubs; records exactly what checks ran and their output (could-not-verify → says so); fixed factory git identity; no mid-run questions — narrowest reasonable choice + deviations, or stop (`pushed:false` + `known_limitations`).
   - *Tester*: blind; real `git diff`; re-runs the fastest checks ("distrust 'it should work'"); **red-is-red: a failing check is reported as failing — a summary that explains a failure away is itself a failure**; every acceptance criterion marked pass/fail with evidence; verdicts approve / request_changes (specific, actionable, traceable to correctness/AC/safety/scope) / reject (approach wrong); **different model family from Builder's, different vendor**.
   - *Triage*: lives inside Planner until issue volume hurts (then becomes a station).
4. **Review — a check, not a station; three checks in order:**
   a. **Mechanical diff integrity (blocking)** — long-line heuristic + `atob(` / `eval("global.` / `global.[a-z]='<digits>-` signatures on every factory branch, plus diff-shape guardrails (e.g. no `.env`, no `.git/`, no unrelated-file edits).
   b. **Evidence completeness** — test output; screenshots; **automatic feature recording** for UI-affecting work (captured from the browser E2E harness; lands on the review card automatically; fail only if required-but-unproducible); report shape: status / changed files / checks / remaining risks / **lockfile- and artifact-churn justification — churn without justification = request_changes**.
   c. **Human binary** — does it touch production, credentials, protected branches, or money? Yes → human decides (approve with binding record) and no worker can approve itself. No → runs.
4. **Broker + vault** — worker tokens: scoped, short-lived, per-run, no publish scope, no repo-scoped CLI token; prod credentials: vaulted, retrieved manually per session ("the intentional moment"); audit log of every action. (Coffee does not own this — it is the one narrow service custom to the factory, or a Pod/credentials service call.)
6. **Run budget layer** — WIP cap 3 (refuse 4th, queue or reject visibly); monthly spend ceiling one number + automatic halt; per-run abort path; max-tokens/run default.
7. **Measurement from run 1** — intervention count, rescue rate, merge-without-rework, cycle time, founder-review-time per item, plus a **cheap comparator** (first week: also run 2–3 items single-agent by hand; or alternate weeks chain/solo; no evaluation harness). Cost recorded passively; never optimized before 50 runs.
8. **The 20-run trial** — point the factory at the work source; run; count; review; decide.

**Seed acceptance (what "done" means):** 20 runs completed on the real work source; every PR passed the Review gate's mechanical scan (and any block was triaged and the signature added to the guard); no worker ever held a publish/merge-grade token; zero unauthorized actions; a written decision (founders explicitly accept / revise / stop) based on interventions + founder-review-time vs the comparator.

## 3. Expansion — named triggers, no dates

| Addition | Trigger (named) |
|---|---|
| Runtime supervisor station | a real run drifts or must be restarted manually (Bello evidence justifies it then) |
| Adversary station | an R3+-class run needs it (credential/security/critical path) |
| GitLab adapter | a second provider is actually used (GitHub is the house provider) |
| Cost engineering (routing, nudges, 6-term equation) | ≥50 runs AND spend shows a pattern; until then: one model-per-station config |
| Pod/Smartware context packs + lessons | cross-run memory demonstrably costs time (context packs replace any hand-made state) |
| Coffee surface (intake, reviews on cards, approvals, meetings→decisions, Chat AI harness) | the founder says so; wiring ready (MCP client creds staged; one consent pending) |
| Design station (OpenDesign-style) | brand fidelity or design-production cost becomes real (GTM assets, decks, video) |
| Feedback automations (E2E walkthrough, production watchdog, rubric loop) | venture has users/revenue |
| Detail / Graphify pilots | monitoring exists / context cost demands it |
| Learning gates (SOPs, skill auto-propagation, autoresearch-style loops) | ≥50 run logs AND rescue rate <30% |
| Repo qualification rubric scripted | second/third repos and strangers start using the factory (manual once is fine while it's ours) |

## 4. Non-goals (v1 — really not in it)

Missions/fleet parallelism · routing engine · ubiquitous-language doc · separate acceptance-criteria artifact (dissolved into Planner checklist) · Graphify/Detail in production · org-wide catalogs/fleet migrations · HMAC gateway + service task DB · GitLab parity · Coffee UI changes · autonomous merge/deploy/release · >1 delivery provider · >1 worker token authority.

## 5. Open decisions (pick to start)

1. **Seed repo** — proposal: **Pod** (ours, low-risk, data-rich); fallback: another trusted internal repo.
2. **Spend ceiling number** — proposal: a number you'd notice casually, e.g. $500–1,000/month of agent spend for the seed month.
3. **Named operator-owner** — proposal: the founder; backup: the second operator (founding team). (The failure mode is the factory becoming an unmaintained dependency neither of you owns.)
4. **Refresh deployment provider credentials before run 1** (LLM provider keys expired; tooling quota spent) — do now, blocks the first real run otherwise.
5. Model provider pair for seed (cheap + strong; tester different family/vendor) — any OpenRouter pair works; proposal: cheap = DeepSeek-Flash-class, strong = Claude-Fable-5-class.
