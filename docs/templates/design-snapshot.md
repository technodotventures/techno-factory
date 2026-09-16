# Design snapshot (DESIGN.md-style) — template

> **Use for:** environments where the real system isn't reachable — fork onboarding, blue-sky prototyping with external tools, customer theming.
> **Never for:** production context in a repo that contains the real system — there, agents use the repo's components + the `product-design` skill + guards. Portable snapshots were measured at ~30% vs ~80% context coverage, ~+92% tokens, and a bias to **re-implement** components (Atlassian DESIGN.md study).
> **Authored on trigger:** a fork lands, an external tool needs brand context, or a theming request arrives. Keep it short: ≤ ~200 lines (~3–6K tokens). Tokens + intent — not a spec to rebuild components.

Copy to `<product>.design.snapshot.md` and fill both halves (follow Google's DESIGN.md spec for the frontmatter shape).

---

```yaml
name: <product>
updated: <YYYY-MM-DD>
tokens:
  color:
    background: "#______"
    surface: "#______"
    text: "#______"
    text-muted: "#______"
    accent: "#______"        # exactly one primary accent; add semantic pairs only if the system has them
    success: "#______"
    danger: "#______"
  typography:
    family: "______"         # one family, or a declared pair
    scale: ["12/16", "14/20", "16/24", "20/28", "28/36"]   # size/leading
    weights: [400, 500, 700]
  spacing: [4, 8, 12, 16, 24, 32, 48]      # base unit: 4
  radius: ["4", "8", "full"]
  elevation: ["none", "sm", "md", "lg"]
```

## Overview
<2–4 sentences: the feeling, the references, what someone should recognize in five seconds.>

## Colour
<Which colours carry meaning. Where accents are allowed. What is never coloured.>

## Typography
<One family or a declared pair; the scale's intent; casing rules.>

## Layout & spacing
<Grid, density, whitespace posture.>

## Components (patterns, not re-implementations)
<The handful of recurring patterns and the rules that keep them consistent. Reference intent — do not respecify components.>

## Do / Don't
- Do: …
- Don't: …

<!-- Worked example — the factory's docs/board system, abridged (`docs/visuals/README.md`):
     palette #111 / #999 / #6b7280 · mono type · 18px dot matrix · exactly two semantic accents:
     red #C0392B = failing state, green #1E874B = verified state.
     Do: one token set across all boards. Don't: ever introduce a third colour. -->
