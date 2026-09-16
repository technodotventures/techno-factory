# Design principles — agentic UX

**The standard for every user-facing surface we build** — Coffee first, then every venture surface and the factory's own interfaces. Adopted from The Skins Factory's *"AI Agent UX Design"* (May 2026) and mapped onto our own primitives.

**The premise:** agents act; they do not assist. So the interface's job is no longer task execution — it is **trust and governance**: *trust without visibility, control without micromanagement, transparency without noise.*

## The five patterns (required design language)

| # | Pattern | What it is | How we express it here |
|---|---|---|---|
| 1 | **Activity feed** | A filterable timeline of agent actions, decisions, and pending items — every entry: what happened, why, confidence, and a path to review. Replaces the notification model. | Coffee: card + project activity. Factory: run logs live on the card. Every agent action must land somewhere a human can read. |
| 2 | **Intervention point** | A designed pause where the agent shows its intended next action — approve, modify, or redirect. Feels like a colleague checking in; never a modal demanding attention, never a bare stop button. | Coffee: task statuses + approvals + comment-steering. Factory: the two human gates (Review / Launch Review) — always with context, never a dead end. |
| 3 | **Confidence gradient** | Certainty is visible and scales: high confidence stays quiet; low confidence gets prominent, review-first treatment. | Verdicts + evidence strength on cards; low-confidence work holds at the gate instead of proceeding loudly. Calm by default. |
| 4 | **Scope boundary** | What the agent can and cannot do is a first-class, visible element — not a settings page buried three levels deep. | Coffee: agent grants/permissions, project scope. The boundary shapes the mental model from day one. |
| 5 | **Handoff** | The moment the agent stops and transfers to a human: what it tried, why it stopped, what it recommends, what the human needs next. The most important interaction — and the one most products get wrong. | Coffee: approvals, escalations, meeting→task handoffs. Factory: a run reaching a gate always carries full context (plan, evidence, open questions). |

## Supporting requirements

- **Decision logs, not action logs** — "this happened **because** that, based on these" is explainable; "this happened" is not.
- **Autonomy spectrum** — classify every agent action: **full** (acts + logs) · **supervised** (acts, review window) · **approval required** (recommends, never executes). Statuses + approvals make the spectrum real.
- **Usable audit trails** — navigable by a human without a data-engineering degree. The card *is* the audit trail here.

## Anti-patterns (never ship these)

- Agent behavior wearing a copilot UI (chat-only for something that acts).
- Audit trails built for compliance that humans can't read.
- Stop-buttons instead of intervention points; modals instead of handoffs.

## How this stays in the DNA (wiring — not vibes)

- **Spec:** user-facing features declare their pattern mapping (which of the five apply, and where) in the brief/criteria.
- **Review (design check):** the human design verdict covers brand fidelity **+ pattern conformance** (`pdlc.md`); `guard-scan` flags UI-impacting changes for this check.
- **Tests:** the a11y gate + journey suite back the patterns mechanically where possible (visible state, labels, no dead ends).
- **Design lint:** Tailwind surfaces run `@shadcn/lint` (`no-arbitrary-values`, `no-raw-colors`, `no-unknown-classes`; component contracts later) — errors carry the fix, so agents clean them before Review. Scoped rules v0 land on Pod (run-008).
- **Design surface:** self-hosted Penpot — exploration, specs, and reviewable hand-offs live there, and its MCP server lets agents read and author designs directly. Code stays the source of truth (repo components + the `product-design` skill); a design snapshot bridges to external tools.
- **Coffee first:** before inventing UI for any pattern, map it onto Coffee primitives (activity, statuses, approvals, grants, comments) — the coffee-first rule applies to design too.
