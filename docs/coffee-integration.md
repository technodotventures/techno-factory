# Coffee × Techno OS — Integration Scoping

**Status:** v1, Sep 2026 · Baseline: connection live (verified end-to-end), Chat surface only. Two environments: **pilot (current)** and **production (venture VPS)** — different credentials, different scope.

---

## 1. What exists today (verified, not claimed)

- **OAuth client** ("hermes", Server integration) in the Techno workspace; consent approved; auth-code exchange 200; **refresh grant verified** — durable.
- **Granted scope so far: `messenger:read` `messenger:write` only.** The UI scope catalogue currently offers *only* Chat integrations — confirmed three ways (create-client modal, developer Events page, and 401 probes against `/task` + the scopes list).
- **Agent-callable surface:** 5 MCP tools — `ListMyWorkspaces`, `GetMessengerRooms`, `PostMessengerRooms`, `GetMessengerRoomsMessages`, `PostMessengerRoomsMessages` — plus their 4 REST equivalents under `/messenger/integrations/*`.
- **Live proof:** channel **"Techno OS"** created via API (members: the founders), first agent message sent and read back.
- **Known gotchas (documented in the `coffee-mcp-api` skill):** Cloudflare bans bare UAs (browser UA required); MCP requires `Accept: application/json, text/event-stream`; large results paginate; **API-sent messages attribute to the consenting user** (no bot identity yet).
- **Blocked pending scope exposure:** tasks, projects, files/attachments, automations/agent-workflow, approvals.

## 2. The two environments

| | **Pilot (now)** | **Production (venture VPS)** |
|---|---|---|
| Where | Current personal environment | Techno Ventures VPS (own deployment) |
| Purpose | Validate flows, build habits, notification plumbing, personal use | All studio-critical automation; the factory's real operating surface |
| Credentials | Current "hermes" client (pilot account) | **Separate OAuth client registered by the venture account** — never reuse pilot tokens |
| Data | Nothing venture-critical; experiments only | Venture data; evidence; approvals; audit-grade |
| Exit → next | Task scopes available (or API keys proven) + pilot used smoothly for 2+ weeks | — |

**Rule:** credentials never cross environments, in either direction. The pilot token lives on the pilot host only; production tokens get minted on the VPS, at deploy, with their own consent.

## 3. Surface map — what we need, per surface

| Surface | Today | Wanted for Techno OS | Enabling ask (Coffee team) |
|---|---|---|---|
| **Chat** (rooms/messages) | ✅ read/write | Run notifications, review pings, daily digests, message→intake bridge | — (works; agent identity would help, see below) |
| **Tasks** (create, statuses, checklist, automations) | ⛔ 401 | Factory intake (Discovery→task), statuses as pipeline stages, approval decisions on cards, evidence checklists | **Expose task scopes to OAuth** (or document workspace API keys) |
| **Files / attachments** | ⛔ 401 | Auto-publish evidence (recordings, test output) to the card | File/attachment scopes |
| **Automations / agent execution** | ⛔ 401 | Status-automation wiring; pause-for-approval surfaces; run limits | Agent-workflow + agent-execution scopes |
| **MCP-capable surface (platform)** | 74 ops marked `x-mcp` in the public spec — incl. 18 task ops (create/status/checklist/comments/agent-runs) | Disambiguate: in-app agents only, or externals too? Either way this is the target surface | Grant task/workspace scopes to OAuth clients (or confirm in-app-agent route) |
| **Meetings / recaps** | ⛔ | Recaps → structured decisions → tasks | Later; depends on task scopes |
| **Events / webhooks** | Polling only (chat cursors) | Push events for messages + task changes (or agreed poll cadence) | Webhook support or accepted poll limits |
| **Agent identity** | ⛔ messages appear as the consenting human | A named agent identity ("Techno OS") so factory posts are attributable and don't impersonate a person | Agent identities for integrations |

## 4. Stage 1 — Pilot scope (now, personal environment)

**Purpose:** make the connection useful immediately at personal scale, and pressure-test message discipline before production.

**Deliverables:**
1. **`coffee-notify`** — a small script the factory/sessions use to post structured updates to the "Techno OS" channel: `[run r-XX] <status> — <one-liner> · cost · link · needs-decision?(y/n)`. One writer, one channel, house format.
2. **Daily digest (optional)** — an agent summary of factory activity → one channel message per day.
3. **Intake bridge (manual)** — messages the founder posts in the channel can reference work ("r-72 looks good, merge it"); the agent reads and acts. Manual until task scopes exist; explicitly *not* an approval mechanism (silence never approves — approvals stay explicit).
4. **Personal use cases enabled now:** agent → Coffee notifications wherever the founder already reads; quick capture ("note to self" messages become Discovery candidates in the next session); the connection itself as the testing ground for the production client.

**Guardrails:**
- Post only in the dedicated channel (never DM-spam; never other rooms without explicit ask).
- **Never paste secrets or internal paths into messages** — messages are written to a third-party system; redaction applies.
- Attribution is understood (posts show as the founder) — so the agent never posts anything the founder wouldn't stand behind; transitional until an agent identity exists.

**Exit criteria:** used weekly without friction · task scopes live (or API keys proven) · no incidents from message handling.

## 5. Stage 2 — Production scope (venture VPS)

**Moves in production:**
1. **Credentials:** new OAuth client registered in the venture account; consent executed *at deploy time* on the VPS; tokens stored 0600 on the VPS; rotation policy; pilot tokens never reused.
2. **Agent identity:** request/bind a named identity for integration posts (replaces human attribution).
3. **Task integration (the real prize):** factory intake creates tasks; PDLC stages map to task statuses; evidence packages publish as attachments + checklist verdicts (the proposal set becomes implementable); approvals happen on cards; the pending-review queue reads the task surface directly.
4. **Autonomy wiring:** status automations call the factory; run limits + pause-for-approval mirror the guard set; spend/WIP counters stay factory-side.
5. **Reliability:** poll/consumption cadence agreed; failure handling (retry, backoff on 429); monitoring hooks; a sandbox workspace for rehearsal if Coffee provides one.

**Migration checklist (when VPS deploy starts):** [ ] venture client registered → [ ] scopes confirmed → [ ] consent + token mint on VPS → [ ] redirect URI strategy for server context → [ ] coffee-notify ported + channel re-bound → [ ] task-surface integration tested → [ ] pilot connection demoted to personal-only use (or retired).

## 6. Open questions for the Coffee team

1. **Scope roadmap:** when do task/file/automation scopes open to OAuth — or will workspace API keys be the documented path? (This is the single enabling change.) **New (Sep 11):** the public spec marks **74 operations `x-mcp`** including a full task surface — is that surface for in-app agents only, or can external OAuth clients be granted it? And can a **file/attachment upload** op be added (currently absent from the x-mcp set)?
2. **Agent identities:** can integrations post as a named agent?
3. **Events:** webhooks (chat + tasks) or documented poll limits?
4. **Sandbox:** a rehearsal workspace for integration development?
5. **Rate-limit documentation** beyond the client's rpm setting.

## 7. Next actions

1. **Check for workspace API keys** in Coffee settings (5 minutes; the REST surface has the routes).
2. **Build `coffee-notify`** (Stage 1, deliverable 1) — first living piece.
3. **Send the scope ask** to the Coffee team (screenshots attached; §6 questions).
4. **Keep the pilot clean** — this environment stays a pilot; production stays a fresh mint.
