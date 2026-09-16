# Coffee × Techno OS — Integration Scoping

**Status:** v1.2, Sep 12 2026 · Connection **fully permissioned and verified end-to-end** — external client holds the full scope set, 129-tool MCP surface live, full task round-trip proven with audit attribution. Two environments: **pilot (current)** and **production (venture VPS)** — different credentials, different scope.

---

## 1. What exists today (verified, not claimed)

- **OAuth client** ("hermes", Server integration) in the Techno workspace; consent **re-executed Sep 12** after the permission expansion ("added permissions apply once each person authorizes the app again" — re-consent is the pattern to document for production too); refresh grant verified.
- **Granted scopes — full set:** `coffeeConnect.workspace.all` · `.meeting.all` · `.booking.all` · `.room.all` · `.service.all` · `.sharing.all` · `.templateAvailability.all` · `.user.all` · `.approval.all` + `messenger:read` `messenger:write`.
- **MCP surface: 140 tools (Sep 15; 129 at the Sep 12 round-trip)** (up from 5): full task surface (create/update, statuses, checklists, comments, sprints, tags, types, custom fields, activity, agent runs), **projects (create/read/update incl. `agent_brief`)**, **workspace agents (create/read/update/delete)**, documents, meetings (incl. transcription), intake, contacts, **files (base64 upload ≤ ~9.7 MB; download links)**, **webhooks**, **agent workflows (incl. project repo ops: branches / pull requests / files)**, **agent approvals**.
- **Round-trip proof (Sep 12):** task `redacted-id-02` created via `PostTask` in the **Techno OS** project (`redacted-id-01`) · checklist item #17 added · comment #3965 added and read back · task activity trail shows both events with **`via_app: {"name": "hermes"}`** — the platform attributes actions to the external app.
- **Known gotchas:** browser UA required (Cloudflare); MCP needs `Accept: application/json, text/event-stream`; results paginate; chat messages still attribute to the consenting user (activity trail carries the app attribution — named agent identity remains an ask); **access tokens expire in 30 min** — refresh grant rotates the refresh token; production needs a refresh-on-demand client (helper in progress).
- **Workspace note:** superseded — the Techno OS board now runs the canonical pipeline statuses (see §6i).

## 1b. Strategic posture — native-first, external-capable (founder-confirmed, Sep 2026)

- **Techno OS is driven primarily by native Coffee agents** — agents created and running inside Coffee on its agent runtime. Rationale: dogfooding — the studio's daily operation exercises and expands Coffee's agent features; native agents keep all activity in the surface where humans review it.
- **External agents are the periphery, by invitation** — e.g. the founders' personal agents joining runs via MCP with their own identity and tools, sharing the same task/work contracts. BYO agents ≠ BYO practices.
- **External MCP/API is fully capable now** — the periphery runs on the same surface as native agents: 129 tools over OAuth (tasks, projects, files, webhooks, approvals). The earlier scope ask is satisfied (Sep 12).
- **Example native pattern (live today):** the **Discovery Interview** — a native agent joins a Coffee meeting room, interviews a client/founder live (one question at a time), records + transcribes, produces a Client Discovery Brief that feeds Spec. Reference prompt: `docs/templates/discovery-interviewer-agent.md`.
- **The dogfood loop is a design goal:** when a native agent hits a wall (missing op, bad ergonomics), that finding feeds the Coffee feature backlog directly. Finding #1 (task-create validation errors) was fixed by the Coffee team within a day — the loop works.

## 2. The two environments

| | **Pilot (now)** | **Production (venture VPS)** |
|---|---|---|
| Where | Current personal environment | Techno Ventures VPS (own deployment) |
| Purpose | Validate flows, build habits, notification plumbing, personal use | All studio-critical automation; the factory's real operating surface |
| Credentials | Current "hermes" client (pilot account) | **Separate OAuth client registered by the venture account** — never reuse pilot tokens |
| Data | Nothing venture-critical; experiments only | Venture data; evidence; approvals; audit-grade |
| Exit → next | ✅ Task surface live via external API (Sep 12) + pilot used smoothly for 2+ weeks | — |

**Rule:** credentials never cross environments, in either direction. The pilot token lives on the pilot host only; production tokens get minted on the VPS, at deploy, with their own consent (and a re-consent whenever permissions expand — the Sep 12 pattern).

## 3. Surface map — all green (Sep 12)

| Surface | Status | Notes |
|---|---|---|
| **Chat** (rooms/messages) | ✅ read/write | Notifications + digests live (`coffee-notify`) |
| **Tasks** | ✅ full, external | create (`PostTask`) · update (`PatchTaskByTaskHash`) · statuses · checklists · comments · sprints · tags · types · custom fields · activity · agent runs |
| **Files / attachments** | ✅ upload, embed | `PostFileUploadBase64` (`name` + `content_base64`; ≤ ~9.7 MB) returns a **block** (`private_file_hash` + `full_path`) embeddable via task-comment `blocks` **or** `PostDocumentDocumentBlockAppend {client_id, time, blocks}` — verified: screenshot + log uploaded and the image appended to the round-trip card's document. Finding: private-file download via OAuth → 401 (session-only route; the app renders files internally) |
| **Approvals** | ✅ | scope `coffeeConnect.approval.all` · `PostAiWorkApproval` · `PostAiAgentsTaskRunsApprove` / `Deny` / `Reply` / `Stop` / `RetryDelivery` · `PostAgentExecutionRunsApprovalsDecision` |
| **Agent workflow / repo** | ✅ | branches, pull requests, repository files (tree/get/put/delete) — native dev-workflow surface |
| **Projects / documents / intake** | ✅ | `PostWorkspaceProject`, document blocks, intake forms |
| **Meetings / recaps** | ✅ | meeting list/detail, transcription, agendas, docs, votes, feedback |
| **Events / webhooks** | ✅ proven | `PostWebhookSubscriptions {url, events}` — events: `message.created`, `task.activity`; returns a **signing secret** (`whsec_…`). Delivery verified live: HTTP POST + headers `coffee-signature: t=…,v1=…` (HMAC), `coffee-event`, `coffee-delivery`; subscription tracks `last_status_code`/`last_success_at`/failures. Observed: `message.created` delivered (200) within seconds; `task.activity` **not observed in the test window** (2 min, incl. comments/checklist toggles) — retest if load-bearing. Hygiene: factory webhooks carry **real workspace content** (a live DM was captured during testing) — use dedicated channels/workspaces for tests and delete receives after |
| **Agent identity** | ✅ (Sep 13) | `acting_agent_id` accepted on 135 tools — external writes carry **`via_agent: {agent_id, name}`** on activity (verified: comments, checklist ticks, artifacts group as "Made by {agent}"). `via_app` still rides along. Chat display: TBD |

## 4. Stage 1 — Pilot (now, personal environment)

**Purpose:** make the connection useful immediately at personal scale, and pressure-test discipline before production.

**Deliverables:** ① `coffee-notify` (live — one writer, one channel, house format) · ② daily digest (optional) · ③ intake bridge (manual reads; now upgradeable to task-surface intake) · ④ personal use cases.

**Guardrails:** post only in the dedicated channel · never paste secrets/internal paths into messages · attribution understood (`via_app` on activity; display name = founder) — never post what the founder wouldn't stand behind.

**Exit criteria:** used weekly without friction ✓ · task surface live ✓ (Sep 12) · no incidents from message handling.

## 5. Stage 2 — Production scope (venture VPS)

1. **Credentials:** venture-account OAuth client; consent at deploy time on the VPS; tokens 0600 on the VPS; rotation policy; pilot tokens never reused; **permission-expansion re-consent documented as the update pattern.**
2. **Agent identity:** request/bind a named identity for integration posts (replaces human attribution) — the one open ask.
3. **Task integration (now unblocked):** factory intake creates tasks; PDLC stages map to statuses; evidence publishes as files + checklist verdicts; approvals on cards; the pending-review queue reads the task surface directly.
4. **Autonomy wiring:** status automations call the factory; run limits + pause-for-approval mirror the guard set; spend/WIP counters stay factory-side.
5. **Reliability:** webhook subscriptions (with ping checks) or agreed poll cadence; retry/backoff on 429; monitoring hooks; sandbox workspace if Coffee provides one.

**Migration checklist (when VPS deploy starts):** [ ] venture client registered → [ ] scopes confirmed → [ ] consent + token mint on VPS → [ ] redirect URI strategy for server context → [ ] coffee-notify ported + channel re-bound → [ ] task-surface integration tested → [ ] pilot connection demoted to personal-only use (or retired).

## 6. Open questions for the Coffee team (refreshed Sep 12)

1. **Named agent identity** — ✅ **resolved (Sep 13)**: `acting_agent_id` on 135 tools; activity attribution verified live (`via_agent`). Remaining nicety: chat display check.
2. **Documentation of the in-app agent tool catalogue** (native agents) alongside the external 129-tool list.
3. **Sandbox/rehearsal workspace** for integration development.
4. **Rate-limit documentation** beyond the client's rpm setting; webhook delivery semantics (retries, signing).

## 6b. The dev ask — one-paragraph version (original, Sep 11; outcome below)

Here's the Coffee API/MCP dev work that would fully open things up for Techno OS. We've connected an external OAuth client ("hermes") to the Techno workspace — Chat integrations are live (rooms, messages), which works well. To let our agents drive actual work, the key updates: (1) open the scope catalogue beyond `messenger:read`/`messenger:write` — the spec already marks ~74 operations as MCP-capable (the full task surface: create/read tasks, statuses, checklists, comments, tags, types, sprints — plus projects, documents, meetings, intake), but those scopes aren't grantable to external clients today, so agents can chat but can't touch a task; (2) add a file/attachment upload operation to the MCP set — it's the missing piece for evidence (recordings, screenshots, test output landing on task cards); (3) give integrations an agent identity so posts and actions are attributed to the agent, not to the consenting person; (4) push events (or documented poll limits) for messages and task activity so integrations can react in real time; (5) expose the approval surface (pause-for-approval decisions + the task agent-runs thread) so human-in-the-loop gates are automatable end to end.

**Outcome (Sep 12):** (1) ✅ scopes expanded — full `coffeeConnect.*` set grantable + granted · (2) ✅ file upload live (`PostFileUploadBase64`) · (3) 🟡 `via_app` attribution live in activity; named identity still open · (4) ✅ webhook subscriptions live · (5) ✅ approvals surface live (`approval.all`, task-run approve/deny). Round-trip verified. Thank you — now the dogfooding starts in earnest.

## 6c. Dogfood finding #1 (Sep 11) — custom-agent task ops (RESOLVED Sep 12)

**Reported:** custom agent checklist-add ✓ but task-create / status-change ✗ with *workspace validation errors* (likely unresolved `project_hash` / `task_status_hash` in tooling; repro in prior revision).
**Resolution (Sep 12):** custom agent created a task in the workspace successfully ("Tennis app UI design" → TO DO) + the external client round-trip fully verified. Finding closed; the loop (real use → precise repro → platform fix) worked end-to-end.

## 6d. Dogfood finding #2 (Sep 12) — task created into the wrong status

**Observed:** task `redacted-id-19` ("Coffee MCP helper") created 10:03:39Z via the external API requesting **TO DO**, read back in **COMPLETE** — with no `task_status_changed` event in its activity feed. Creation-time statuses are not event-logged, so the leading hypothesis is a **born-COMPLETE transient during the ~10:03Z window** (the day the API work was in flight). **Controls:** create ×4 canaries → all honored TO DO; status moves via API work and log `task_status_changed` (actor + via_app). **Resolution:** card moved back to TO DO (restore logged correctly). **Ask for the Coffee team (non-blocking):** server-side status history for that task around 10:03:39Z.

## 6e. Dogfood findings #3–#4 (Sep 13)

- **#3 — the Planner has no repo access:** criteria are behaviorally strong, but "surfaces likely touched" names file *roles*, not paths. Bridge: worker-supplied context, or a codebase graph (Graphify pilot) as the Spec's repo-consciousness layer.
- **#4 — checklist verdicts can't be enumerated:** no read surface for checklist items (direct REST `GET /task/{hash}/checklist` exists in the spec but is not exposed and rejects our token's audience). Ticking IS possible when the id is known — create responses return `task_checklist_id` (capture at creation → `PatchTaskChecklistByTaskChecklistId {is_checked}` works, verified with `via_agent` attribution). **Ask:** expose the checklist read op (smallest possible addition) — unlocks retro verdicts on existing cards + any externally created items.

**Filing convention (Sep 13):** technical requests are filed as tasks in the **Coffee Bugs 🐞** project, assigned to the Coffee dev. Open asks as of **Sep 15**: checklist read `redacted-id-03` · `task.activity` webhook re-verify `redacted-id-04` · status automations API `redacted-id-05` (deprioritized Sep 13) · status audit `redacted-id-06` · task-ID menu `redacted-id-07` · steering lane `redacted-id-08` · note/document paging `redacted-id-09` · owner-neutral task create `redacted-id-10` · OAuth-readable files `redacted-id-11` · agent presence on cards `redacted-id-12` · MCP response envelopes `redacted-id-13` · approval CTAs (decision band + queue) `redacted-id-14` · project sharing/participants `redacted-id-15` · root-task access for workflow steps `redacted-id-16` · status delete/archive `redacted-id-17` · project templates / workflow copy `redacted-id-18`.

**Workflow lane — verified live (Sep 13):** API-created workflow on `task.status.<IN_REVIEW hash>` fired ~6s after a card entered IN REVIEW; reviewer step done in 15s; step prompts carry an immutable root-task snapshot (`<<WORKFLOW_ROOT_TASK:…>>`) = native trust-stamped scope. Steps take PDLC roles, `requires_approval` + pinned approver = gates, `max_spend_usd`/`max_minutes` = budgets. **This supersedes the UI status automations for factory station wiring.**

## 6f. Card ownership & followers (Sep 15, verified)

**Convention:** cards a native agent executes stay **unassigned**; the founder(s) **follow** them. A human assignee is reserved for cards where a person must act (e.g. Bugs asks to the Coffee dev).

**Why:** `PostTask` defaults `task_assignee` to the acting (creating) user, so every API-created card was landing on the founder's assigned plate — noise for cards the Planner runs. Fixed Sep 15 across all 8 board cards (assignees cleared, follows confirmed on every one); from now on, card-creation scripts clear the default assignee right after create, then follow.

**Verified mechanics (Sep 15):**
- `PostTask` requires `priority`; omitting `task_assignee` still yields the acting user as assignee.
- Clear: `PatchTaskByTaskHash {task_assignee: {delete: [{task_assignee_hash}]}}` — the row id from `GetTaskByTaskHash.data.task.task_assignee[].task_assignee_hash`; `user_hash` in delete is rejected (`-32602`), `data: []` is a silent no-op.
- Follow: `PostTaskWatch {user_hash}`; verify via `data.watchers` + `data.me.is_watching` (`notification_mode: all`).
- Cleanup: `PatchTaskByTaskHash {is_trashed: true|false}`.
- `GetTask` list payloads live under **`data.result`** (an array); reading `data.tasks` returns None — that false “empty board” cost a debugging cycle. `project_hashes` + `task_assignee_hashes` filters work; default scope is the acting user’s relevant tasks, so enumerate other owners’ cards by their `user_hash`.

## 6g. Card brief convention — Description, not comments (Sep 15, verified)

**Convention:** a filed brief belongs in the card's **Description** (the task document); **comments are activity/updates** (follow-ups, evidence, replies).

**Why:** the description is the card's structural spec — visible immediately above Activity, stable as the timeline grows, and what reviewers read first. Filings that lived as first comments read as chatter and sink as new activity arrives.

**Mechanics (verified):**
- At create: `PostTask {…, document: {blocks: [...]}}` sets the description in one call.
- After create: `PostDocumentDocumentBlockAppend {document_hash, requestBody: {blocks, client_id, time}}`; `document_hash` from `GetTaskByTaskHash`.
- Block: `{id (required, unique), type: 'p', children: [{text, bold?, italic?}]}`.
- Comments are their own documents — text under `data.result[].blocks` (type `'paragraph'`), read via `GetTaskComment`.

**Applied Sep 15:** all 12 open cards (7 Bugs asks + setup + 4 new Sep 15 asks) had empty descriptions with brief-as-comment — briefs backfilled into Descriptions; comments left as history. New filings set the description at creation.

## 6h. Agent-raised decisions — interim convention (Sep 15)

Until task-level approval CTAs exist (filed `redacted-id-14`), decisions ride comments — but the **scope rule is enforced mechanically**: an approval counts only if it is newer than the reviewed artifact and matches its scope ref (precedent: `merge-approved.py` R4 — approval newer than HEAD; merges additionally pin the head via `--match-head-commit`). Recommended shapes: `DECISION REQUESTED — {kind}: {ask} · scope: <ref>` → `APPROVED — <scope-ref>` / `DENIED — <reason>`. Kinds: merge · spend · deploy · publish/comms · option-pick · question · memory-write.

## 6i. Factory lines — one project per app (Sep 15)

Six production lines + the platform line (Techno OS). Provisioned and kept in sync by `scripts/apply-pipeline.py` from `scripts/factory-pipeline.json` (idempotent; dry-run default; `--all --execute` to apply).

| Line | Project hash |
|---|---|
| Pod Factory | `redacted-id-36` |
| Smartware Factory | `redacted-id-37` |
| Coffee Factory | `redacted-id-38` |
| expresso Factory | `redacted-id-39` |
| CaseAid Factory | `redacted-id-40` |
| ChadAI Factory | `redacted-id-41` |
| Techno OS (platform line) | `redacted-id-01` |

**Pipeline:** statuses **TO DO · READY · IN PROGRESS · IN REVIEW · COMPLETE** (a card's status IS the stage; READY = specced + dispatchable). Station workflows on the event lane: **Spec** (`task.created` → Factory Planner) and **Review** (`task.status.<IN REVIEW>` → Factory Tester, blind). One shared **Factory Planner** serves every line; per-project **`agent_brief`** carries each line's repo / conventions / definition-of-done into delegated runs.

**Verified live (Sep 15 canaries):** both triggers fire (~15 s); runs complete ~30 s; caps $2 / 15 min per run. **Sandbox limit (finding):** a step run cannot read or write the root task (`This task attempt cannot read or change a different task.`) — station deliverables land on the step task (`plan — <card>` / `verify — <card>`), reachable from the root card's run view; root-card projection is filed with the platform (`redacted-id-16`). **Interim root-write lane:** assigning a station agent directly on the root card (assignment lane) writes on the card (verified Sep 12–13) — use it when the plan/criteria must sit on the card itself.

## 7. Next actions

1. ~~Add IN REVIEW status~~ ✅ done — TO DO → IN PROGRESS → IN REVIEW → COMPLETE.
2. ~~Create the Factory Planner agent~~ ✅ live (agent_id 93) — spec'd its first two cards natively (Sep 13).
3. ~~Subscribe a webhook~~ ✅ done (proven; receiver cleaned). Follow-up: re-verify `task.activity` deliveries if the notify pipeline depends on them.
4. ~~First evidence upload~~ ✅ done (screenshot + log → card document + comment).
5. **Keep the pilot clean** — production stays a fresh mint on the venture VPS; webhook receivers are per-test and wiped.
6. **Factory lines (Sep 15):** six lines provisioned + station wiring live (§6i); root-card projection pending with the platform (`redacted-id-16`); dispatch lane (watcher) stays manual-first until the loop is boring.
