# Portability & self-hosting

**The factory is a pattern, not a deployment.** This repo is the reference implementation: the PDLC stations, the evidence discipline, the guards — plus the adapters that wire them to a board, a delivery provider, and agent runtimes. Where this repo says "Coffee", read "the board". Nothing in the design depends on any single operator's personal environment.

## Core vs adapter

- **Core (portable):** `docs/` (techno-os, pdlc, design-principles), `docs/templates/` (agent roles, design snapshot, test plan), the run discipline (`runs/`, evidence packages, guard scans), the scorecard.
- **Adapters (environment):** `scripts/coffee_mcp.py`, `coffee-notify`, Coffee tool names and hashes in scripts, the notification channel, credential stores. Porting = rewrite the adapter; the core is board-agnostic.

## Adapter contract — what a host must provide

| Role | Required primitives | Reference today | Swap notes |
|---|---|---|---|
| **Board** | tasks with stages · acceptance criteria as checklist · comments as run log · files as evidence · approvals as gates · agent assignment | Coffee | any board with these primitives; keep the stage semantics identical (TO DO → IN PROGRESS → IN REVIEW → COMPLETE) |
| **Delivery** | branches · pull requests · checks | GitHub | GitLab adapter queued (trigger: actually used) |
| **Agents** | durable runs on tasks · comment delivery (steering) · attributed identities | Coffee runtime + external agents via MCP | any runtime that can read a card, write back, and act on a repo |
| **Notifications** | one channel agents can post to | Coffee chat (house format) | any chat API |
| **Memory (optional)** | cross-run records | Smartware/Pod (direction) | the loop works without one; run logs + scorecard are the fallback memory |

## Deployment shape: where the loop lives

- **Pilot (now):** a personal environment. Purpose: prove the loop, build habits. Nothing venture-critical; credentials isolated from production.
- **Production:** a venture-owned host (e.g. the venture VPS). All studio-critical automation. Strict isolation: separate OAuth client, separate model keys, tokens `0600` on the host — credentials never cross environments in either direction.

**Operators:** the founders sit at the two gates (Review / Launch Review). Personal agent surfaces and dev environments (editor + coding-agent seats, e.g. VS Code with Codex/Claude-class tooling) may join as extra operators — **nothing depends on them**. **Host hygiene:** production never lives on a personal dev environment; dev seats are operator surfaces, and production credentials never live on them.

## Deploy checklist (venture host)

1. **Runtime:** repo checkout · python + node · ffmpeg + Playwright browsers (for recorded evidence) · the provider CLI (`gh` or equivalent).
2. **Identity:** venture-registered OAuth client for the board + consent at deploy · token store `0600` · round-trip verified · **venture model keys — no personal keys**.
3. **Worker:** one agent profile that runs the stations from `docs/templates/` + the repo's scripts. The operator playbook *is* the repo — no private knowledge required.
4. **Watcher daemon:** polls the board (webhooks when available) → assigns the Planner on new cards → fires runs → posts run updates → flags approvals. **WIP cap and spend ceiling are enforced here — the only layer that can refuse.**
5. **Delivery auth:** scoped git credentials (push + PRs only — no publish tokens in workers) for the target repos.
6. **Board wiring:** stages, automations (native or watcher-equivalent), dedicated notification channel.
7. **Smoke:** one small card end-to-end — red → green, evidence on the card, review gate, merge.
8. **Demote the pilot:** the personal connection drops to personal use; nothing in production references it.

## Forking for another studio

1. **Copy the core;** pick adapters: board (Coffee · GitHub Issues · Linear · files), delivery (GitHub · GitLab), agents (Hermes · Claude Code · Codex · BYO).
2. **Set the gates:** who approves merge / launch — and agents never approve their own work.
3. **Start minimal:** one repo · one board · one worker · WIP ≤ 3; seed ~20 runs before expanding (expansion triggers: `techno-os.md` §9 — capabilities are added on triggers, not phases).
4. **Non-negotiable:** evidence discipline — no run closes without receipts (the mission question: *did this actually happen?*).

## Design context for forks (portable snapshots)

A forker — or an external tool — won't have the repo's real design system. For those cases, ship a **design snapshot**: a DESIGN.md-style one-file distillate of tokens + intent.

- **Template:** `docs/templates/design-snapshot.md`. Copy to `<product>.design.snapshot.md`.
- **Use for:** fork onboarding · blue-sky prototyping with external tools · customer theming.
- **Never for:** production context where the repo is the system — there, the real components + the `product-design` skill + guards are the source of truth (measured failure modes: Atlassian DESIGN.md study).
- **Trigger:** authored when a fork lands, an external prototype needs brand context, or a theming request arrives.
