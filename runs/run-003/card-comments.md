### comment 4009

## Plan — Pod capabilities module UI audit

**Spec of record:** "Pod Capabilities PRD" (workspace note `redacted-id-31`). This audit is graded against its §15 UX requirements (15.1 capability cards, 15.2 review panel, 15.3 freshness language, 15.4 empty/failure states) and the §9 revision/deployment lifecycle vocabulary. Findings must cite the requirement ID they breach.

**Approach**

- I could not inspect the module. No repository is connected to this project, so `/pod/capabilities` and the capabilities wiring are unreadable from here. This card is therefore a *plan to audit*, not an audit. The Build stage does the inspection; I have defined exactly what its output must contain.

- Establish the surface inventory first: enumerate every route and component under `/pod/capabilities` (Skills list, Plugin list, Inbox, Library, Discover, Review panel, source/health views) and every place capability state is rendered. Write it down as a table before judging anything — an audit without a complete surface list silently misses screens.

- Audit each surface against §15 and §11, one requirement at a time, recording findings in the repo FINDINGS index. A finding is only valid if it names: the requirement ID, the exact route/component and the state to reach it, an expected vs observed pair, and a reproducible step sequence.

- Rank findings by user harm, not by how easy they are to fix. A wrong freshness label (implying live when cached) and a status conveyed by colour alone are correctness/accessibility defects, not polish. Ship the ranked list as the card's actual output.

- Only then propose improvements, prioritised by that ranking, each mapped to the finding it closes. Improvements stay proposals — no code in this card.

**Surfaces/files likely touched** — the audit reads, but does not modify, these Pod areas:

- `/pod/capabilities` route and its page/route file(s) — the Capabilities entry point.

- The Skills list view and the Plugin list view (separate aggregate types per CAP-LIB-001 — if they are one merged list, that itself is a finding).

- The Inbox view and the Library view (approval vs approved surfaces; CAP-ING-006, CAP-LIB-004).

- The revision review panel (§15.2) and any diff/file-list rendering.

- The Discover/source-search surface and its freshness/health indicators (§15.3, CAP-SRC-004).

- Capability card component(s) (§15.1) — wherever type, revision, source, freshness, component counts, risk, and deployment count are rendered.

- The capabilities wiring: source-adapter clients, the capability/revision/deployment data layer and any state hooks/selectors feeding these views, plus their tests.

- Exact filenames cannot be named from here — see the note above; resolving them is the first Build-stage action.

**Known risks and blast radius**

- *Biggest risk is a shallow audit.* "Looks dated" is not a finding. The value of this card is a reproducible defect list tied to requirement IDs; without that, Build will implement generic restyling and the real defects survive.

- *Trust misrepresentation is the highest-severity class.* Any UI implying live/real-time data when a source is cached or polling (CAP-SRC-004, §15.3), or showing "deployed" without target verification (§16), is a trust defect — rank these first.

- *Read-only.* The audit must not change behaviour. If inspecting a surface requires seeding state, that seeding must be local and disposable.

- *Blast radius of the later improvement is contained:* capability views, not the ingestion or deployment engines. Exclude any change that would alter stored revision/deployment state.

**out_of_scope** — this card is NOT doing:

- Implementing any UI change (the scoped improvement is a follow-up card raised from this audit's ranked list).

- Auditing other modules (`Audit UI on all modules` is the umbrella card; this is the Capabilities slice only).

- Designing the source-adapter or inspection backends (the PRD §11 owns that in a different phase).

- Security review of executable/plugin content beyond how it is *displayed* (CAP-PLG-003 is an inspection-engine property, not a UI one).

- Redesigning the product's information architecture or renaming product surfaces; brand/visual design system work.

- Backend schema, migration, or API-shape changes, including any change to revision or deployment state machines.

**Decisions taken (proceeding without asking)**

- *Decision:* the PRD is the acceptance standard, not the current product's conventions. Where the module behaves differently from the PRD, the PRD wins and the divergence is a finding. This makes the audit objective rather than taste-based.

- *Decision:* findings are recorded in the repo FINDINGS index as the founder asked; until a repository is connected, findings accumulate in this card's Agent tab and move to the index when the repo is available. I am not inventing an index location I cannot verify.

- *Decision:* this card delivers the audit plus a prioritised improvement proposal. The improvement itself becomes a separate card, because "audit, then improve" cannot be one reviewable pass.

**Open questions** — none blocking. Two facts are needed to *execute* the audit (see the checklist's first item), but they do not change the plan.

---

### comment 3989

Requested (founder): the Capabilities module in Pod (Skills / plugins / inbox / library surfaces) works but lacks a good UI. Scope: audit the current capabilities UI against the product surfaces, record findings (repo FINDINGS index), then a scoped UI improvement. Candidate for factory run 001.