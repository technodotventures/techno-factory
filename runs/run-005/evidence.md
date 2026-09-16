# Run 005 — evidence (Pod deps: clear the beta-gate)

> Mission check: *did this actually happen?* Every claim maps to a file in `evidence/` or a link.

- **Work item:** card `redacted-id-26` — "Pod deps 005 — clear the beta-gate: dependency advisories"
- **Repo / branch:** `technodotventures/pod` · `factory/fix-deps-audit` (from `origin/main` @ `48f5adf`); head `ad70201`
- **PR:** `technodotventures/pod#6` — <https://github.com/technodotventures/pod/pull/6> (shortlink `tinyurl.com/2xj72ocb`)
- **CI (PR):** ✅ `verify` **4m46s — first beta-gate green since Sep 8** (audit → typecheck → 290/290 → UI build → acceptance → macOS desktop pack) · ✅ `e2e` 4m48s.
- **Merged:** `c9889ae` (PR #6, 13:45Z, ~4 min after review). **Post-merge on main: `verify` ✅ + `e2e` ✅ — beta gate green on `main` for the first time since Sep 8.**
- **Verdict:** merged (approval).

## Evidence map

| Item | Evidence |
|---|---|
| Audit red → green | `red-audit.txt` (5 advisories, exit 1) → `green-audit.txt` (0, exit 0) |
| Fix shape | Lockfile-only: imapflow 1.7.8 · mailparser 3.9.26 · nodemailer 10.0.9 (`package.json` untouched) |
| Runtime fix | `beta-gate.yml` → Node 26 (on 22 the macOS gate cancels the watch-auth tests) |
| Suites | `green-unit-tests.txt` (290/290) · `green-e2e.txt` (17/17) |
| Guards | `guard-scan.txt` — lockfile churn = the change itself |
| CI | `ci-both-green.txt` |

## Notes

- The gate had been red repo-wide since the POD-AUDIT-003 merge — first on the advisories, then on the runtime. Both cleared in one PR.
- Once merged: `verify` green on `main`; every open/future PR inherits it.
- No Planner-spec'd checklist on this card (scope was fully enumerated in the kickoff instructions); the evidence above is the record.
