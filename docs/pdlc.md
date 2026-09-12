# The Product Development Lifecycle (PDLC)

**Canonical flow.** Every doc, skill, and surface (Techno OS, the factory, launch, Coffee cards) uses these names. Vocabulary is standard industry language — SDLC for the build half, the standard launch arc for GTM. We do not invent terms.

```
Discovery → Spec → Build → Test → Review → Merge          (development half — SDLC)
              ↓
          Prepare → Message → Create → Launch Review → Go Live → Measure → Retro   (launch half — standard GTM)
              ↑                                                                        │
              └───────────────────────── insights ─────────────────────────────────────┘
```

**How it runs:** Coffee carries the state; the factory carries the execution. A card's **status** is the pipeline stage · checklist items are the **acceptance criteria** and later the **verdicts** · comments are the **run log** · files are the **evidence** · approvals are the **gates**.

## Development half (SDLC)

| Step | What happens | Runs on | Exit criteria |
|---|---|---|---|
| **Discovery** | Problem/opportunity intake — founders, customers, or Analyst candidates. For new engagements: a **Discovery Interview** — native Coffee agent in a meeting room, one question at a time, recorded + transcribed, brief out. | Native Coffee agent ("Client Relations") + founders | worth speccing; brief produced |
| **Spec** | Requirements → **acceptance criteria as checklist items on the card**, plan comment, **first proof step** (red before green), `out_of_scope` list. | Native Coffee agent ("Factory Planner") on the card | criteria checklist exists; analytics events declared (user-visible features) |
| **Build** | Implementation on a branch, one task at a time; deviations recorded, never silent. | External worker (sandboxed; branch `factory/<type>-<slug>`); card updated via API | code complete; repo checks run |
| **Test** | Blind verification (Tester never sees Builder reasoning); re-runs the checks; failures reported as failures. | External worker (blind Tester) + evidence uploaded to card | evidence on card; verdicts pass/fail per criterion |
| **Review** | **The human decision — Approve to merge.** Mechanical diff scan + evidence on the card; *silence never approves*. | **A person, in Coffee** (card in IN REVIEW) | approved, or sent back with notes |
| **Merge** | Merged behind a feature flag; run log closed. | Worker/human merges; card → COMPLETE | increment complete |

**Discovery in practice (native, live today):** the Discovery Interview agent interviews the founders or a client live — recording + transcription on, unknowns labeled, MoSCoW priorities captured — and produces the brief that feeds Spec. Reference prompt: `docs/templates/discovery-interviewer-agent.md`.

## Launch half (standard launch arc)

| Step | What happens | Runs on | Exit criteria |
|---|---|---|---|
| **Prepare** | **Release record** assembled from the merged build: release notes, behavior summary, screenshots, recording, demo URL. | release-prep agent | release record complete |
| **Message** | **Messaging brief**: audience, the tension it resolves, ≤3 proof points, explicit non-claims. | founders + creative | brief approved |
| **Create** | **Launch assets**: help docs, video, social, email, in-app, support training. | producer agents | assets drafted |
| **Launch Review** | **Fact check → brand check → legal check (conditional) → Go/No-Go.** | reviewers (people) | signed off, or sent back |
| **Go Live** | Ordered rollout: demo → docs → support smoke test → flag ramp → in-app → email → social → analytics armed. | release (checklist on the card) | live |
| **Measure** | Continuous product-health monitoring (Product Analyst). | Product Analyst agent | running |
| **Retro** | 30-day retrospective: did it work? What changes the process? **Kill/pivot call** when adoption thresholds are missed. | founders + Analyst | document + process patches |

## The Product Analyst (Measure)

Standing agent — the answer to "are people actually using what we ship?"

- **Monitors:** usage analytics (most-used/unused), activation funnels, stuck points, support load — plus the analytics events each release declares.
- **Produces:** weekly cited insight report · **candidate work items → Discovery** (humans triage) · Retro inputs.
- **Boundaries:** raises signal, never decides or builds. Distinct from the engineering watchdog (uptime/errors).

**Why it's explicit:** it closes the loop. Without it the PDLC is a line; with it, Measure → Discovery makes it a cycle — every launch teaches the factory what to build next.

## Roles at a glance

- **Agents (build):** Planner · Builder · Tester (blind) — plus Triage inside planning.
- **Agents (launch):** release-prep · producers — plus the **Product Analyst** (continuous).
- **People:** the **Review** decision · the **Launch Review / Go-No-Go** · steering, spend, credentials (both gates: *silence never approves*).

## Vocabulary (canonical — use these, retire the rest)

| Retired | Canonical |
|---|---|
| Gate A / Gates A–E | **Review** / **Launch Review** (fact · brand · legal · Go/No-Go) |
| Verifier / Checker | **Tester** |
| SOC / "done-when list" | **Acceptance criteria** |
| WorkItem | **Task** |
| EvidencePack | **Evidence package** |
| RunRecord | **Run log** |
| Launch Dossier | **Messaging brief** |
| EXTRACT / STORY / MAKE / PROVE / SHIP / LEARN | **Prepare / Message / Create / Launch Review / Go Live / Measure (+Retro)** |

## Current status & next increments

| Area | State | Next |
|---|---|---|
| Build half | Coffee end-to-end connected (129 tools); native agent task-capable; board mapped **TO DO → IN PROGRESS → IN REVIEW → COMPLETE**; first real card on the board | Create the Factory Planner agent (prompt ready); seed: 20 runs on a recurring low-risk source |
| Launch half | Designed; first increment = release record + evidence assembly (Prepare) | Build when a real launch needs it |
| Measure | Designed; Analyst pilot activates with first live users | — |
| Known gaps | named agent identity (Coffee side) · `task.activity` webhook unverified · approval-band UI is a Coffee proposal (interim: status + evidence comment) | tracked in `coffee-integration.md` |
