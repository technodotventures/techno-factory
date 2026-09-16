#!/usr/bin/env python3
"""merge-approved.py — merge a factory PR after an authorized approval lands on its card.

Human judgment (the approval) stays with the founders; the merge itself is mechanical.
Every rail must pass or the worker holds and reports. Dry-run by default.

Rails:
  R1  PR head branch is a factory branch (factory/*)
  R2  state OPEN; mergeable MERGEABLE + mergeStateStatus CLEAN
  R3  all status checks SUCCESS on the *current* HEAD sha (>=1 check)
  R4  an approval comment from an authorized user, NEWER than the last commit,
      and posted by a human (no via_app / no posted_by_agent — agent-authored
      comments must never count as approval)
  R5  no sensitive paths in the diff (.github/workflows, secrets) unless --allow-sensitive
  R6  merge uses --match-head-commit <sha> (GitHub refuses if HEAD moved again)

Usage:
  merge-approved.py --card <task_hash> [--pr N] [--execute] [--allow-sensitive]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coffee_mcp import mcp_call

WS = os.environ.get("FACTORY_BOARD_WORKSPACE", "techno")
REPO = os.environ.get("FACTORY_DELIVERY_REPO", "technodotventures/pod")
AUTHORIZED = {h.strip() for h in os.environ.get("FACTORY_APPROVER_USER_HASHES", "").split(",") if h.strip()}  # board user hashes allowed to approve (set FACTORY_APPROVER_USER_HASHES)
APPROVE_RE = re.compile(r"\b(approved|approve|merge it|ship it|go ahead and merge)\b", re.I)
PR_URL_RE = re.compile(r"github\.com/[^/\s]+/[^/\s]+/pull/(\d+)")
PR_SHORT_RE = re.compile(r"\b(?:pod|PR)\s*#(\d+)\b", re.I)
SENSITIVE = (".github/workflows/", "secrets", ".env")


def j(r):
    try:
        return json.loads(r["result"]["content"][0]["text"])
    except Exception as e:
        return {"err": str(e)[:200]}


def gh(*args, check=True):
    cmd = ["gh", *args]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])}… failed: {p.stderr[:200]}")
    return p.stdout.strip(), p.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True)
    ap.add_argument("--pr", type=int)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--allow-sensitive", action="store_true")
    a = ap.parse_args()

    report = []
    def rail(name, ok, detail):
        report.append((name, ok, detail))
        return ok

    # --- card -> PR number + approval scan
    c = j(mcp_call("GetTaskComment", {"workspace": WS, "task_hash": a.card, "limit": 100}))
    comments = sorted(((c.get("data") or {}).get("result") or []), key=lambda x: x.get("task_comment_id") or 0)
    pr_n = a.pr
    if not pr_n:
        for cm in reversed(comments):
            blocks = cm.get("blocks") or []
            text = "\n".join("".join(ch.get("text", "") for ch in (b.get("children") or [])) for b in blocks)
            m = PR_URL_RE.search(text) or PR_SHORT_RE.search(text)
            if m:
                pr_n = int(m.group(1))
                break
    if not pr_n:
        print("HOLD: no PR number on the card (pass --pr explicitly)")
        sys.exit(2)

    v, _ = gh("pr", "view", str(pr_n), "--repo", REPO, "--json",
              "state,mergeable,mergeStateStatus,headRefName,headRefOid,statusCheckRollup,commits,url")
    pr = json.loads(v)
    head = pr["headRefOid"]

    rail("R1 factory branch", pr["headRefName"].startswith("factory/"), pr["headRefName"])
    rail("R2 open+clean", pr["state"] == "OPEN" and pr["mergeable"] == "MERGEABLE" and pr["mergeStateStatus"] == "CLEAN",
         f'{pr["state"]}/{pr["mergeable"]}/{pr["mergeStateStatus"]}')
    rollup = pr.get("statusCheckRollup") or []
    all_ok = len(rollup) >= 1 and all((x.get("conclusion") == "SUCCESS") for x in rollup)
    rail("R3 checks green", all_ok, ", ".join(f'{x.get("name")}={x.get("conclusion")}' for x in rollup))

    try:
        last_commit = (pr.get("commits") or [])[-1].get("committedDate")
    except Exception:
        last_commit = None

    approvals = []
    ignored_agent = []
    for cm in comments:
        author = ((cm.get("user") or {}).get("user_hash")
                  or (cm.get("author") or {}).get("user_hash"))
        blocks = cm.get("blocks") or []
        text = "\n".join("".join(ch.get("text", "") for ch in (b.get("children") or [])) for b in blocks)
        created = cm.get("created_at") or cm.get("updated_at")
        if author in AUTHORIZED and APPROVE_RE.search(text):
            # R4 must be a human approval: agent-authored comments (via_app set by
            # the hermes app, or posted_by_agent set by a native Coffee agent) can
            # coincidentally match APPROVE_RE and must never count.
            if not cm.get("via_app") and not cm.get("posted_by_agent"):
                approvals.append((created, text[:80]))
            else:
                ignored_agent.append((created, text[:60]))
    fresh = [x for x in approvals if last_commit and x[0] and x[0] > last_commit]
    rail("R4 approval newer than HEAD", bool(fresh),
         f"last_commit={last_commit}; approvals={approvals or 'none'}; "
         f"agent-authored ignored={ignored_agent or 'none'}; fresh={fresh or 'none'}")

    diff, _ = gh("pr", "diff", str(pr_n), "--repo", REPO, "--name-only")
    files = [f for f in diff.splitlines() if f.strip()]
    bad = [f for f in files if any(s in f for s in SENSITIVE)]
    rail("R5 sensitive paths", (not bad) or a.allow_sensitive, f"{len(files)} files; flagged={bad or 'none'}")

    print(f"\n=== merge-approved · PR #{pr_n} · {REPO} ===")
    for name, ok, detail in report:
        print(f"  [{'PASS' if ok else 'HOLD'}] {name}: {detail}")

    if not all(ok for _, ok, _ in report):
        print("\nRESULT: HOLD — rails not satisfied. No merge performed.")
        sys.exit(1)

    if not a.execute:
        print(f"\nRESULT: ALL RAILS PASS (dry-run). Would merge with: gh pr merge {pr_n} --squash --match-head-commit {head}")
        sys.exit(0)

    out, rc = gh("pr", "merge", str(pr_n), "--repo", REPO, "--squash", "--match-head-commit", head)
    merged = rc == 0
    merge_sha = ""
    if merged:
        v2, _ = gh("pr", "view", str(pr_n), "--repo", REPO, "--json", "mergeCommit")
        merge_sha = (json.loads(v2).get("mergeCommit") or {}).get("oid", "")
        mcp_call("PostTaskComment", {"workspace": WS, "task_hash": a.card, "requestBody": {
            "text": (f"Merge receipt — PR #{pr_n} merged via merge-approved worker.\n"
                     f"Head sha: {head} · merge commit: {merge_sha} · checks: {', '.join(x.get('name','') for x in rollup)} SUCCESS.\n"
                     f"Approval (newer than HEAD): {fresh[0][0]} — \"{fresh[0][1]}\"")}})
    print(f"\nRESULT: {'MERGED ' + merge_sha if merged else 'MERGE FAILED'} (exit {rc})")
    sys.exit(0 if merged else 1)


if __name__ == "__main__":
    main()
