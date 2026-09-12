# Coffee × Techno OS — Integration Scoping

**Status:** v1.2, Sep 12 2026 · Connection **fully permissioned and verified end-to-end** — external client holds the full scope set, 129-tool MCP surface live, full task round-trip proven with audit attribution. Two environments: **pilot (current)** and **production (venture VPS)** — different credentials, different scope.

---

## 1. What exists today (verified, not claimed)

- **OAuth client** ("hermes", Server integration) in the Techno workspace; consent **re-executed Sep 12** after the permission expansion ("added permissions apply once each person authorizes the app again" — re-consent is the pattern to document for production too); refresh grant verified.
- **Granted scopes — full set:** `coffeeConnect.workspace.all` · `.meeting.all` · `.booking.all` · `.room.all` · `.service.all` · `.sharing.all` · `.templateAvailability.all` · `.user.all` · `.approval.all` + `messenger:read` `messenger:write`.
- **MCP surface: 129 tools** (up from 5): full task surface (create/update, statuses, checklists, comments, sprints, tags, types, custom fields, activity, agent runs), projects, documents, meetings (incl. transcription), intake, contacts, **files (base64 upload ≤ ~9.7 MB)**, **webhooks**, **agent-workflow repo ops (branches / pull requests / files)**, **agent approvals**.
- **Round-trip proof (Sep 12):** task `8bYcM2NpKePhco43TQkY9fX8` created via `PostTask` in the **Techno OS** project (`kyybetzjot9c`) · checklist item #17 added · comment #3965 added and read back · task activity trail shows both events with **`via_app: {"name": "hermes"}`** — the platform attributes actions to the external app.
- **Known gotchas:** browser UA required (Cloudflare); MCP needs `Accept: application/json, text/event-stream`; results paginate; chat messages still attribute to the consenting user (activity trail carries the app attribution — named agent identity remains an ask).
- **Workspace note:** the **Techno OS** project currently has statuses **TO DO / IN PROGRESS / COMPLETE** only — add **IN REVIEW** (or map PDLC stages onto statuses) before wiring the review flow.

## 1b. Strategic posture — native-first, external-capable (founder-confirmed, Sep 2026)

- **Techno OS is driven primarily by native Coffee agents** — agents created and running inside Coffee on its agent runtime. Rationale: dogfooding — the studio's daily operation exercises and expands Coffee's agent features; native agents keep all activity in the surface where humans review it.
- **External agents are the periphery, by invitation** — e.g. the founders' personal agents (Hermes and others) joining runs via MCP with their own identity and tools, sharing the same task/work contracts. BYO agents ≠ BYO practices.
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
| **Files / attachments** | ✅ | `PostFileUploadBase64` (`name` + `content_base64`; optional `folder_hash`; ≤ ~9.7 MB b64) |
| **Approvals** | ✅ | scope `coffeeConnect.approval.all` · `PostAiWorkApproval` · `PostAiAgentsTaskRunsApprove` / `Deny` / `Reply` / `Stop` / `RetryDelivery` · `PostAgentExecutionRunsApprovalsDecision` |
| **Agent workflow / repo** | ✅ | branches, pull requests, repository files (tree/get/put/delete) — native dev-workflow surface |
| **Projects / documents / intake** | ✅ | `PostWorkspaceProject`, document blocks, intake forms |
| **Meetings / recaps** | ✅ | meeting list/detail, transcription, agendas, docs, votes, feedback |
| **Events / webhooks** | ✅ | `PostWebhookSubscriptions {url, events}` + ping — push events replace polling |
| **Agent identity** | 🟡 partial | activity trail: `via_app: "hermes"` ✅; chat posts still show as the consenting user → named identity remains the open ask |

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

1. **Named agent identity** for integrations (activity attribution exists via `via_app`; chat display still human) — the last structural ask.
2. **Documentation of the in-app agent tool catalogue** (native agents) alongside the external 129-tool list.
3. **Sandbox/rehearsal workspace** for integration development.
4. **Rate-limit documentation** beyond the client's rpm setting; webhook delivery semantics (retries, signing).

## 6b. The dev ask — one-paragraph version (original, Sep 11; outcome below)

Roham — here's the Coffee API/MCP dev work that would fully open things up for Techno OS. We've connected an external OAuth client ("hermes") to the Techno workspace — Chat integrations are live (rooms, messages), which works well. To let our agents drive actual work, the key updates: (1) open the scope catalogue beyond `messenger:read`/`messenger:write` — the spec already marks ~74 operations as MCP-capable (the full task surface: create/read tasks, statuses, checklists, comments, tags, types, sprints — plus projects, documents, meetings, intake), but those scopes aren't grantable to external clients today, so agents can chat but can't touch a task; (2) add a file/attachment upload operation to the MCP set — it's the missing piece for evidence (recordings, screenshots, test output landing on task cards); (3) give integrations an agent identity so posts and actions are attributed to the agent, not to the consenting person; (4) push events (or documented poll limits) for messages and task activity so integrations can react in real time; (5) expose the approval surface (pause-for-approval decisions + the task agent-runs thread) so human-in-the-loop gates are automatable end to end.

**Outcome (Sep 12):** (1) ✅ scopes expanded — full `coffeeConnect.*` set grantable + granted · (2) ✅ file upload live (`PostFileUploadBase64`) · (3) 🟡 `via_app` attribution live in activity; named identity still open · (4) ✅ webhook subscriptions live · (5) ✅ approvals surface live (`approval.all`, task-run approve/deny). Round-trip verified. Thank you — now the dogfooding starts in earnest.

## 6c. Dogfood finding #1 (Sep 11) — custom-agent task ops (RESOLVED Sep 12)

**Reported:** custom agent checklist-add ✓ but task-create / status-change ✗ with *workspace validation errors* (likely unresolved `project_hash` / `task_status_hash` in tooling; repro in prior revision).
**Resolution (Sep 12):** custom agent created a task in Optimus OS successfully ("Tennis app UI design" → TO DO) + the external client round-trip fully verified. Finding closed; the loop (real use → precise repro → platform fix) worked end-to-end.

## 7. Next actions

1. **Add IN REVIEW status** to the Techno OS project (2 min in the UI) so PDLC stages map cleanly: TO DO → IN PROGRESS → IN REVIEW → COMPLETE.
2. **Create the Factory Planner agent** in Coffee (template ready: `docs/templates/planner-agent.md`) + the first real card in the Techno OS project.
3. **Subscribe a webhook** for task-activity events → notification pipeline (test with `PostWebhookSubscriptionsPing` first).
4. **Wire the first evidence upload** (file → card) to prove the evidence path end-to-end.
5. **Keep the pilot clean** — production stays a fresh mint on the venture VPS.
