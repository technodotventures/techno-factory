# Software Factory — technical diagrams

Six boards, one visual system (Swiss/monospace, black & white, with exactly two semantic accents: **red `#C0392B` = failing state, green `#1E874B` = verified state** — nothing else is ever colored).

| Board | Files |
|---|---|
| Factory overview — work in → the factory → work out, human gates | `01-factory-overview.svg` · `.png` |
| Product Development Lifecycle — both halves, the two human gates | `02-pdlc.svg` · `.png` |
| Anatomy of one run — red → green → evidence → approve → merged | `03-run-anatomy.svg` · `.png` |
| Improvement loop — runs → findings → backlog → fix | `04-improvement-loop.svg` · `.png` |
| Factory topology — where everything lives: Coffee control plane, delivery, workers, personal seats, peers (marker = state: ■ live · ▢ direction · ■ gap) | `05-topology.svg` · `.png` |
| Target architecture — the finished factory: core · adapters · triggers, the loop, the fork contract | `06-target-architecture.svg` · `.png` |

- Sources are **self-contained SVGs** (no external fonts or CDN); PNGs are 1440-wide renders of the same geometry (canvas height varies per board).
- `index.html` stacks all six (open locally or via GitHub Pages).
- All boards are generated from one geometry module — one token set (palette `#111 / #999 / #6b7280`, 18px dot matrix, single type scale), so the set stays consistent as it grows.
