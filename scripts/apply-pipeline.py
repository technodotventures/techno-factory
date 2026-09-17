#!/usr/bin/env python3
"""apply-pipeline.py — apply the canonical factory pipeline to Coffee projects.

Loads scripts/factory-pipeline.json and makes each target project match it:
  • statuses  — ensure the canonical set (rename legacy titles, fix colors, create missing)
  • agents    — ensure station agents exist (create from the spec if missing)
  • workflows — ensure the station workflows exist (event triggers, role steps, budgets)
  • briefs    — set each project's agent_brief (the per-project run background)

Dry-run by default; --execute performs the writes and reads everything back.
Idempotent: a re-run reports OK / skip for every item.

Usage:
  python3 apply-pipeline.py --all [--execute]
  python3 apply-pipeline.py --line "Pod Factory" [--execute]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coffee_mcp import mcp_call  # noqa: E402

WS = "techno"
SPEC_PATH = Path(__file__).resolve().parent / "factory-pipeline.json"


def unwrap(envelope):
    try:
        return json.loads(envelope["result"]["content"][0]["text"])
    except Exception:
        return envelope


def call(tool, args):
    return unwrap(mcp_call(tool, {"workspace": WS, **args}))


def data_of(resp, *keys, default=None):
    cur = resp.get("data", {}) if isinstance(resp, dict) else {}
    for k in keys:
        cur = (cur or {}).get(k) if isinstance(cur, dict) else None
    return cur if cur is not None else default


# ---------------------------------------------------------------- agents

AGENT_FIELDS = ("name", "description", "initial_prompt", "personality",
                "tool_domains", "run_max_spend_usd", "run_max_minutes")


def build_agent_body(a):
    return {k: a[k] for k in AGENT_FIELDS if k in a}


def ensure_agents(spec, execute, out):
    resp = call("GetWorkspaceSettingsPublicAgents", {})
    agents = data_of(resp, "result", default=[]) or []
    by_name = {a.get("name"): a.get("agent_id") for a in agents}
    for a in spec.get("agents", []):
        name = a["name"]
        if name in by_name:
            aid = by_name[name]
            det = call("GetWorkspaceSettingsAgentsByAgentId", {"agent_id": aid})
            d = det.get("data") if isinstance(det, dict) else None
            if isinstance(d, dict) and isinstance(d.get("result"), dict):
                d = d["result"]
            d = d if isinstance(d, dict) else {}
            drift = [k for k in ("description", "personality", "initial_prompt",
                                 "tool_domains", "run_max_spend_usd", "run_max_minutes")
                     if k in a and d.get(k) is not None and d.get(k) != a[k]]
            if drift:
                out(f"  agent UPDATE: {name!r} (drifted: {drift})")
                if execute:
                    call("PutWorkspaceSettingsAgentsByAgentId",
                         {"agent_id": aid, "requestBody": build_agent_body(a)})
                    out("    -> updated")
            else:
                out(f"  agent ok: {name!r} (id {aid})")
            continue
        out(f"  agent CREATE: {name!r}")
        if execute:
            call("PostWorkspaceSettingsAgents", {"requestBody": build_agent_body(a)})
            hit = []
            for _ in range(3):
                resp2 = call("GetWorkspaceSettingsPublicAgents", {})
                agents2 = data_of(resp2, "result", default=[]) or []
                hit = [x for x in agents2 if x.get("name") == name]
                if hit:
                    break
                time.sleep(2)
            if hit:
                by_name[name] = hit[0].get("agent_id")
                out(f"    -> created, id {by_name[name]}")
            else:
                out("    !! created but not found in read-back")
    return by_name


# ---------------------------------------------------------------- statuses

def get_statuses(project_hash):
    resp = call("GetTaskStatus", {"project_hash": project_hash})
    rows = data_of(resp, "result", default=[]) or []
    return [r for r in rows if r.get("project_hash") == project_hash]


def ensure_statuses(project_hash, spec, execute, out):
    canonical = spec["statuses"]
    # 1) legacy renames (dry-run simulates the rename locally so later checks are honest)
    rows = get_statuses(project_hash)
    by_title = {r["title"]: r for r in rows}
    for old, new in spec.get("legacy_status_renames", {}).items():
        if old in by_title and new not in by_title:
            out(f"  status RENAME: {old!r} -> {new!r}")
            if execute:
                res = call("PatchTaskStatusByTaskStatusHash",
                           {"task_status_hash": by_title[old]["task_status_hash"],
                            "requestBody": {"title": new}})
                if not (isinstance(res, dict) and res.get("success")):
                    out(f"    !! rename response: {json.dumps(res)[:200]}")
                rows = get_statuses(project_hash)
                by_title = {r["title"]: r for r in rows}
            else:
                row = by_title.pop(old)
                by_title[new] = {**row, "title": new}
    # 2) create missing + fix colors
    if execute:
        rows = get_statuses(project_hash)
        by_title = {r["title"]: r for r in rows}
    for st in canonical:
        cur = by_title.get(st["title"])
        if cur is None:
            out(f"  status CREATE: {st['title']!r} ({st['type']}, {st['color']})")
            if execute:
                res = call("PostTaskStatus", {"requestBody": {
                    "title": st["title"], "task_status_type": st["type"],
                    "color_hex": st["color"], "project": [{"project_hash": project_hash}]}})
                if not (isinstance(res, dict) and res.get("success")):
                    out(f"    !! create response: {json.dumps(res)[:200]}")
        else:
            if (cur.get("color_hex") or "").lower() != st["color"].lower():
                out(f"  status RECOLOR: {st['title']!r} {cur.get('color_hex')} -> {st['color']}")
                if execute:
                    res = call("PatchTaskStatusByTaskStatusHash",
                               {"task_status_hash": cur["task_status_hash"],
                                "requestBody": {"color_hex": st["color"]}})
                    if not (isinstance(res, dict) and res.get("success")):
                        out(f"    !! recolor response: {json.dumps(res)[:200]}")
            else:
                out(f"  status ok: {st['title']!r}")
    # 3) order check (canonical statuses must be strictly increasing)
    rows = get_statuses(project_hash)
    by_title = {r["title"]: r for r in rows}
    seq = [(st["title"], by_title[st["title"]].get("order")) for st in canonical if st["title"] in by_title]
    orders = [o for _, o in seq]
    if orders != sorted(orders) or len(set(orders)) != len(orders):
        out(f"  status ORDER off: {seq} — patching to canonical order")
        if execute:
            for idx, st in enumerate(canonical):
                if st["title"] in by_title:
                    call("PatchTaskStatusByTaskStatusHash",
                         {"task_status_hash": by_title[st["title"]]["task_status_hash"],
                          "requestBody": {"order": idx}})
    else:
        out(f"  status order ok: {seq}")
    final = get_statuses(project_hash)
    others = [r["title"] for r in final if r["title"] not in {s["title"] for s in canonical}]
    if others:
        out(f"  note: non-canonical statuses remain (not deletable via API): {others}")
    return {r["title"]: r["task_status_hash"] for r in final}


# ---------------------------------------------------------------- workflows

def build_steps(w, agents):
    steps, unresolved = [], []
    for s in w["steps"]:
        step = {"id": s["id"], "role": s["role"], "brief": s["brief"],
                "depends_on": [], "requires_approval": s.get("requires_approval", False)}
        aid = agents.get(s.get("agent_name"))
        if aid:
            step["agent_id"] = aid
        elif s.get("agent_name"):
            unresolved.append(s["agent_name"])
        steps.append(step)
    return steps, unresolved


def ensure_workflows(project_hash, status_hashes, spec, agents, execute, out):
    resp = call("GetAgentWorkflow", {"project_hash": project_hash})
    existing = data_of(resp, "workflows", default=[]) or []
    by_name = {w.get("name"): w for w in existing}
    for w in spec["workflows"]:
        hit = by_name.get(w["name"])
        enabled = w.get("enabled", True)  # spec can own enablement (e.g. disabled-and-kept-for-rollback)
        steps, unresolved = build_steps(w, agents)
        if unresolved:
            out(f"  workflow SKIP: {w['name']!r} — unresolved station agent(s) {unresolved}; "
                f"no step without its pinned agent")
            continue
        if hit is None:
            event = w["trigger"]["event"]
            if event.startswith("task.status.<"):
                key = event[len("task.status.<"):-1]
                h = status_hashes.get(key)
                if not h:
                    out(f"  workflow SKIP: {w['name']!r} — status {key!r} not resolved")
                    continue
                event = f"task.status.{h}"
            out(f"  workflow CREATE: {w['name']!r} (on {event}; agent {w['steps'][0].get('agent_name')})")
            if execute:
                body = {"name": w["name"], "description": w["description"],
                        "trigger_kind": "event", "event_name": event,
                        "project_hash": project_hash, "is_enabled": enabled,
                        "max_spend_usd": w["max_spend_usd"], "max_minutes": w["max_minutes"],
                        "steps": steps}
                res = call("PostAgentWorkflow", {"requestBody": body})
                if not (isinstance(res, dict) and res.get("success")):
                    out(f"    !! create response: {json.dumps(res)[:240]}")
            continue
        # exists: drift check (step briefs / pinned agents / enablement / caps)
        cur = hit.get("steps") or []
        drift = []
        if [s.get("id") or s.get("step_id") for s in cur] != [s["id"] for s in steps]:
            drift.append("step set")
        else:
            for c, wn in zip(cur, steps):
                if (c.get("brief") or "") != wn["brief"]:
                    drift.append(f"brief:{wn['id']}")
                    break
                c_agent = c.get("agent_id") or (c.get("agent") or {}).get("agent_id")
                if wn.get("agent_id") and c_agent != wn["agent_id"]:
                    drift.append(f"agent:{wn['id']}")
                    break
        if hit.get("is_enabled") != enabled:
            drift.append("enablement")
        if hit.get("max_spend_usd") != w["max_spend_usd"]:
            drift.append("max_spend")
        if hit.get("max_minutes") != w["max_minutes"]:
            drift.append("max_minutes")
        if not drift:
            out(f"  workflow ok: {w['name']!r}")
            continue
        out(f"  workflow UPDATE: {w['name']!r} (drifted: {drift})")
        if execute:
            body = {"expected_revision": hit.get("revision"),
                    "name": w["name"], "description": w["description"],
                    "trigger_kind": hit.get("trigger_kind") or "event",
                    "event_name": hit.get("event_name"),
                    "project_hash": project_hash, "is_enabled": enabled,
                    "max_spend_usd": w["max_spend_usd"], "max_minutes": w["max_minutes"],
                    "steps": steps}
            res = call("PutAgentWorkflowByAgentWorkflowHash",
                       {"agent_workflow_hash": hit.get("agent_workflow_hash"),
                        "requestBody": body})
            if not (isinstance(res, dict) and res.get("success")):
                out(f"    !! update response: {json.dumps(res)[:240]}")
    # read-back
    resp = call("GetAgentWorkflow", {"project_hash": project_hash})
    now = {x.get("name"): x for x in (data_of(resp, "workflows", default=[]) or [])}
    for w in spec["workflows"]:
        x = now.get(w["name"])
        if x:
            out(f"  workflow verified: {w['name']!r} enabled={x.get('is_enabled')} "
                f"trigger={x.get('event_name')} steps={len(x.get('steps') or [])}")


# ---------------------------------------------------------------- briefs

def ensure_brief(project_hash, name, spec_line, execute, out):
    brief = spec_line.get("brief")
    if not brief:
        out("  brief: none in spec (statuses-only line)")
        return
    resp = call("GetWorkspaceProjectByProjectHash", {"project_hash": project_hash})
    cur = data_of(resp, "result", default={}) or {}
    if cur.get("name") != name:
        out(f"  !! project hash/name mismatch: read {cur.get('name')!r} for {name!r}")
        return
    if (cur.get("agent_brief") or "") == brief:
        out("  brief ok")
        return
    out(f"  brief SET ({len(brief)} chars)")
    if execute:
        res = call("PutWorkspaceProjectByProjectHash", {
            "project_hash": project_hash,
            "requestBody": {"name": cur.get("name"), "description": cur.get("description"),
                            "agent_brief": brief}})
        if not (isinstance(res, dict) and res.get("success")):
            out(f"    !! response: {json.dumps(res)[:200]}")
        chk = call("GetWorkspaceProjectByProjectHash", {"project_hash": project_hash})
        c2 = data_of(chk, "result", default={}) or {}
        out(f"    read-back: brief {'set' if (c2.get('agent_brief') == brief) else 'MISMATCH'}; "
            f"name {c2.get('name')!r}; description {'intact' if c2.get('description') == cur.get('description') else 'CHANGED'}")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--line")
    ap.add_argument("--execute", action="store_true")
    a = ap.parse_args()
    if not a.all and not a.line:
        ap.error("pass --all or --line NAME")

    raw = SPEC_PATH.read_text()
    raw = raw.replace('"your-board-project-hash"', json.dumps(os.environ.get("FACTORY_BOARD_PROJECT_HASH", "your-board-project-hash")))
    spec = json.loads(raw)
    lines = spec["lines"]
    if a.line:
        lines = [ln for ln in lines if a.line in (ln["name"], ln["hash"])]
        if not lines:
            print(f"no line matches {a.line!r}")
            sys.exit(2)

    mode = "EXECUTE" if a.execute else "DRY-RUN"
    print(f"== apply-pipeline [{mode}] — {len(lines)} line(s) ==")
    print("== agents ==")
    agents = ensure_agents(spec, a.execute, print)

    for ln in lines:
        print(f"\n== {ln['name']} ({ln['hash']}) ==")
        ensure_statuses(ln["hash"], spec, a.execute, print)
        if ln.get("statuses_only"):
            print("  (statuses-only line — workflows/brief skipped)")
            continue
        statuses = get_statuses(ln["hash"])
        status_hashes = {r["title"]: r["task_status_hash"] for r in statuses}
        ensure_workflows(ln["hash"], status_hashes, spec, agents, a.execute, print)
        ensure_brief(ln["hash"], ln["name"], ln, a.execute, print)

    print(f"\n== done ({mode}) ==")


if __name__ == "__main__":
    main()
