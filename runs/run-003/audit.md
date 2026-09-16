# Run 003 — Pod Capabilities module UI audit (draft)

- **Status:** draft for run review. Read-only audit; **no code changes**.
- **Repo:** `technodotventures/pod` — audit tree = **`c9889ae`** (branch tip of `main`; audited via the local `pod-run005` worktree, whose tree is byte-identical to `c9889ae` — `git diff --stat ad70201 c9889ae` → empty).
- **Run card:** `redacted-id-23` — "Pod capabilities module — UI audit + improvement" (Techno OS project `redacted-id-01`). Plan comment = `runs/run-003/card-comments.md`.
- **Date:** 2026-09-14 (UTC). Auditor: factory verifier (run 003).

---

## 1. Method + sources

### 1.1 Spec of record (PRD)

- The governing PRD is **"Pod Capabilities PRD"** — a Coffee workspace note, `note_hash redacted-id-31` (`document_hash redacted-id-32`; markdown twin note `redacted-id-33`, doc `redacted-id-34`), created 2026-08-07. It is named as the "Spec of record" in the run card plan (card-comments.md:5).
- **PRD note text not directly readable by the factory at audit time** (Coffee MCP truncates large notes: `{"truncated":true,"message":"Result exceeds the tool budget…"}` on `GetDocumentNoteByNoteHash`, `GetDocumentByDocumentHash`; no paging params exposed; REST fallback is scope/resource-gated 401; the browser session is not authenticated to the workspace). **Grading basis: card criteria + spec section mapping; verbatim cross-check pending a native-agent fetch.**
- Section/ID mapping used for citations (per card spec, card-comments.md:5 and :25–:33): **§15.1** capability cards, **§15.2** review panel, **§15.3** freshness language, **§15.4** empty/failure states; **§9** revision/deployment lifecycle vocabulary; **CAP-LIB-001** (separate aggregates), **CAP-ING-006** / **CAP-LIB-004** (Inbox vs Library), **CAP-SRC-004** (source freshness/health), **§16** (deployed without target verification), **§11** (source adapters — out of scope here), **CAP-PLG-003** (inspection engine — out of scope, UI display only).
- The card's 12 acceptance criteria (the audit's grading checklist) are transcribed in §5 below.
- Note on the entry point: `/pod/capabilities` is the **protocol discovery route** (`README.md:90`) and stays unchanged by design (ADR-0002 decision 9). The product Capabilities surface is the cockpit nav key `skills`, label **"Capabilities"** (`ui/src/main.tsx:725`). Findings below reference the product surface.

### 1.2 Code paths read (tree `c9889ae`)

| Area | Path |
|---|---|
| Skill routes | `src/routes/skills.ts` (list `:87`, content `:109`, create `:173`, revisions `:267`, approve `:275`, reject `:298`, scan `:320`, deploy preview `:362`, deploy `:389`, enable `:433`, agents `:507`, disable `:579`, delete `:616`, registry proxies+cache `:648–:760`) |
| Plugin routes | `src/routes/plugins.ts` (list `:63`, get `:75`, import/inspect `:84`, approve `:169`, reject `:191`, delete `:203`) |
| Adjacent | `src/routes/agents-registry.ts`, `src/services/agent-profile-manifest.ts`, `src/capabilities/plugin-package.ts`, `src/pod/db.ts` (revision capture `:2401`, `:2882`; `created_by` cols `:202`, `:263`) |
| UI | `ui/src/main.tsx` — nav `:725`; command-palette entry `:3441`; App data load `:3128–:3142`, refresh callback `:3761–:3777`; `CapabilitiesView` `:15422`; Inbox `:16050–:16111`; Library `:16113–:16170`; Deployments `:16172–:16231`; Discover (`SkillsBrowseTab`) `:14766–:15420`; skill review panel `:15808–:15884`; plugin review panel `:15886–:15976`; card renderers `:16064–:16104`, `:16127–:16163`; `ui/src/styles.css` (badge/chip classes `:9263`, `:19875–:20100`) |
| Docs | `docs/adr/0002-capabilities-module.md`, `CONTEXT.md` (glossary: Inbox/Library/Deployment/Partial deployment/Compatibility/Drift) |

### 1.3 How UI states were determined

- **Static read** of the tree above (primary basis for every finding).
- **Live pass performed** (before the mid-run instruction to skip it; evidence retained): disposable local instance of `c9889ae`-equivalent tree on Node `v26.5.1`, API `127.0.0.1:8937`, UI `127.0.0.1:5297`, isolated data dir `/tmp/pod-audit003` (seeding was local and disposable, per card rule). States captured by DOM text + screenshots: first-run onboarding → cockpit; Capabilities empty Inbox / Library / Deployments; then a seeded **Skill** (r1 approved to Library, r2 draft that rewrote `SKILL.md` and added `reference/cheatsheet.md`) and a seeded **Plugin** (r1 draft: 1 nested Skill, 2 MCP servers, incl. one stdio + one streamable-http); Inbox cards, Library card, both review panels, type filter, and the Discover surface (live registry results from ClawHub). Server stopped after capture; no tracked-file changes (`git status` clean in the worktree).
- **Limits of the live pass:** a11y contrast/axe not run; no visual diffing beyond manual inspection; states not reachable without external services (OAuth agent connection, real native agent skill directories) were graded from code and are marked *unverified live* where relevant.

---

## 2. Surface inventory (first proof step)

Every capability surface, its implementation, and whether the audit reached it live:

| # | Surface | Implementation | Reached live |
|---|---|---|---|
| S1 | Capabilities entry (nav key `skills`, label "Capabilities") | `ui/src/main.tsx:725`; palette `:3441` | ✓ |
| S2 | Tab shell: Inbox / Library / Deployments / Discover | `main.tsx:15980–16001` | ✓ |
| S3 | Aggregate type filter (All / Skills / Plugins) | `main.tsx:16021–16031` | ✓ (filters correctly) |
| S4 | Inbox list (skills+plugins merged) + counts | `main.tsx:16050–16111` | ✓ (empty + populated) |
| S5 | Library list (skills+plugins merged) + status | `main.tsx:16113–16170` | ✓ (empty + populated) |
| S6 | Skill review panel (inbox context) | `main.tsx:15808–15884` | ✓ (r2 draft vs r1 approved) |
| S7 | Plugin review panel (inbox context) | `main.tsx:15886–15976` | ✓ |
| S8 | Deployments surface | `main.tsx:16172–16231` | ✓ (empty state) |
| S9 | Discover / source search | `main.tsx:14766–15420`, rendered `:16036–16048` | ✓ |
| S10 | Agent-assignment modal (per skill) | `main.tsx:16233–16285` | code only |
| S11 | Topbar actions: Import Plugin, Scan agents | `main.tsx:16002–16018` | ✓ (Scan agents ran; no findings on host) |
| S12 | Backend shape feeding the UI | `src/routes/skills.ts`, `src/routes/plugins.ts` | ✓ (probed) |
| S13 | Skill/Plugin data load + refresh path | `main.tsx:3128–3142`, `:3761–3777` | ✓ (no polling; see F1) |

Adjacent, out of scope: `LearningsView` (no capability role), `agents-registry` UI in Connections.

---

## 3. Ranked findings (by user harm)

Severity key: **H** = trust/correctness or blocked core flow; **M** = requirement breach with usability/completeness impact; **L** = edge/limited impact.

Trust-critical class is ranked first (per card risk note, card-comments.md:41).

---

### F1 — No freshness or source-health language anywhere in Capabilities; Discover serves cached registry data as if live (H)

- **Requirement breached:** §15.3 freshness language / CAP-SRC-004 (per card spec; card-comments.md:29, :41).
- **Route/state:** Cockpit → left nav "Capabilities" → **Discover** (`SkillsBrowseTab`, `main.tsx:14766`) with registry results rendered (state: any non-empty Discover, or Inbox/Library with data).
- **Expected:** for a cached or polling source the rendered UI says so explicitly — e.g. "Cached result, N minutes old", "Never synced", per-source health/failure state; capability lists show when they were last refreshed.
- **Observed:**
  - The skills.sh registry catalog is **server-cached for 5 minutes** (`src/routes/skills.ts:697–714`, `SKILLSSH_CACHE_TTL = 5 * 60 * 1000`; response carries only `{skills,total}` — no cache age). The UI renders these as current with **bare source chips** ("ClawHub" / "SkillsMP" / "skills.sh") and no age or cache disclosure (`main.tsx:15328–15332`, `:15374–15378`).
  - Partial registry failures are **swallowed silently** (only `console.warn`): ClawHub proxy/direct failure `main.tsx:14831–14847`, skills.sh failure `:14886–14889`, SkillsMP failure `:14912–14915`. The "Could not reach skill registries — showing featured skills" notice fires **only when every source returns zero** (`:14934–14940`); a partial outage renders a shorter list with no health indicator.
  - The Inbox/Library snapshots are fetched **once** at app load (`main.tsx:3128–3142`) and only re-fetched after user actions (`:3761–3777`; no capability polling — the app's only 5-minute interval `:3208` is connection sync). No "as of / last updated" timestamp is shown anywhere.
  - Live scan of the entire Capabilities view text returned `cached:false, freshness:false, last sync:false, synced:false, stale:false, updated:false`.
- **Repro steps:**
  1. Start the dev stack with a fresh data dir (`npm run dev:all`, isolated `COFFEE_POD_DATA_DIR`).
  2. Complete onboarding via "Set up later"; open **Capabilities → Discover**.
  3. Observe results with source chips but no fetch/cache age.
  4. Call `GET /pod/skills/registry/skillssh/skills?view=trending` twice within 5 minutes from the same Pod — identical payloads, no age field (server cache, `skills.ts:697–714`).
  5. Optionally stop access to one registry host and reload Discover: list shortens with no failure indicator (console-only warning).
- **Evidence:** `ui/src/main.tsx:14810–14940`, `:15328–15332`, `:15374–15378`, `:3128–3142`, `:3761–3777`; `src/routes/skills.ts:697–714`; live DOM scan (2026-09-14, UI 5297).

---

### F2 — "Local files / Directory found" claims an on-disk install that was never verified (H)

- **Requirement breached:** §16 (showing deployed/installed without target verification — per card spec, card-comments.md:41); conflicts with §9 vocabulary ("deployment" = materialization into the agent's native directory **followed by digest verification**; CONTEXT.md).
- **Route/state:** Capabilities → **Inbox** → click a Skill card whose revision has package files (also reachable from Library for an approved revision). Reproduced live with a skill that was never deployed to any agent.
- **Expected:** distinguish "canonical revision retained by Pod" from "materialized into an agent's native directory and digest-verified". The "Local files" affordance (and the word "found") should appear only when a verified deployment exists.
- **Observed:** the panel shows **"LOCAL FILES — Directory found — Canonical revision 2"** although no agent is assigned and no files exist on disk. `renderLocalFiles()` renders "Directory found" whenever `skillContent` is non-null (`main.tsx:15753–15772`), and `skillContent` is populated from the **revision's package files in Pod** (`:15446–15464`) — never from a filesystem check; the "directory" value is literally `Canonical revision N` (`:15454`; server side `src/routes/skills.ts:131`).
- **Repro steps:**
  1. Seed a Skill with files (`POST /pod/skills`, body with `files`) — no agents connected.
  2. Open **Capabilities → Inbox**, click the Skill card.
  3. Observe section "LOCAL FILES" → "Directory found" + "Canonical revision N".
  4. Inspect the data dir / agent skill directories: nothing was written; no deployment record exists (`GET /pod/skills` → `deployments: []`).
- **Evidence:** `ui/src/main.tsx:15753–15772`, `:15446–15464`; `src/routes/skills.ts:116–134`; live capture (2026-09-14).

---

### F3 — Skill revision review shows no change disclosure: no diff, no instruction-vs-resource distinction (H)

- **Requirement breached:** §15.2 review panel (card criterion 8: "distinguishes instruction-file changes from resource changes for a Skill revision; absence is a finding"); §9 revision vocabulary (per card spec).
- **Route/state:** Capabilities → **Inbox** → open a Skill whose pending revision differs from the approved one (reproduced: r2 rewrote `SKILL.md` and added `reference/cheatsheet.md` vs approved r1).
- **Expected:** the review surface shows **what changed** — at minimum a changed/added/removed file list with the pending revision classified (instruction files vs resource files), so approval is informed.
- **Observed:** the panel renders one flat list of file chips for the incoming revision and the raw markdown of the primary file (`main.tsx:15852–15862`). There is no diff against the previous revision, no added/removed markers, and no instruction-vs-resource classification; revision history rows show only `r2 · v1.3.0 DRAFT` / `r1 · v1.2.0 APPROVED` (`:15827–15839`). Approve/Reject sit next to this (`:15863–15868`) with no change summary between the reviewer and the decision. The plugin side has a section labelled "Capability diff", but Skills — the surface this criterion names — have none.
- **Repro steps:**
  1. Seed a Skill (`POST /pod/skills`), approve r1 (`POST /pod/skills/:id/revisions/:rid/approve`).
  2. Re-post the same `source_slug` with a rewritten `SKILL.md` and one added resource file → r2 draft.
  3. Open **Capabilities → Inbox**, click the Skill card.
  4. Observe: file chips + raw content only; no changed-file list, no instruction/resource split, no comparison to r1.
- **Evidence:** `ui/src/main.tsx:15808–15883` (esp. `:15827–15839`, `:15852–15862`, `:15863–15868`), approve/reject handler `:15521–15541`; live capture (2026-09-14).

---

### F4 — Review panels do not show who proposed the revision (M)

- **Requirement breached:** §15.2 "…and who proposed it" (card criterion 11).
- **Route/state:** Both review panels (Skill: `main.tsx:15808`; Plugin: `:15886`), inbox context, any pending revision.
- **Expected:** proposer identity (and time) for the pending revision.
- **Observed:** the skill meta grid shows Revision / Version / Package / Origin / Detected (`:15818–15825`); the plugin grid shows Revision / Version / Package / Format / Origin / Author (`:15902–15910`) — "Detected" is a timestamp, "Origin" is the source (manual/local), "Author" is the package author. The revision's `created_by` is persisted and returned by the API (`src/pod/db.ts:202`, `:2443`; live payload `created_by: "person-local"`) but is **not rendered** anywhere in either panel.
- **Repro steps:**
  1. Seed any Skill/Plugin (as F2/F1 repro).
  2. Open **Capabilities → Inbox** → click the card.
  3. Search the panel for the proposer: absent. Compare with `GET /pod/skills` → `pending_revision.created_by`.
- **Evidence:** `ui/src/main.tsx:15818–15825`, `:15902–15910`; `src/pod/db.ts:202`, `:2401–:2443`, `:2882–:2931`; live capture (2026-09-14).

---

### F5 — Capability cards omit freshness and risk (and component/deployment counts for Skills) (M)

- **Requirement breached:** §15.1 capability cards (card criterion 5: type, name, description, revision, source, freshness, component counts, risk summary, Library/Inbox status).
- **Route/state:** Capabilities → **Inbox** or **Library**, any populated list (card renderer `main.tsx:16064–16104`, `:16127–16163`).
- **Expected:** each card carries the §15.1 field set.
- **Observed:** cards have **type** (text chip "SKILL"/"PLUGIN" + icon `:16071`, `:16093`), **name**, **description**, **revision** (`r2` / `Draft v1.3.0`), **source** badge, and **Library/Inbox status** ("In Library", "Update waiting"; `:15781–15795`). **Missing:** *freshness* on all cards (no age/as-of anywhere); *risk summary* on all cards (plugin risk exists only inside the plugin detail panel, `:15931–15949`); *component counts* only on Plugin tiles (`1 Skills / 2 MCP`, `:16076–16079`, `:16137–16140`) — Skill tiles show no package/component count; *deployment count* nowhere on cards (only in the Deployments tab).
- **Repro steps:**
  1. Seed a Skill and a Plugin (as above); open **Capabilities → Inbox**.
  2. Compare the visible card fields against the §15.1 list: no freshness, no risk, no counts on the Skill tile.
  3. Open **Library** (approved skill) — same gaps; open the plugin detail to see risk appears only there.
- **Evidence:** `ui/src/main.tsx:16064–16104`, `:16127–16163`, `:15781–15795`, `:15931–15949`; live captures (2026-09-14).

---

### F6 — One merged list renders for Skills and Plugins; no separate aggregate list views (M)

- **Requirement breached:** CAP-LIB-001 (per card spec: "if they are one merged list, that itself is a finding"; card-comments.md:23).
- **Route/state:** Capabilities → **Inbox** or **Library**, default filter "All".
- **Expected:** Skills and Plugins navigable as distinct aggregate types under the one Capabilities entry (per ADR-0002 decision 1: separate Skill and Plugin aggregates).
- **Observed:** both sections render **a single merged grid** — plugins first, then skills (`main.tsx:16064–16105` inbox; `:16127–16163` library). A working type filter exists (`All | Skills | Plugins`, `:16021–16031`) and per-card kind chips/ semantics are correct (nested plugin skills are *not* flattened — plugin detail lists components separately, `:15886–15930`, consistent with ADR-0002 decision 5), but there is no dedicated Skills list view or Plugin list view: the aggregate types are not separately navigable.
- **Repro steps:**
  1. Seed one Skill and one Plugin; open **Capabilities → Inbox** (default "All").
  2. Observe a single list containing both; note ordering mixes aggregate types.
  3. Use the type filter to narrow — confirms filtering exists but there are no per-type views/routes.
- **Evidence:** `ui/src/main.tsx:15484–15487`, `:16064–16105`, `:16127–16163`, `:16021–16031`; `docs/adr/0002-capabilities-module.md` (decisions 1, 5); live capture (2026-09-14).

---

### F7 — Library exposes only a type filter; tag / compatibility / source / risk / freshness / deployment / update-state filters absent; no local search (M)

- **Requirement breached:** §15 Library filters (card criterion 9: "…filters for type, tag, compatibility, source, risk, freshness, deployment and update state — each filter actually filters").
- **Route/state:** Capabilities → **Library** (also Inbox), any populated list.
- **Expected:** the eight filter dimensions, each operational.
- **Observed:** only **type** exists (`main.tsx:16021–16031`); it does work (live: Plugins→0 shows empty state, Skills→1 shows the card). There are **no controls** for tag, compatibility, source, risk, freshness, deployment, or update state anywhere in the section (`:16113–16170` renders only the grid/empty state), and no text search — the app-level "Search your mind…" bar is memory search, not capability search. "Update waiting" exists as a per-card chip (`:16144`, `:16160`) but not as a filter.
- **Repro steps:**
  1. Open **Capabilities → Library** with ≥1 capability.
  2. Enumerate the available filter controls: only All/Skills/Plugins.
  3. Attempt to filter by source, risk, freshness, update state, tag, deployment state: no UI exists.
- **Evidence:** `ui/src/main.tsx:16021–16031`, `:16113–16170`, `:16144`, `:16160`; live capture (2026-09-14).

---

### F8 — Plugin review panel's "Capability diff" is a composition list, not a change view (M)

- **Requirement breached:** §15.2 review panel ("shows what changed", card criterion 11); §9 lifecycle vocabulary (per card spec).
- **Route/state:** Capabilities → **Inbox** → open a Plugin with a pending revision (reproduced with r1; the gap is structural for re-imports).
- **Expected:** for a review of revision N, show what changed vs the retained revision (added/removed/changed components, status changes) — the section is even named "Capability diff".
- **Observed:** the section renders the incoming revision's own component composition: counts (Skills / MCP servers / Extensions) and a component list with statuses (`main.tsx:15914–15930`). Nothing is compared against `current_revision`; on a plugin that already has an approved revision, a re-import adding/removing an MCP server would render identically to its first review. Additionally, per-agent compatibility (a derived, per-agent property per CONTEXT.md) is only a static note: "Agent compatibility, credentials and aggregate deployment remain separate" (`:15958–15963`).
- **Repro steps:**
  1. Import a Plugin (`POST /pod/plugins`) and approve r1.
  2. Re-import the same `source_ref` with one component changed → r2 draft.
  3. Open **Capabilities → Inbox**, click the plugin: no added/removed indicators vs r1; the "Capability diff" block shows only the new revision's composition.
- **Evidence:** `ui/src/main.tsx:15886–15976` (esp. `:15912–15930`, `:15958–15963`); live capture (2026-09-14).

---

### F9 — Deployments: agents without "claude"/"codex" in their name get no deploy affordance and no explanation (L, code-only — unverified live)

- **Requirement breached:** no specific PRD ID retained in the available spec mapping; best-fit §9 deployment vocabulary (per card spec) — otherwise **no PRD basis**.
- **Route/state:** Capabilities → **Deployments** with a Library Skill assigned to a connected agent whose id/name does not contain "claude" or "codex" (e.g. "hermes"). Not reproduced live (no agent connected in the audit instance) — *unverified live*.
- **Expected:** either a usable deploy action (target selectable) or an explicit reason why deployment is unavailable.
- **Observed:** `deploymentTarget()` infers the harness from name substrings and returns `null` otherwise (`main.tsx:15628–15633`); the Deploy button renders only when `target` is non-null (`:16214–16219`), so such rows show a state chip and no action, with no message explaining the missing target.
- **Repro steps:**
  1. Connect an agent named e.g. "hermes" (Connections), approve a Skill with a package, assign the agent.
  2. Open **Capabilities → Deployments**: row appears; no Deploy button; no explanation text.
  3. Compare: renaming the agent to contain "codex" makes the button appear.
- **Evidence:** `ui/src/main.tsx:15628–15633`, `:16190–16227` (esp. `:16214–16219`); code-only (unverified live).

---

### Findings explicitly NOT raised (checked, no breach)

- **§15.4 empty/failure states on Inbox/Library:** both empty states render next productive actions — Inbox: "Inbox clear" + **Scan agents** + **Import Plugin** (`main.tsx:16053–16062`); Library: "Your Capability Library is empty" + **Discover Skills** + **Import Plugin** (`:16116–16125`); Deployments empty state explains the next step (`:16190–16195`). Verified live. Pass.
- **Type/lifecycle distinguishable without colour:** every type/status signal is a text label (or text + icon): kind chips "SKILL"/"PLUGIN" (`:16071`, `:16093`), status badge labels "In Library / Enabled / In review / Discovered / Disabled / Needs attention" (`:15786–15789`), draft chips "Draft v1.3.0", revision states "DRAFT/APPROVED" (`:15834`), deployment states in words (`:16213`), plugin component statuses "VALID/INVALID/UNSUPPORTED" (`:15926`). No colour-only status found. Pass.
- **Approve/reject reachable in one place (§15.2):** both panels keep Approve + Reject together in the detail footer (`:15863–15880`, `:15964–15972`). Pass (the *substance* around them is F3/F4/F8).

---

## 4. Improvements (proposals only — no code in this pass)

Mapped 1:1 to findings; priority order = harm order. Size S/M/L.

| # | Improvement | Closes | Size | Priority |
|---|---|---|---|---|
| I1a | **Freshness strip on Discover + capability lists:** show client fetch time and cache semantics ("Registry results may be cached up to 5 min", "Last loaded HH:MM"), and render a per-source health line when a registry fails or falls back (surface the existing failure branch instead of console-only). | F1 | S | 1 |
| I1b | **Additive cache metadata for registry proxies:** return `fetched_at` / `cached` on `/pod/skills/registry/skillssh/*` (and the other proxies) so I1a can show true source age. Additive response field only — no stored-state change; flag as follow-up if treated as API-shape work. | F1 | M | 2 |
| I2 | **Fix the "Local files" claim:** show "Canonical revision rN retained in Pod — not materialized" unless a deployment record with verified target exists; only then say "Directory found" + target path. | F2 | S | 3 |
| I3 | **Skill revision change disclosure:** in the review panel, compute and render a changed-file list between the pending revision and the retained revision (added/changed/removed, with instruction-files vs resource-files grouping) above the approve/reject pair. Data is already present in `revisions[].files` returned by `/pod/skills`. | F3 | M | 4 |
| I4 | **Show the proposer:** render `revision.created_by` + `created_at` ("Proposed by … · 1m ago") in both review panels' meta grids. | F4 | S | 5 |
| I5 | **Card completeness (§15.1):** add freshness chip (revision age), risk chip for plugins (from `inspection.risk` counts), package/file count for skills, and deployment count/state chip; keep the existing chips. | F5 | M | 6 |
| I6 | **Separate aggregate views:** sub-navigation Skills | Plugins (keep "All") within Inbox/Library so each aggregate type is directly navigable under the single Capabilities entry. | F6 | S–M | 7 |
| I7 | **Library filter bar:** add search + filters for tag, source, risk, freshness (age bands), update state, deployment state, and compatibility (where data exists); ensure each filter actually narrows the list. | F7 | M–L | 8 |
| I8 | **Plugin review diff:** compare the pending revision's components against the retained revision (added/removed/status-changed by `component_key`); keep "Capability composition" as the label when there is no baseline. | F8 | M | 9 |
| I9 | **Deployment target handling:** resolve the harness from agent metadata rather than name substrings, or render an explicit "No supported adapter for this agent — choose a target" state with target selection. | F9 | S | 10 |

Kept as-is (no improvement needed): empty-state actions, non-colour status labels, one-place approve/reject.

**Scope note for improvements:** all items are capability-view UI changes (contained blast radius per the card). I1b is the only item touching a backend response shape (additive field); I2/I9 rely on data already returned (`deployments`, agent ids). None alters stored revision/deployment state.

---

## 5. Acceptance-criteria coverage (the card's 12 criteria)

| # | Criterion | Verdict | Where |
|---|---|---|---|
| C1 | FIRST PROOF STEP: surface inventory with file+component per surface, each confirmed reachable by loading it | ✅ | §2 (all principal surfaces reached live except S10/S13-code-only paths, marked) |
| C2 | Every finding carries PRD requirement ID, exact route+state, expected vs observed, numbered repro steps | ✅ | §3, every finding |
| C3 | Skills and Plugins separately navigable as distinct aggregate types under one Capabilities entry; merged list = finding | ❌ **F6** | single merged grid (`main.tsx:16064–16105`, `:16127–16163`) |
| C4 | Cached/polling source says so explicitly; bare reference = finding | ❌ **F1** | Discover source chips only; 5-min server cache undisclosed (`skills.ts:697–714`) |
| C5 | Capability cards render type, name, description, revision, source, freshness, component counts, risk summary, Library/Inbox status | ❌ **F5** | freshness + risk missing on all cards; counts partial |
| C6 | Type + lifecycle status distinguishable without colour alone | ✅ | text chips/badges (`:15781–15795`, `:15834`, `:15926`, `:16213`) |
| C7 | Empty Inbox and empty Library each show a next productive action | ✅ | `:16053–16062`, `:16116–16125`; live-verified |
| C8 | Review surface distinguishes instruction-file changes from resource changes for a Skill revision | ❌ **F3** | no diff/classification (`:15852–15862`) |
| C9 | Library exposes working filters for type, tag, compatibility, source, risk, freshness, deployment and update state | ❌ **F7** | type only (`:16021–16031`) |
| C10 | Findings ranked by user harm; every improvement maps to the finding it closes; ranked list is the deliverable | ✅ | §3 ranked; §4 mapped |
| C11 | Review panel (§15.2) shows what changed and who proposed it, approve/reject reachable in one place | ❌ partial — **F3** (what changed, skills), **F4** (who proposed), **F8** (plugin change view); approve/reject in one place ✅ | `:15808–15884`, `:15886–15976` |
| C12 | Audit output = findings and improvements only; no code changes; scoped UI improvement a separate follow-up | ✅ | this document; follow-ups in §6 |

Result: 7/12 pass, 5 fail (C3–C5, C8, C9, C11-partial). Every failure has a finding.

---

## 6. Scope note, limitations, follow-ups

**Scope:** no code changes were made in this audit. No tracked file in any repo was modified (worktree `git status` clean; the live pass ran against a disposable data dir in `/tmp`, since removed/stopped). All improvements above are proposals; the scoped UI improvement is to be raised as a **separate follow-up card** built from the ranked list (§4), not implemented here.

**Follow-up candidates (raised from this audit):**
- F-UP-1: Freshness/health disclosure (I1a; +I1b if the additive field is accepted) — closes F1.
- F-UP-2: Deployed-claim correction (I2) — closes F2.
- F-UP-3: Review change disclosure + proposer identity (I3, I4) — closes F3/F4.
- F-UP-4: Card completeness (I5) — closes F5.
- F-UP-5: Aggregate views + Library filters (I6, I7) — closes F6/F7.
- F-UP-6: Plugin diff + deploy target handling (I8, I9) — closes F8/F9.

**Limitations:**
1. **PRD verbatim text not readable at audit time** (Coffee MCP truncation; statement required in §1.1). Section-level citations (§15.x / CAP-ids) follow the card's mapping; exact per-requirement wording is pending a native-agent fetch.
2. F9 is code-only (*unverified live*): reproducing needs a connected agent with a non-claude/codex name.
3. Visual-only aspects (contrast, spacing, motion) were inspected manually in the live pass but not mechanically (no axe/visual-diff run in this pass).
4. Registry-dependent Discover states were captured against live ClawHub results; an all-sources-failure run was not reproduced (code path read at `:14934–14940`).

---

## 7. Addendum — verbatim PRD cross-check (post-fetch)

After this draft was completed, the verbatim §15.1–15.4 + §9 text was fetched via a native-agent run (comment `4161` on card `redacted-id-24`; saved: `runs/run-003/prd-fetch-comment.md`). Cross-check against the findings above:

- **§15.3 — F1 stands, strengthened.** The verbatim requirement matches F1 exactly, including the example labels ("Live webhook", "Checked 4 minutes ago", "Cached result, 2 days old", "Refresh failed", "Never synced") and "a refresh icon without status is insufficient". I1a should adopt the PRD's exact example strings.
- **§15.1 — F5 stands.** The verbatim card field list adds **deployment count and update state** beyond the card criteria's list; deployment count is absent from cards, update state exists only as a chip. I5's scope may extend by a deployment-count chip.
- **§15.2 — F3/F4/F8 stand; two slices not separately audited.** The verbatim panel spec is broader than the audited slices: it also requires a *plain-language change summary*, a *runtime review block* (executables, remote connections, headers, binaries, permissions, credentials), *package hash*, and *export/defer actions* alongside approve/reject. The runtime-review block and export/defer actions were outside the card criteria and are flagged for the follow-up run when F3/F8 are commissioned.
- **§9 — F2 stands; F9's §9 basis confirmed.** The lifecycle vocabulary confirms verification language ("Synchronized: Pod re-read the target and its observed package digest matches the approved revision") — exactly what F2's "found" claim lacks. §9.2 lists "Unsupported" as a deployment state, confirming F9's best-fit basis.

Net effect: **no finding retracted; F1/F2/F5 strengthened; two additional §15.2 slices noted for follow-up.**
