# Provenance — where the requirements come from

This file is the evidence map behind the requirements and decisions in `techno-os.md` and `pdlc.md`. The full research narratives (extracted pages, verbatim numbers, per-source notes) live in the internal research archive, not in this repository. *Numbers below were verified against primary sources at the time of research.*

## Method
Primary sources only (blogs, repos, talks, published code). Everything marked **verified** was read at source; claims from aggregators/tweets were chased back to primaries or dropped. Anything not reviewed is labelled as such in the internal archive.

## Sources and what we harvested

| Source | What we used | What we deliberately did NOT copy |
| --- | --- | --- |
| Uber (X article 2090828118454071296 + uber.com blog) — "Running a Software Factory Efficiently" | 70%+ agent-attributed PRs; 3,600+ skills; 30K+ executions/day; users ×7, requests ×9.4, AI spend flat; cost/session −52%; 6-term cost equation; 400K-token auto-compaction; search-then-mount vs 50–70K preloaded schemas; code-mode >50–90% savings; spend nudges at 50/80/100%. | 1,000+ MCP servers, 24M-node graph, 3,600-skill catalogs, bespoke internal platform |
| Spotify engineering blog (Portal modes 9/2026, Code-with-Claude 6/2026, Data Assistant, Multi-agent ads, Release Part 2) | 99% weekly AI use; +76% PR frequency; Fleetshift 2.5M+ auto-merged maintenance PRs; release cycle −8h; human judgment = the constraint. | Fleetshift-style org-wide fleets, Backstage-sized catalogs |
| factory.ai (research posts + product docs) | Standard-of-completion-pipeline contrast: single agent 36% → 90% parity on GDAL-family tasks; ~13× wall time; harness model-routing 58% cost cut. | Their platform/fleet scale |
| Vercel Labs eve / Foreman (code + docs) | 4 stations; reviewer deliberately blind to implementer reasoning; factory brain = curated notes (~40K chars); trust stamped once at dispatch; deny-rather-than-park for unattended runs. | Their deployment stack |
| Ryan Carson + Matt Pocock (talks, blog, Sandcastle) | One task/one agent/one env + evidence-PR; E2E walkthrough ~$60/run; METR: experienced devs 19% slower while believing faster; Sandcastle executor (non-root, per-repo `.factory/`, `.out-of-scope`). | Their toolchains |
| Bello (v0.5.1, 142 commits, Python) | Runtime supervision pattern; +9% supervision value on messy specs. | — |
| Multiplayer AI Manifesto | Five principles (never copy-and-paste; door open; artifacts with resumable sessions; attestation; humans in the loop). | — |

## Requirement map (condensed)
- **A — Intake & contracts**: stable identity, project scoping, idempotency, audit events.
- **B — Evidence & proof**: every deliverable carries verdicts + proof (tests, recordings, scans); the mission question is *did this actually happen?*.
- **C — Approval & policy**: human decides anything touching production/credentials/protected branches/money; approvals in Coffee; silence never approves; stale = rejected in the record.
- **D — Memory & ecosystem**: memory substrate (Smartware runtime, Coffee-native direction — see `Mem` in the proposal set), skills as versioned repositories, BYO agents via portable profiles.
- **E — Governance**: per-run records, spend caps, WIP cap, secret redaction, named operator.
- **F — Delivery**: GitHub/GitLab-integrated, branch-per-run, reviews inside Coffee.
- **G — Evolution**: capabilities added on triggers, not phases; evaluation gates on new skills/tools.

*(Full requirement list A–G with per-requirement notes: internal research archive.)*
