#!/usr/bin/env python3
"""Generate docs/visuals/06-target-architecture.svg — the finished factory, fork-facing.

Every element is classified: core (any fork keeps it) · adapter (choose yours) ·
trigger (add when it fires). Same house system as 01–05: Swiss-mono, dot matrix,
#111/#999/#6b7280, one accent (green #1E874B = verified/core).
Canvas 1440x1310 (the closing map — zones + loop + fork contract).
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent / "06-target-architecture.svg"

INK, GREY, LT, DOTS = "#111111", "#6b7280", "#999999", "#d9d9d9"
GREEN = "#1E874B"
F = "ui-monospace, 'JetBrains Mono', 'IBM Plex Mono', Menlo, Consolas, monospace"
LADV, NADV, GAP = 8.55, 7.75, 12

P = []


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def zone(x, y, w, h, label, sub):
    P.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{LT}" stroke-width="1.0" stroke-dasharray="6 5"/>')
    P.append(f'<text x="{x+20}" y="{y+30}" font-size="15" font-weight="700" fill="{INK}" letter-spacing="0.6">{esc(label)}</text>')
    if sub:
        P.append(f'<text x="{x+20}" y="{y+50}" font-size="12" font-weight="400" fill="{GREY}" letter-spacing="0.2">{esc(sub)}</text>')


def item(x, y, marker, label, note=None):
    if marker == "core":
        mk = f'<rect x="{x}" y="{y-9}" width="8" height="8" fill="{GREEN}"/>'
    elif marker == "adapter":
        mk = f'<rect x="{x}" y="{y-9}" width="8" height="8" fill="none" stroke="{LT}" stroke-width="1.0"/>'
    else:  # trigger
        mk = f'<circle cx="{x+4}" cy="{y-5}" r="4.2" fill="none" stroke="{LT}" stroke-width="1.0"/>'
    P.append(mk)
    tx = x + 16
    P.append(f'<text x="{tx}" y="{y}" font-size="13" font-weight="400" fill="{INK}">{esc(label)}</text>')
    if note:
        nx = tx + round(len(label) * LADV) + GAP
        P.append(f'<text x="{nx}" y="{y}" font-size="12" font-weight="400" fill="{GREY}">{esc(note)}</text>')


def items(x, y0, rows, zone_w=0, pitch=23):
    for i, (m, lab, note) in enumerate(rows):
        item(x, y0 + i * pitch, m, lab, note)
    for m, lab, note in rows:
        w = len(lab) * LADV + (len(note) * NADV + GAP if note else 0) + 20
        if zone_w and w > zone_w - 40:
            print(f"WARN overflow: '{lab}' needs {w:.0f}px, has {zone_w-40}px")


# ── canvas + frame ───────────────────────────────────────────────────────────
P.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1310" viewBox="0 0 1440 1310" font-family="{F}">')
P.append('<defs><pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="0.5" cy="0.5" r="0.95" fill="#d9d9d9"/></pattern><clipPath id="framec"><rect x="48" y="48" width="1344" height="1214" rx="12"/></clipPath></defs>')
P.append('<rect width="1440" height="1310" fill="#ffffff"/>')
P.append('<g clip-path="url(#framec)"><rect x="48" y="48" width="1344" height="1214" fill="url(#dots)"/></g>')
P.append(f'<rect x="48" y="48" width="1344" height="1214" rx="12" fill="none" stroke="{DOTS}" stroke-width="1.0"/>')
P.append(f'<text x="88" y="92" font-size="15" font-weight="700" fill="{INK}" letter-spacing="1.2">06 / TARGET ARCHITECTURE — THE FINISHED FACTORY</text>')
P.append(f'<rect x="1249.86" y="73" width="102.14" height="28" fill="none" stroke="{INK}" stroke-width="1.0"/>')
P.append(f'<text x="1300.93" y="91.32" font-size="12" font-weight="700" fill="{INK}" text-anchor="middle" letter-spacing="0.6">TECHNO OS</text>')

# ── legend strip ─────────────────────────────────────────────────────────────
P.append(f'<rect x="88" y="118" width="1264" height="34" fill="none" stroke="{INK}" stroke-width="1.0"/>')
P.append(f'<rect x="106" y="130" width="9" height="9" fill="{GREEN}"/><text x="124" y="140" font-size="12" fill="{GREY}">core — any fork keeps this</text>')
P.append(f'<rect x="392" y="130" width="9" height="9" fill="none" stroke="{LT}"/><text x="410" y="140" font-size="12" fill="{GREY}">adapter — choose your implementation</text>')
P.append(f'<circle cx="748" cy="134.5" r="4.5" fill="none" stroke="{LT}"/><text x="762" y="140" font-size="12" fill="{GREY}">trigger — add when it fires</text>')
P.append(f'<text x="1332" y="140" font-size="12" fill="{INK}" text-anchor="end">fork = core + your adapters</text>')

# ── row 1: Control plane | Delivery ──────────────────────────────────────────
zones = [
    (88, 166, 656, 272, "CONTROL PLANE — THE BOARD", "state · evidence · decisions (reference: Coffee)", [
        ("core", "Task stages", "the PDLC as statuses; IN REVIEW = the gate"),
        ("core", "Acceptance checklists", "authored before the build — the verifier's contract"),
        ("core", "Comments = run log", "receipts land on the card as they happen"),
        ("core", "Files & recordings", "evidence — byte-exact, human-reviewable"),
        ("core", "Approvals rail", "raised in-app · decided by humans · receipted"),
        ("core", "Notifications", "one channel agents can post to"),
        ("core", "Agents — native + BYO", "same task contract over MCP / API"),
        ("adapter", "Meetings & recordings", "agent-attended, transcribed → tasks"),
        ("core", "Skills", "process lives with the workspace"),
    ]),
    (768, 166, 584, 272, "DELIVERY — THE CODE PLANE", "where code truth lives", [
        ("core", "factory/* branches", "every run = a branch + a PR"),
        ("core", "CI checks", "unit · e2e · a11y — read back to the card"),
        ("core", "Review = merge gate", "human approval · exact-HEAD-sha match"),
        ("adapter", "The provider", "GitHub │ GitLab — the adapter is thin"),
        ("trigger", "Releases", "release record per feature → launch lane"),
    ]),
]
for x, y, w, h, lab, sub, rows in zones:
    zone(x, y, w, h, lab, sub)
    items(x + 20, y + 72, rows, w)

# ── row 2: Execution | Operators ─────────────────────────────────────────────
zones = [
    (88, 462, 656, 248, "EXECUTION — THE WORKER FLEET", "sandboxed · budgeted · receipted", [
        ("core", "Operator profile", "the operator playbook IS the repo"),
        ("core", "Chain — Plan → Build → Test", "blind, different-vendor verifier"),
        ("trigger", "Supervisor · Adversary", "conditional — a real failure's evidence"),
        ("core", "Evidence capture", "red → green · screenshots · recordings"),
        ("core", "Guards", "WIP ≤ 3 · spend ceiling · token broker · diff scan"),
        ("core", "Merge worker", "deterministic · rail-checked · human-gated"),
        ("core", "Sandbox", "non-root · egress allowlist · vaulted creds"),
        ("adapter", "Host", "any venture-owned machine · never a personal box"),
    ]),
    (768, 462, 584, 248, "OPERATORS — THE HUMANS", "sit at the gates, nowhere else", [
        ("core", "The gates", "Review · Launch Review (Go / No-Go)"),
        ("core", "Steering", "comments · decisions · priorities"),
        ("core", "Human-posted approvals", "the rail ignores agent prose"),
        ("adapter", "Extra seats", "personal agents · dev envs — nothing depends on them"),
        ("core", "Owner", "a named operator-owner — never unowned"),
    ]),
]
for x, y, w, h, lab, sub, rows in zones:
    zone(x, y, w, h, lab, sub)
    items(x + 20, y + 72, rows, w)

# ── row 3: Design lane | Intelligence ────────────────────────────────────────
zones = [
    (88, 734, 656, 224, "DESIGN LANE", "design lives with the system — not in a tool silo", [
        ("core", "Design discipline", "in-repo skill + agentic-UX standard"),
        ("core", "Design lint", "mechanical checks agents self-correct against"),
        ("adapter", "Penpot (self-hosted)", "open source; MCP lets agents read & author"),
        ("trigger", "Design snapshot", "one-file handoff for forks & external tools"),
    ]),
    (768, 734, 584, 224, "INTELLIGENCE — MEASURE & MEMORY", "the loop closes itself — added on trigger", [
        ("trigger", "Product analytics", "PostHog-first · agent-readable"),
        ("trigger", "Bug mining", "post-merge defect sweep"),
        ("trigger", "Context graph", "codebase graph — token economics"),
        ("trigger", "Memory substrate", "cross-run context packs"),
        ("trigger", "Feedback automations", "E2E walkthrough · watchdog · rubric loop"),
        ("core", "Retro", "30-day PASS / LEARN — feeds Discovery"),
    ]),
]
for x, y, w, h, lab, sub, rows in zones:
    zone(x, y, w, h, lab, sub)
    items(x + 20, y + 72, rows, w)

# ── loop strip ───────────────────────────────────────────────────────────────
P.append(f'<rect x="88" y="982" width="1264" height="80" fill="none" stroke="{INK}" stroke-width="1.0"/>')
P.append(f'<text x="108" y="1010" font-size="15" font-weight="700" fill="{INK}" letter-spacing="0.9">THE LOOP</text>')
P.append(f'<text x="108" y="1034" font-size="13" fill="{INK}">ENGINEERING — Discovery → Spec → Build → Test → Review (gate) → Merge</text>')
P.append(f'<text x="108" y="1054" font-size="13" fill="{INK}">LAUNCH — Prepare → Message → Create → Launch Review (gate) → Go Live → Measure → Retro ↺ Discovery</text>')

# ── fork contract strip ──────────────────────────────────────────────────────
P.append(f'<rect x="88" y="1086" width="1264" height="150" fill="none" stroke="{INK}" stroke-width="1.0"/>')
P.append(f'<text x="108" y="1114" font-size="15" font-weight="700" fill="{INK}" letter-spacing="0.9">FORK CONTRACT</text>')
P.append(f'<text x="330" y="1114" font-size="12" fill="{GREY}">what any environment must provide — copy the core, choose the adapters</text>')
cols = [
    (108, "BOARD", ["tasks · stages · checklists", "comments · files · approvals", "agent assignment"]),
    (364, "DELIVERY", ["branches · pull requests", "checks · merge gate"]),
    (620, "AGENTS", ["durable runs on tasks", "write-back to the card", "action on a repo"]),
    (876, "NOTIFICATIONS", ["one channel", "agents can post to"]),
    (1132, "MEMORY (optional)", ["repo files + run logs", "are the fallback"]),
]
for cx, label, lines in cols:
    P.append(f'<text x="{cx}" y="1150" font-size="12" font-weight="700" fill="{INK}" letter-spacing="0.5">{label}</text>')
    for i, ln in enumerate(lines):
        P.append(f'<text x="{cx}" y="{1170+i*20}" font-size="12" fill="{GREY}">{esc(ln)}</text>')
P.append(f'<text x="108" y="1228" font-size="12" fill="{GREY}">start minimal: one repo · one board · one worker · WIP ≤ 3 — expand on triggers, not phases.</text>')

# ── footer ───────────────────────────────────────────────────────────────────
P.append(f'<text x="720" y="1252" font-size="15" fill="{INK}" text-anchor="middle" letter-spacing="0.3">Coffee carries the state; the factory carries the execution.</text>')
P.append('</svg>')

OUT.write_text("\n".join(P))
print("wrote", OUT, "|", OUT.stat().st_size, "bytes")
