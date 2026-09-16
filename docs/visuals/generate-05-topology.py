#!/usr/bin/env python3
"""Generate docs/visuals/05-topology.svg — factory topology zone map.

House style (from 01-factory-overview.svg): 1440x900, Swiss-mono, dot matrix,
#111/#999/#6b7280 palette, two semantic accents only (green #1E874B verified,
red #C0392B failing/gap).
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent / "05-topology.svg"

INK, GREY, LT, DOTS = "#111111", "#6b7280", "#999999", "#d9d9d9"
GREEN, RED = "#1E874B", "#C0392B"
F = "ui-monospace, 'JetBrains Mono', 'IBM Plex Mono', Menlo, Consolas, monospace"

# measured advance widths (px/char): 13px ≈ 8.55, 12px ≈ 7.75
LADV, NADV, GAP = 8.55, 7.75, 12

P = []  # svg parts


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def zone(x, y, w, h, label, sub):
    P.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{LT}" stroke-width="1.0" stroke-dasharray="6 5"/>')
    P.append(f'<text x="{x+20}" y="{y+30}" font-size="15" font-weight="700" fill="{INK}" letter-spacing="0.6">{esc(label)}</text>')
    if sub:
        P.append(f'<text x="{x+20}" y="{y+50}" font-size="12" font-weight="400" fill="{GREY}" letter-spacing="0.2">{esc(sub)}</text>')


def item(x, y, marker, label, note=None):
    mk = {
        "live": f'<rect x="{x}" y="{y-9}" width="8" height="8" fill="{GREEN}"/>',
        "gap": f'<rect x="{x}" y="{y-9}" width="8" height="8" fill="{RED}"/>',
        "dir": f'<rect x="{x}" y="{y-9}" width="8" height="8" fill="none" stroke="{LT}" stroke-width="1.0"/>',
    }[marker]
    P.append(mk)
    tx = x + 16
    P.append(f'<text x="{tx}" y="{y}" font-size="13" font-weight="400" fill="{INK}">{esc(label)}</text>')
    if note:
        nx = tx + round(len(label) * LADV) + GAP
        P.append(f'<text x="{nx}" y="{y}" font-size="12" font-weight="400" fill="{GREY}">{esc(note)}</text>')


def items(x, y0, rows, zone_w=0, pitch=23):
    for i, (m, lab, note) in enumerate(rows):
        item(x, y0 + i * pitch, m, lab, note)
    # width sanity check for containment
    for m, lab, note in rows:
        w = len(lab) * LADV + (len(note) * NADV + GAP if note else 0) + 20
        if zone_w and w > zone_w - 40:
            print(f"WARN overflow: '{lab}' needs {w:.0f}px, has {zone_w-40}px")


# ── canvas + frame + defs (verbatim house geometry) ──────────────────────────
P.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="900" viewBox="0 0 1440 900" font-family="{F}">')
P.append('<defs><pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="0.5" cy="0.5" r="0.95" fill="#d9d9d9"/></pattern><clipPath id="framec"><rect x="48" y="48" width="1344" height="804" rx="12"/></clipPath></defs>')
P.append('<rect width="1440" height="900" fill="#ffffff"/>')
P.append('<g clip-path="url(#framec)"><rect x="48" y="48" width="1344" height="804" fill="url(#dots)"/></g>')
P.append(f'<rect x="48" y="48" width="1344" height="804" rx="12" fill="none" stroke="{DOTS}" stroke-width="1.0"/>')
P.append(f'<text x="88" y="92" font-size="15" font-weight="700" fill="{INK}" letter-spacing="1.2">05 / FACTORY TOPOLOGY</text>')
P.append(f'<rect x="1249.86" y="73" width="102.14" height="28" fill="none" stroke="{INK}" stroke-width="1.0"/>')
P.append(f'<text x="1300.93" y="91.32" font-size="12" font-weight="700" fill="{INK}" text-anchor="middle" letter-spacing="0.6">TECHNO OS</text>')

# ── row 1: Coffee | GitHub | Workers ─────────────────────────────────────────
zones = [
    (88, 150, 500, 290, "COFFEE", "external platform — source of record for human work state", [
        ("live", "Board & cards", "status = stage · comments = run log"),
        ("live", "Approvals & gates", "Review · Launch Review"),
        ("live", "Files & evidence", "recordings · byte-exact links"),
        ("live", "Meetings", "agent-attended · transcribed → tasks"),
        ("live", "Native agents", "Factory Planner · Chat harness"),
        ("live", "Skills", "stored with the workspace"),
        ("live", "MCP / API — 136 tools", "signed webhooks → notifications"),
        ("dir", "Repo lane", "GitHub App broker"),
        ("gap", "task.activity webhook", "unverified — tracked"),
    ]),
    (612, 150, 340, 290, "GITHUB", "org technodotventures — delivery plane", [
        ("live", "techno-factory", "docs·scripts·runs"),
        ("live", "pod", "unit · UI · E2E · containment"),
        ("live", "factory/* branches", "PRs · checks"),
        ("live", "Merge gate", "approval + exact-sha"),
        ("dir", "GitLab", "second provider · pending"),
    ]),
    (976, 150, 376, 290, "WORKERS", "sandboxed execution — the external plane", [
        ("live", "OS shell operator", "runs 000–007"),
        ("live", "Evidence capture", "red → green"),
        ("live", "Merge worker", "deterministic · exact-sha"),
        ("live", "ci-heal watch", "30-minute scan · dedupe"),
        ("live", "Guards", "hooks > scripts > prompts"),
        ("dir", "/agent-execution", "status + approvals"),
    ]),
]
for x, y, w, h, lab, sub, rows in zones:
    zone(x, y, w, h, lab, sub)
    items(x + 20, y + 72, rows, w)

# ── strip between rows ───────────────────────────────────────────────────────
P.append(f'<text x="720" y="462" font-size="12" font-weight="400" fill="{GREY}" text-anchor="middle" letter-spacing="0.2">cards dispatch the work · branches carry it · checks and receipts return to the card</text>')

# ── row 2: Personal surfaces | Peers & substrate ────────────────────────────
zones = [
    (88, 484, 560, 206, "PERSONAL SURFACES", "operator seats — demote to optional operators (portability)", [
        ("live", "Personal agent fleet", "reviewer pass · OAuth identity"),
        ("live", "Desktop agent", "the only surface with live provider keys"),
        ("live", "VPS (personal box)", "file mirrors :8099/:8100 · staging"),
        ("gap", "Provider keys", "refresh before the seed — one live"),
        ("dir", "Production host", "venture-owned · worker + watcher"),
    ]),
    (672, 484, 680, 206, "PEERS & SUBSTRATE", "named peers — adopt on trigger", [
        ("dir", "Smartware", "memory substrate → into Coffee"),
        ("dir", "Pod", "companion · agent registry / BYO bridge"),
        ("dir", "expresso", "workflow semantics · receipts"),
        ("live", "Design lint — @shadcn/lint", "adopted standard · wiring queued"),
        ("dir", "Pilots — Detail · Graphify", "bug mining · context graph"),
    ]),
]
for x, y, w, h, lab, sub, rows in zones:
    zone(x, y, w, h, lab, sub)
    items(x + 20, y + 72, rows, w)

# ── legend ──────────────────────────────────────────────────────────────────
P.append(f'<rect x="88" y="700" width="1264" height="88" fill="none" stroke="{INK}" stroke-width="1.0"/>')
P.append(f'<text x="112" y="732" font-size="15" font-weight="700" fill="{INK}" letter-spacing="0.9">STATE/</text>')
P.append(f'<rect x="112" y="750" width="9" height="9" fill="{GREEN}"/><text x="130" y="759" font-size="12" font-weight="400" fill="{GREY}">live — verified with a receipt</text>')
P.append(f'<rect x="472" y="750" width="9" height="9" fill="none" stroke="{LT}" stroke-width="1.0"/><text x="490" y="759" font-size="12" font-weight="400" fill="{GREY}">direction — named trigger, not yet built</text>')
P.append(f'<rect x="892" y="750" width="9" height="9" fill="{RED}"/><text x="910" y="759" font-size="12" font-weight="400" fill="{GREY}">gap — blocked / failing, tracked</text>')
P.append(f'<text x="112" y="778" font-size="12" font-weight="400" fill="{GREY}">&gt; zones are homes, not phases. Humans sit only at the gates — in Coffee.</text>')

# ── footer ──────────────────────────────────────────────────────────────────
P.append(f'<text x="720" y="838" font-size="17" font-weight="400" fill="{INK}" text-anchor="middle" letter-spacing="0.3">Coffee carries the state; the factory carries the execution.</text>')
P.append('</svg>')

OUT.write_text("\n".join(P))
print("wrote", OUT, "|", OUT.stat().st_size, "bytes")
