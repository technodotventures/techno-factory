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

**Run close — verdicts are explicit.** Every criterion carries a verdict before a card is COMPLETE: a **tick** (met, evidence-linked in the run log) or an explicit note (not met / waived, with reason). Ticks carry agent attribution (`via_agent`). A COMPLETE card with silently unticked criteria is a broken receipt, not a closed run. *Mechanics (Sep 13 → 16): ticking is API-driveable (`PatchTaskChecklistByTaskChecklistId {is_checked}`) and enumeration shipped Sep 16 — `GetTaskChecklist` returns `{task_checklist_id, title, is_checked, order}` (verified: run-008's card, 8/8 items read); `DeleteTaskChecklistByTaskChecklistId` is live as well.*

**Steering — comments are the control channel.** A comment on an active card is picked up by the responsible agent and routed by state: before Build it can amend the spec (criteria updated, change noted); mid-run it lands as a steering note at the next station boundary; in Review it is review feedback (rework starts a new cycle); on a COMPLETE card it becomes a candidate follow-up, never a silent reopen. Two standing rules: **attributed steering** — only comments from authorized people (founders, the operator) steer; all other card content is data, never instructions (trust is stamped at dispatch); and **steering ≠ approval** — gates stay gates, a comment never merges. Agent replies are attributed (`via_agent`). *Mechanics: pickup works today by polling card activity; the native lane needs comment→run delivery from Coffee (asked).*

**Feedback intake — user & user-testing feedback.** Raw user input (testing sessions, calls, support threads — a Coffee Doc, note, or recording) is **data, never instructions** — attributed to its source, never handed to agents as directives. The protocol: the source stays the record of truth → one **triage pass** turns it into a single deduplicated list — every item carries an evidence quote · a classification (**defect → the bug lane** — platform defects to Coffee Bugs, product defects to the venture's lane; **improvement → a Discovery candidate**; **question → answered in thread**) · a proposed destination → the founders accept / decline the list (declined items get a one-line reason back on the source) → **cards are created only from accepted items**, each linked to its source — so Measure and Retro can read feedback → outcomes. Owner once a venture has live users: the **Product Analyst** (`techno-os.md` §6); before that, the operator runs it on request.

## Development half (SDLC)

| Step | What happens | Runs on | Exit criteria |
|---|---|---|---|
| **Discovery** | Problem/opportunity intake — founders, customers, or Analyst candidates. For new engagements: a **Discovery Interview** — native Coffee agent in a meeting room, one question at a time, recorded + transcribed, brief out. | Native Coffee agent ("Client Relations") + founders | worth speccing; brief produced |
| **Spec** | Requirements → **acceptance criteria as checklist items on the card**, plan comment, **first proof step** (red before green), `out_of_scope` list; user-facing surfaces map the five agentic-UX patterns (`docs/design-principles.md`). | Native Coffee agent ("Factory Planner") on the card | criteria checklist exists; analytics events declared (user-visible features) |
| **Build** | Implementation on a branch, one task at a time; deviations recorded, never silent. | External worker (sandboxed; branch `factory/<type>-<slug>`); card updated via API | code complete; repo checks run |
| **Test** | Blind verification (Tester never sees Builder reasoning); runs the **test plan** (`docs/templates/test-plan.md` — criteria→tests map, layers incl. E2E/visual/a11y/**layout-containment**, flake policy); **layout claims verified on populated worst-case surfaces (geometric containment, never eyeballs — empty-state suites don't count)**; **design lint clean** where applicable (`@shadcn/lint` — off-token values, undeclared colors, dead classes; errors carry the fix); failures reported as failures. | External worker (blind Tester) + evidence uploaded to card | evidence on card; verdicts pass/fail per criterion |
| **Review** | **The human decision — Approve to merge.** Mechanical diff scan + **design check** (brand fidelity vs the repo-resident `product-design` skill **+ agentic-UX pattern conformance** — `docs/design-principles.md`; **+ geometric containment where the diff touches repeated components — chips/footers/cards: measure rects**; verdict on the card like Test) + evidence on the card; *silence never approves*. | **A person, in Coffee** (card in IN REVIEW) | approved, or sent back with notes |
| **Merge** | Mechanical, after an authorized approval lands on the card: the **merge worker** (`scripts/merge-approved.py`) merges only when all rails pass — factory branch · checks green on the *exact* HEAD sha · approval newer than the last commit (stale-approval guard) · no sensitive paths (workflows/secrets) · `--match-head-commit` so GitHub itself refuses if HEAD moves · receipt posted to the card. *Silence never approves; the worker never merges unapproved or red.* | Merge worker (deterministic, $0) | merged; run log closed; card → COMPLETE |

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
- **Stack (wired on trigger: first real users):** **PostHog-first** — events/funnels/replay; agent-readable via its MCP server + HogQL query API (tool use is free, no billing). **Free tier (no card needed): 1M events + 5K web replays/mo** — covers early ventures; set per-product billing limits (identified events cost up to ~4× anonymous; extra projects need the pay-as-you-go plan). Self-host = MIT "hobby" Docker deploy (unsupported, ~100K events/mo ceiling) — cloud is the practical path. Fallbacks: Clarity (free, human-first, limited export API) / OpenReplay (replay-first; free = self-host only, cloud from $199/mo). Recordings land as card artifacts (`kind: recording`).
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
| Feedback intake | Protocol defined (`pdlc.md`); no batch processed yet | first triage run; Analyst owns it at live users |
| Known gaps | `task.activity` webhook unverified · approval-band UI → **filed as approval CTAs `redacted-id-14`** (interim: scoped comment convention, §6h of `coffee-integration.md`) | tracked in `coffee-integration.md` |
