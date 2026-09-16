#!/usr/bin/env python3
"""ci-heal — CI failure detection + diagnosis briefs for factory branches.

Scans recent failed workflow runs on factory branches (and main) across the
factory repos. For each unhandled failure it:
  1. checks whether a newer run for the same workflow+branch already succeeded
     (marks it superseded-skip) or is re-running (waits),
  2. extracts the failed step + an error excerpt from the run log,
  3. classifies the failure (deterministic heuristics),
  4. writes a diagnosis brief to runs/ci-heal/,
  5. posts one notification to the factory Coffee channel.

The FIX lane stays agent-operated: a worker (human or agent) picks up the
brief and runs the repo's fix-and-verify loop (red -> fix -> green).

Usage:
  python3 scripts/ci-heal.py [--repos owner/repo,...] [--limit N] [--dry-run] [--no-notify]

Exit code 0 always (reporter role); prints a summary.
"""
import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "runs" / "ci-heal"
STATE_PATH = OUT_DIR / "state.json"
NOTIFY = ROOT / "scripts" / "coffee-notify"
DEFAULT_REPOS = ["technodotventures/pod", "technodotventures/techno-factory"]

# Ordered: most specific failure markers first. Step names bias the result when
# they name the phase (typecheck / e2e / tests); otherwise the failure excerpt decides.
CATEGORIES = [
    ("RUNTIME-VERSION", re.compile(r"cancelledByParent|event loop has already resolved|ERR_DLOPEN|NODE_MODULE_VERSION", re.I)),
    ("UNIT-TEST", re.compile(r"✖ failing tests|not ok \d+|# fail [1-9]|ERR_ASSERTION|AssertionError", re.I)),
    ("E2E", re.compile(r"Playwright|toBeVisible|locator\(|trace\.zip", re.I)),
    ("DEPS-AUDIT", re.compile(r"\d+ vulnerabilit|npm audit|advisories", re.I)),
    ("TYPECHECK", re.compile(r"error TS\d{4}|Found \d+ error|typecheck", re.I)),
    ("INSTALL", re.compile(r"npm ERR!|EBADENGINE|EUSAGE|npm ci failed", re.I)),
]

SUGGESTIONS = {
    "DEPS-AUDIT": "Run `npm audit --audit-level=low`; prefer lockfile-only bumps; keep the suite green.",
    "RUNTIME-VERSION": "Check the repo's verified runtime (`docs/install.md`). Node 26 is the house runtime; older Node cancels the watch-auth-style tests.",
    "TYPECHECK": "Run the typecheck locally (`npm run typecheck`); fix the reported types.",
    "UNIT-TEST": "Reproduce (`npm test`, or the single file); fix; capture red->green per the test plan.",
    "E2E": "Run `npx playwright test` locally; open the failing trace artifact for the exact step.",
    "INSTALL": "Check lockfile / node version / registry access; reproduce with `npm ci`.",
    "UNKNOWN": "Open the run log; triage manually and classify for the next iteration.",
}


def gh(args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])} failed: {r.stderr.strip()[:200]}")
    return r.stdout


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_state():
    try:
        return json.loads(STATE_PATH.read_text())
    except Exception:
        return {}


def save_state(state):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=1))


def classify(step, text):
    s = (step or "").lower()
    if "audit" in s:
        return "DEPS-AUDIT"
    if "typecheck" in s or "type check" in s:
        return "TYPECHECK"
    if "playwright" in s or "e2e" in s:
        return "E2E"
    if "install" in s or "npm ci" in s:
        return "INSTALL"
    for name, rx in CATEGORIES:
        if rx.search(text):
            return name
    if "test" in s:
        return "UNIT-TEST"
    return "UNKNOWN"


def failed_step(log):
    for raw in log.splitlines():
        if "##[error]" in raw:
            m = re.search(r"##\[error\](.*)", raw)
            if m:
                return m.group(1).strip()[:120]
    return None


def excerpt_from_log(log, max_lines=80):
    lines = []
    for raw in log.splitlines():
        parts = raw.split("\t", 3)
        msg = parts[3] if len(parts) == 4 else raw
        msg = re.sub(r"\x1b\[[0-9;]*m", "", msg).strip()
        if msg:
            lines.append(msg)
    return "\n".join(lines[-max_lines:] if len(lines) > max_lines else lines)


def render_brief(repo, run, step, cat, excerpt, branch):
    return f"""# CI failure brief — {repo} · {run['workflowName']}

- **Run:** {run['url']} — {run.get('displayTitle', '')}
- **Branch:** {branch} · **created:** {run.get('createdAt', '')}
- **Failed step:** {step or '(n/a)'}
- **Category:** {cat}

## Error excerpt

```
{excerpt}
```

## Suggested next actions

- {SUGGESTIONS[cat]}
- Fix lane: branch `{branch}` — diagnose -> fix -> push -> re-verify (red -> green per the test plan). Brief generated {now_iso()}.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos", default=",".join(DEFAULT_REPOS))
    ap.add_argument("--limit", type=int, default=15)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-notify", action="store_true")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    state = load_state()
    briefed = 0

    for repo in [r.strip() for r in args.repos.split(",") if r.strip()]:
        try:
            runs = json.loads(gh(["run", "list", "--repo", repo, "--limit", str(args.limit),
                                  "--json", "databaseId,workflowName,headBranch,conclusion,status,url,displayTitle,createdAt"]))
        except Exception as e:
            print(f"!! {repo}: {e}")
            continue
        for run in runs:
            rid = str(run["databaseId"])
            branch = run.get("headBranch") or ""
            if run.get("conclusion") != "failure":
                continue
            if not (branch.startswith("factory/") or branch == "main"):
                continue
            if rid in state:
                continue

            # stale-branch check: a merged/closed PR is no longer actionable
            try:
                prs = json.loads(gh(["pr", "list", "--repo", repo, "--head", branch, "--state", "all",
                                     "--json", "state,number", "--limit", "1"]))
                if prs and prs[0].get("state") in ("MERGED", "CLOSED"):
                    state[rid] = {"status": "stale-branch-skip", "at": now_iso()}
                    print(f"skip (branch PR {prs[0]['state'].lower()}) {repo} {rid} {run['workflowName']} {branch}")
                    continue
            except Exception:
                pass

            # superseded / re-running check
            try:
                latest = json.loads(gh(["run", "list", "--repo", repo, "--branch", branch,
                                        "--workflow", run["workflowName"], "--limit", "1",
                                        "--json", "conclusion,status"]))
                if latest and latest[0].get("conclusion") == "success":
                    state[rid] = {"status": "superseded-skip", "at": now_iso()}
                    print(f"skip (superseded) {repo} {rid} {run['workflowName']} {branch}")
                    continue
                if latest and latest[0].get("status") in ("queued", "in_progress"):
                    print(f"wait (re-run in progress) {repo} {rid} {run['workflowName']} {branch}")
                    continue
            except Exception:
                pass

            try:
                log = gh(["run", "view", rid, "--repo", repo, "--log-failed"])
            except Exception as e:
                log = f"(log fetch failed: {e})"
            step = failed_step(log)
            ex = excerpt_from_log(log)
            cat = classify(step, f"{ex}\n{log[:2000]}")
            slug = re.sub(r"[^a-z0-9]+", "-", (run["workflowName"] or "ci").lower()).strip("-")
            brief = OUT_DIR / f"{rid}-{slug}.md"
            if args.dry_run:
                print(f"[dry] would brief {repo} {rid} {run['workflowName']} on {branch} [{cat}] -> {brief.name}")
                briefed += 1
                continue

            brief.write_text(render_brief(repo, run, step, cat, ex, branch))
            print(f"briefed {repo} {rid} {run['workflowName']} on {branch} [{cat}] -> {brief.name}")
            briefed += 1

            if not args.dry_run:
                if not args.no_notify:
                    msg = (f"CI red — {repo} · {run['workflowName']} on {branch} · {cat}"
                           f" · brief: runs/ci-heal/{brief.name} · {run['url']}")
                    subprocess.run(["python3", str(NOTIFY), msg], capture_output=True, text=True, timeout=120)
                state[rid] = {"status": "briefed", "brief": brief.name, "category": cat, "at": now_iso()}

    if not args.dry_run:
        save_state(state)
    print(f"\nbriefed: {briefed} · tracked total: {len(state)}")


if __name__ == "__main__":
    main()
