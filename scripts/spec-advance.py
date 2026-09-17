#!/usr/bin/env python3
"""spec-advance — native-lane station worker for the six factory lines (Mt14Eiext).

Replaces the sandboxed step workflows with Coffee's NATIVE assignment lane
(verified Sep 17: an assigned station agent works the ROOT card — plan/criteria
and verdicts land ON the card):

  1. Spec dispatch   — TO DO card with no Factory Planner assignment -> assign (93).
  2. Auto-advance    — TO DO card, Planner assignment done + acceptance criteria
                       present -> move to READY + notify the factory channel.
                       (READY = specced & dispatchable.)
  3. Review dispatch — IN REVIEW card with no Factory Tester assignment -> assign (113).
                       Verdicts land on the card; the tester prompt is dual-mode aware.

Idempotent by construction (assignment rows and status moves are the state).
Dry-run by default; --execute to act. Prints only what moved (cron-safe).

Usage:
  python3 scripts/spec-advance.py [--project <hash> ...] [--limit N] [--execute]
Env: COFFEE_WORKSPACE (default 'techno') + standard COFFEE_* (token store / oauth).
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from coffee_mcp import mcp_call  # noqa: E402

WS = os.environ.get("COFFEE_WORKSPACE", "techno")
HOST = f"https://{WS}.meetcoffee.ai"
PLANNER_ID = 93
TESTER_ID = 113
DONE_STATES = ("done", "completed", "complete")
DEFAULT_PROJECTS = [
    "bfhqkkn9ofbk",  # Pod Factory
    "m4c5fngzfbtx",  # Smartware Factory
    "oxju1frzaz6q",  # Coffee Factory
    "w1l9zhbscg8j",  # expresso Factory
    "kynsde4gp1bf",  # CaseAid Factory
    "tsp8hn56rmn3",  # ChadAI Factory
]


def j(r) -> dict:
    try:
        return json.loads(r["result"]["content"][0]["text"])
    except Exception:
        return {"_err": str(r)[:250]}


def status_title(card) -> str:
    tp = card.get("task_project") or []
    return ((tp[0].get("task_status") or {}).get("title") or "") if tp else ""


def agent_rows(card, name_fragment: str):
    return [r for r in (card.get("task_agent_assignee") or []) if name_fragment in str(r.get("name") or "")]


def decide(card, checklist_n):
    """Pure decision for one card -> action string or None.

    checklist_n=None means 'not fetched yet' (cheap pre-pass). Note: API-created
    assignments stay 'staged' even after the agent finishes (UI-created go 'done'),
    so spec-completeness is judged by the deliverable — criteria on the card — not
    by the assignment status.
    """
    st = status_title(card)
    planner = agent_rows(card, "Planner")
    tester = agent_rows(card, "Tester")
    if st == "TO DO":
        if not planner:
            return "dispatch-spec"
        alive = any(str(r.get("status")) not in ("failed", "cancelled", "error") for r in planner)
        if not alive:
            return None
        if checklist_n is None:
            return "need-checklist"
        return "advance" if checklist_n > 0 else None
    if st == "IN REVIEW":
        if not tester:
            return "dispatch-review"
        return None
    return None


def fetch_card(h):
    return ((j(mcp_call("GetTaskByTaskHash", {"workspace": WS, "task_hash": h})).get("data") or {}).get("task")) or {}


def checklist_count(h) -> int:
    ck = j(mcp_call("GetTaskChecklist", {"workspace": WS, "task_hash": h}))
    return len(((ck.get("data") or {}).get("result")) or [])


def status_hash(project, title):
    s = j(mcp_call("GetTaskStatus", {"workspace": WS, "project_hash": project, "limit": 30}))
    for x in ((s.get("data") or {}).get("result") or []):
        if x.get("project_hash") == project and x.get("title") == title:
            return x.get("task_status_hash")
    return None


def notify(msg):
    try:
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "coffee-notify"), msg],
                           capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            logdir = ROOT / "runs" / "spec-advance"
            logdir.mkdir(parents=True, exist_ok=True)
            with (logdir / "notify.err.log").open("a") as fh:
                fh.write((r.stdout or "") + (r.stderr or "") + "\n")
    except Exception as exc:  # noqa: BLE001
        try:
            logdir = ROOT / "runs" / "spec-advance"
            logdir.mkdir(parents=True, exist_ok=True)
            with (logdir / "notify.err.log").open("a") as fh:
                fh.write(f"{exc}\n")
        except Exception:  # noqa: BLE001
            pass


def candidates(project, limit):
    r = j(mcp_call("GetTask", {"workspace": WS, "project_hashes": [project], "limit": limit}))
    out = []
    for t in ((r.get("data") or {}).get("result") or []):
        if t.get("is_trashed"):
            continue
        st = status_title(t)
        if st in ("TO DO", "IN REVIEW"):
            out.append(t.get("task_hash"))
    return out


def main():
    ap = argparse.ArgumentParser(description="Native-lane spec/advance/review worker (dry-run by default).")
    ap.add_argument("--project", action="append", default=[])
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--execute", action="store_true")
    a = ap.parse_args()
    projects = a.project or DEFAULT_PROJECTS
    moved = 0
    for p in projects:
        for h in candidates(p, a.limit):
            card = fetch_card(h)
            if not card:
                continue
            action = decide(card, None)
            if action == "need-checklist":
                action = decide(card, checklist_count(h))
            if not action:
                continue
            title = str(card.get("title") or "")[:80]
            if action == "dispatch-spec":
                if a.execute:
                    res = j(mcp_call("PostAiAgentsAssignTask", {"workspace": WS, "requestBody": {"task_hash": h, "agent_id": PLANNER_ID}}))
                    ok = bool((res.get("data") or {}).get("task_agent_assignee_hash")) or bool(res.get("success"))
                    print(f"SPEC-DISPATCHED {h} | {title} | ok={ok}")
                    if not ok:
                        print(f"ERROR assign failed: {json.dumps(res)[:200]}")
                else:
                    print(f"would-dispatch-spec {h} | {title}")
                moved += 1
            elif action == "advance":
                if a.execute:
                    sh = status_hash(p, "READY")
                    res = j(mcp_call("PatchTaskByTaskHash", {"workspace": WS, "task_hash": h, "requestBody": {
                        "task_project_status": [{"project_hash": p, "task_status_hash": sh}]}}))
                    ok = bool(res.get("success"))
                    print(f"ADVANCED {h} | {title} | ready={ok}")
                    if ok:
                        notify(f"✅ Specced \u2192 READY: \u201c{title}\u201d \u2014 {HOST}/task?hash={h}")
                else:
                    print(f"would-advance {h} | {title}")
                moved += 1
            elif action == "dispatch-review":
                if a.execute:
                    res = j(mcp_call("PostAiAgentsAssignTask", {"workspace": WS, "requestBody": {"task_hash": h, "agent_id": TESTER_ID}}))
                    ok = bool((res.get("data") or {}).get("task_agent_assignee_hash")) or bool(res.get("success"))
                    print(f"REVIEW-DISPATCHED {h} | {title} | ok={ok}")
                    if not ok:
                        print(f"ERROR review assign failed: {json.dumps(res)[:200]}")
                else:
                    print(f"would-dispatch-review {h} | {title}")
                moved += 1
    if not moved:
        print("spec-advance: nothing to do.")


if __name__ == "__main__":
    main()
