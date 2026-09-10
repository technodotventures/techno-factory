# The Product Development Lifecycle (PDLC)

**This is the canonical flow.** Every doc, skill, and surface (Techno OS, the factory, the launch process, Coffee cards) uses these names.

**Naming principle:** standard industry vocabulary — SDLC for the build half, the standard launch process for the GTM half. We do not invent terms; if the industry has a word for it, we use that word.

## The flow

```
Discovery → Spec → Build → Test → Review → Merge          (development half — SDLC)
              ↓
          Prepare → Message → Create → Launch Review → Go Live → Measure → Retro   (launch half — standard GTM)
              ↑                                                                        │
              └───────────────────────── insights ─────────────────────────────────────┘
```

## Development half (SDLC)

| Step | What happens | Role | Exit criteria |
|---|---|---|---|
| **Discovery** | Problem/opportunity intake — from founders, customers, or the Product Analyst's candidates; validated enough to spec | founders / anyone | worth speccing |
| **Spec** | Requirements + **acceptance criteria**; a failing test first | Planner (agent) | acceptance-criteria checklist exists |
| **Build** | Implementation on a branch, one task at a time | Builder (agent) | code complete; repo checks run |
| **Test** | Automated + manual verification; **evidence captured** (test output, recordings, screenshots) | Tester (agent) | evidence exists; failures reported as failures |
| **Review** | The human decision — **Approve to merge** (mechanical diff scan + evidence on the card; *silence never approves*) | a person | approved, or sent back with notes |
| **Merge** | Merged behind a feature flag | system | increment complete |

## Launch half (standard launch process)

| Step | What happens | Role | Exit criteria |
|---|---|---|---|
| **Prepare** | Assemble the **release record** from the merged build: release notes, behavior summary, screenshots, recording, demo URL | release prep (agent) | release record complete (`release-manifest.json`) |
| **Message** | **Messaging brief**: who it's for, the tension it resolves, ≤3 proof points, explicit non-claims | founders + creative | brief approved |
| **Create** | Produce the **launch assets**: help docs, video, social, email, in-app, support training | producers (agents) | assets drafted |
| **Launch Review** | **Fact check → brand check → legal check (conditional)** → the **Go/No-Go** decision | reviewers (people) | signed off, or sent back |
| **Go Live** | Ordered rollout: demo → docs → support smoke test → flag ramp → in-app → email → social → analytics armed | release | live |
| **Measure** | **Continuous product-health monitoring** — see Product Analyst below | Product Analyst (agent) | running |
| **Retro** | **Post-launch retrospective** (first formal checkpoint at 30 days): did it work? what changes the process? | founders + Analyst | document + template patches |

## The Product Analyst (the Measure role)

A standing agent role in Techno OS — the answer to "are people actually using what we ship?"

**It monitors:** usage analytics (most-used / unused features), activation funnels and drop-off points, where users get stuck (rage-clicks, repeated failures, dead ends), support-load signals (tickets per feature), and the analytics events **each release declares in its release record** — so the Analyst always knows what to watch for every feature.

**It produces:**
- a **weekly insight report** (adoption, dead features, stuck points, support load — plain language, cited to the data);
- **candidate work items** — improvement/feature proposals that enter **Discovery** (typed as candidates; humans triage);
- inputs for the 30-day **Retro** (adoption thresholds were set at Launch Review; the Analyst checks them).

**Boundaries:** the Analyst doesn't decide and doesn't build — it raises signal. It is distinct from the **engineering watchdog** (uptime, errors, performance — engineering concerns); the Analyst owns *product* health (usage, adoption, behavior).

**Why it's explicit:** it closes the loop. Without it, the PDLC is a line; with it, Measure → Discovery makes it a cycle — every launch teaches the factory what to build next.

## Roles at a glance

- **Agents (factory):** Planner · Builder · Tester
- **Agents (launch):** release-prep, producers — plus the **Product Analyst** (continuous)
- **People:** the Review decision (pre-merge) · the Launch Review / Go-No-Go · (both: *silence never approves*)

## Vocabulary (canonical — use these, retire the rest)

| Retired | Canonical |
|---|---|
| Gate A (build) | **Review** ("Approve to merge") |
| Gates A–E (launch) | **Launch Review** — fact check · brand check · legal check · **Go/No-Go** |
| Verifier / Checker | **Tester** |
| SOC / "done-when list" | **Acceptance criteria** |
| WorkItem | **Task** |
| EvidencePack | **Evidence package** |
| RunRecord | **Run log** |
| launch-manifest.json | **Release record** (`release-manifest.json`) |
| Launch Dossier | **Messaging brief** |
| EXTRACT / STORY / MAKE / PROVE / SHIP / LEARN | **Prepare / Message / Create / Launch Review / Go Live / Measure (+Retro)** |
| "sign-off" (action) | **Approve** (sign-off is fine as the noun) |

## Current status & next increments

1. **Build half** — factory v1 seed: coffee connect → 20 runs on the recurring work source (in progress).
2. **Launch half** — first increment when a real launch needs it: **release record emission + evidence package assembly** (the Prepare step).
3. **Measure** — Product Analyst pilot activates when a venture has live users and releases declare analytics events.
