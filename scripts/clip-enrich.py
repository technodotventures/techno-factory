#!/usr/bin/env python3
"""clip-enrich — clip-intake enrichment worker for the factory lines.

Watches cards for Coffee clip links (https://<ws>.meetcoffee.ai/clip/<clip_hash>)
and appends an evidence digest (transcript + visual notes from keyframes) to the
card Description, so native stations (planner / tester / build workers) can
consume screen-recorded feedback. Mirrors the manual pipeline proven Sep 17 2026
on card lBKlrI8OfZILQkXxhFX5E2AK (clip 6uddxzvnbvdzk884jvi7e1wx22y2db8).

Pipeline: native resolve (GetClipsByClipHash; public-share lane as fallback) ->
webm via minted file link (GetFileDownloadLinkByFileHash) -> ffmpeg keyframes ->
Coffee transcribe (PostClipsTranscribe; local faster-whisper fallback) -> optional
vision notes (OpenAI-compatible endpoint) -> digest -> Description blocks +
poster/keyframes attached + marker comment.
Uses Coffee's native clip tools (shipped Sep 17 2026): GetClipsByClipHash,
PostClipsTranscribe, GetFileDownloadLinkByFileHash.

Usage:
  python3 scripts/clip-enrich.py --project <hash> [--project <hash> ...] [--limit N] [--execute]
  python3 scripts/clip-enrich.py --task <hash> [--execute|--dry-run] [--reprocess]

Dry-run is the DEFAULT (the full pipeline runs; nothing is posted). Idempotent:
cards already carrying the marker ('clip-enrich:v1' comment or 'CLIP ANALYSIS'
brief block) are skipped unless --reprocess. Exit code 0 always (worker role).

Env (optional unless noted):
  COFFEE_WORKSPACE           workspace subdomain (default 'techno')
  CLIP_ENRICH_WORKDIR        scratch dir (default <repo>/runs/clip-enrich)
  CLIP_ENRICH_WHISPER_PY     python w/ faster-whisper (default /opt/data/whisper-venv/bin/python)
  CLIP_ENRICH_WHISPER_MODEL  default 'small'
  CLIP_ENRICH_TRANSCRIBE     auto|native|local (default auto: Coffee transcribe, whisper fallback)
  CLIP_ENRICH_VISION_BASE_URL / _API_KEY / _MODEL   (OpenAI-compatible; skip if unset)
  CLIP_ENRICH_MAX_FRAMES     default 8
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from coffee_mcp import mcp_call  # noqa: E402

WS = os.environ.get("COFFEE_WORKSPACE", "techno")
HOST = f"https://{WS}.meetcoffee.ai"
WORKDIR = Path(os.environ.get("CLIP_ENRICH_WORKDIR", str(ROOT / "runs" / "clip-enrich")))
STATE_PATH = WORKDIR / "state.json"
STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
MARKER = "clip-enrich:v1"
CLIP_RE = re.compile(r"/clip/([A-Za-z0-9]{16,})")
DEFAULT_PROJECTS = [
    "bfhqkkn9ofbk",  # Pod Factory
    "m4c5fngzfbtx",  # Smartware Factory
    "oxju1frzaz6q",  # Coffee Factory
    "w1l9zhbscg8j",  # expresso Factory
    "kynsde4gp1bf",  # CaseAid Factory
    "tsp8hn56rmn3",  # ChadAI Factory
]
OPEN_STATUSES = ("TO DO", "READY", "IN PROGRESS")


def j(r) -> dict:
    try:
        return json.loads(r["result"]["content"][0]["text"])
    except Exception:
        return {"_err": str(r)[:250]}


def brief_blocks(document_hash) -> list:
    """Read a task document's blocks; tolerant of response-shape variants."""
    if not document_hash:
        return []
    doc = j(mcp_call("GetDocumentByDocumentHash", {"workspace": WS, "document_hash": document_hash}))
    d = doc.get("data") or {}
    return d.get("blocks") or (d.get("document") or {}).get("blocks") or []


def log(msg):
    print(msg, flush=True)


def load_state():
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            return {}
    return {}


def save_state(state):
    STATE_PATH.write_text(json.dumps(state, indent=1))


def _child_text(ch) -> str:
    """Recursively flatten a block child; captures link URLs too."""
    if not isinstance(ch, dict):
        return ""
    t = ch.get("text", "") or ""
    for c in (ch.get("children") or []):
        t += _child_text(c)
    u = ch.get("url")
    if u and u not in t:
        t += (" " if t else "") + u
    return t


def doc_text(blocks) -> str:
    return "\n".join("".join(_child_text(c) for c in (b.get("children") or [])) for b in blocks)


def comments_of(task_hash):
    c = j(mcp_call("GetTaskComment", {"workspace": WS, "task_hash": task_hash, "limit": 100}))
    out = []
    for cm in ((c.get("data") or {}).get("result") or []):
        out.append("\n".join("".join(ch.get("text", "") for ch in (b.get("children") or [])) for b in (cm.get("blocks") or [])))
    return out


def extract_clip_links(text):
    seen, out = set(), []
    for m in CLIP_RE.finditer(text or ""):
        h = m.group(1)
        if h not in seen:
            seen.add(h)
            out.append(h)
    return out


def is_enriched(comment_texts, brief_text):
    if MARKER in (brief_text or ""):
        return True
    if "CLIP ANALYSIS" in (brief_text or ""):
        return True
    return any(MARKER in t for t in comment_texts)


def fetch(url, timeout=180):
    req = urllib.request.Request(url, headers=UA)
    resp = urllib.request.urlopen(req, timeout=timeout)
    return resp.status, resp.headers.get("content-type", ""), resp.read()


def native_clip(clip_hash):
    r = j(mcp_call("GetClipsByClipHash", {"workspace": WS, "clip_hash": clip_hash}))
    d = r.get("data") or {}
    if isinstance(d, dict):
        return d.get("clip") or (d if d.get("clip_hash") else None)
    return None


def resolve_clip(clip_hash):
    """Native integration lane first (Sep 17); public-share lane as fallback."""
    try:
        c = native_clip(clip_hash)
        if c:
            return c
    except Exception:
        pass
    st, ct, body = fetch(f"{HOST}/api/v1/clips/{clip_hash}?subdomain={WS}", timeout=60)
    data = json.loads(body)
    return (data.get("data") or {}).get("clip") or {}


def _file_hash_from(full_path):
    m = re.search(r"file_hash=([A-Za-z0-9_\-]+)", full_path or "")
    return m.group(1) if m else None


def fetch_clip_file(full_path, timeout=600):
    """Minted-link fetch (native lane); falls back to the direct public path."""
    fh = _file_hash_from(full_path)
    if fh:
        try:
            dl = j(mcp_call("GetFileDownloadLinkByFileHash", {"workspace": WS, "file_hash": fh}))
            d = dl.get("data") or {}
            url = d.get("url") or d.get("download_url") or d.get("link") or ""
            if url:
                st, ct, data = fetch((HOST + url) if url.startswith("/") else url, timeout=timeout)
                return data
        except Exception:
            pass
    st, ct, data = fetch(HOST + full_path, timeout=timeout)
    return data


def native_transcribe(clip_hash):
    """Coffee-side transcription; polls up to ~3 min for the transcript to appear."""
    try:
        t = j(mcp_call("PostClipsTranscribe", {"workspace": WS, "clip_hash": clip_hash, "requestBody": {"force": False}}))
        if not t.get("success"):
            return None
        for _ in range(12):
            time.sleep(15)
            c = native_clip(clip_hash) or {}
            if c.get("transcript_text"):
                return c["transcript_text"]
    except Exception:
        return None
    return None


def ffprobe_duration(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True)
    try:
        return float(p.stdout.strip())
    except Exception:
        return None


def extract_media(webm, work):
    wav = work / "audio.wav"
    frames_dir = work / "frames"
    frames_dir.mkdir(exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-i", str(webm), "-vn", "-ac", "1", "-ar", "16000", str(wav)],
                   capture_output=True, text=True)
    subprocess.run(["ffmpeg", "-y", "-i", str(webm), "-vf", "fps=1/6,scale='min(1920,iw)':-2",
                    "-q:v", "4", str(frames_dir / "%02d.jpg")], capture_output=True, text=True)
    frames = sorted(frames_dir.glob("*.jpg"))
    return wav, frames


def transcribe(wav):
    py = os.environ.get("CLIP_ENRICH_WHISPER_PY", "/opt/data/whisper-venv/bin/python")
    if not Path(py).exists():
        return None, f"whisper python not found at {py}"
    helper = ROOT / "scripts" / "clip-transcribe.py"
    p = subprocess.run([py, str(helper), str(wav)], capture_output=True, text=True, timeout=1800)
    if p.returncode != 0:
        return None, f"transcribe failed: {p.stderr[:200]}"
    return p.stdout.strip(), None


def vision_notes(frame_paths, max_frames):
    base = os.environ.get("CLIP_ENRICH_VISION_BASE_URL")
    key = os.environ.get("CLIP_ENRICH_VISION_API_KEY")
    model = os.environ.get("CLIP_ENRICH_VISION_MODEL")
    if not (base and key and model):
        return None, "vision endpoint not configured (skipped)"
    if len(frame_paths) > max_frames:
        step = len(frame_paths) / max_frames
        frame_paths = [frame_paths[int(i * step)] for i in range(max_frames)]
    notes = []
    max_tokens = 4000
    for i, fp in enumerate(frame_paths):
        b64 = base64.b64encode(fp.read_bytes()).decode()
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": "Keyframe from a screen recording giving product feedback. Reply with the final answer only: in 1-3 sentences, what UI state is on screen (app, panel, fields, values, cursor) and any visible friction."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
            ]}],
            "max_tokens": max_tokens,
        }
        req = urllib.request.Request(base.rstrip("/") + "/chat/completions", data=json.dumps(payload).encode(),
                                     headers={**UA, "Content-Type": "application/json", "Authorization": f"Bearer {key}"})
        try:
            resp = urllib.request.urlopen(req, timeout=180)
            out = json.loads(resp.read())
            msg = out.get("choices", [{}])[0].get("message", {}) or {}
            content = (msg.get("content") or "").strip()
            if not content:
                # reasoning-model fallback: the answer sometimes lands inside reasoning_content
                r = (msg.get("reasoning_content") or "").strip()
                if r:
                    tail = r[-600:]
                    parts = [s for s in re.split(r"(?<=[.!?])\s+", tail) if s.strip()]
                    content = " ".join(parts[-3:])[:320]
            notes.append(f"- frame {i+1}: " + (content or "(no model output)")[:320])
        except Exception as e:  # noqa: BLE001
            detail = ""
            try:
                detail = e.read()[:200].decode("utf-8", "replace")  # type: ignore[attr-defined]
            except Exception:  # noqa: BLE001
                pass
            return None, f"vision call failed: {e} {detail}"
    return "\n".join(notes), None


def build_digest(clip, clip_hash, transcript, vnotes, vnote_err, n_frames, duration):
    lines = [
        "CLIP ANALYSIS \u2014 agent\u2019s-eye view (clip-intake enrichment, %s)" % time.strftime("%Y-%m-%d"),
        "",
        f"Source: clip `{clip_hash}` (\u201c{clip.get('title','')}\u201d, {clip.get('source','screen')} recording, "
        f"{int((clip.get('duration_ms') or 0)/1000)} s). Fetched via the public lane; audio transcribed locally; keyframes via ffmpeg.",
        "",
        "TRANSCRIPT (verbatim)" if transcript else "TRANSCRIPT: unavailable for this run.",
        transcript or "",
        "",
        f"VISUAL NOTES ({n_frames} keyframes extracted)",
        vnotes or f"(vision notes unavailable: {vnote_err})",
        "",
        "HOW THIS WAS FETCHED (reproducible)",
        "- Clip record: MCP `GetClipsByClipHash` (native; public share lane as fallback).",
        "- Media: `GetFileDownloadLinkByFileHash` minted link from the clip's file_hash (fallback: direct path).",
        "- Transcript: Coffee `PostClipsTranscribe` when available (fallback: local faster-whisper); keyframes: ffmpeg \u2192 vision model.",
        "- Automated by `scripts/clip-enrich.py` (factory worker).",
    ]
    return "\n".join(lines)


def post_comment(task_hash, text):
    return bool(j(mcp_call("PostTaskComment", {"workspace": WS, "task_hash": task_hash,
                                               "requestBody": {"text": text[:15000]}})).get("success"))


def upload_attach(task_hash, path, title, tries=3):
    for k in range(tries):
        try:
            b64 = base64.b64encode(path.read_bytes()).decode()
            up = j(mcp_call("PostFileUploadBase64", {"workspace": WS, "requestBody": {"name": path.name, "content_base64": b64}}))
            fh = ((up.get("data") or {}).get("private_file_hash")) or ((up.get("data") or {}).get("file_hash"))
            if fh:
                art = j(mcp_call("PostTaskArtifact", {"workspace": WS, "task_hash": task_hash,
                                                      "requestBody": {"private_file_hash": fh, "kind": "data", "title": title}}))
                if art.get("success") or art.get("data"):
                    return True
        except Exception:
            pass
        time.sleep(3 * (k + 1))
    return False


def process_card(task_hash, clip_hashes, execute, work_root):
    result = {"task": task_hash, "status": "noop", "detail": ""}
    work = work_root / task_hash
    work.mkdir(parents=True, exist_ok=True)
    clip_hash = clip_hashes[0]
    try:
        clip = resolve_clip(clip_hash)
    except Exception as e:
        result.update(status="error", detail=f"resolve failed: {e}")
        return result
    vpath = ((clip.get("video") or {}).get("full_path"))
    if not vpath:
        result.update(status="error", detail="clip record has no video path")
        return result
    webm = work / "clip.webm"
    webm.write_bytes(fetch_clip_file(vpath, timeout=600))
    duration = ffprobe_duration(webm)
    transcript = clip.get("transcript_text") or None
    if not transcript and os.environ.get("CLIP_ENRICH_TRANSCRIBE", "auto") in ("auto", "native"):
        transcript = native_transcribe(clip_hash)
    wav, frames = extract_media(webm, work)
    if not transcript:
        transcript, terr = transcribe(wav)
    vnotes, verr = vision_notes(frames, int(os.environ.get("CLIP_ENRICH_MAX_FRAMES", "8")))
    poster = None
    ppath = ((clip.get("preview_thumbnail") or {}).get("full_path"))
    if ppath:
        try:
            poster = work / "poster.jpg"
            poster.write_bytes(fetch_clip_file(ppath, timeout=60))
        except Exception:
            poster = None
    digest = build_digest(clip, clip_hash, transcript, vnotes, verr, len(frames), duration)
    (work / "digest.txt").write_text(digest)  # operator-reviewable artifact (both modes)
    result["digest_chars"] = len(digest)
    result["frames"] = len(frames)
    result["transcript_chars"] = len(transcript or "")
    if not execute:
        result.update(status="would-enrich",
                      detail=f"clip {clip_hash[:8]}… \u00b7 {int((duration or 0))}s \u00b7 transcript {len(transcript or '')}c \u00b7 frames {len(frames)} \u00b7 vision {'yes' if vnotes else 'no'} \u00b7 digest {len(digest)}c (dry-run)")
        return result
    chunks = [digest[i:i + 3400] for i in range(0, len(digest), 3400)]
    blocks = [{"id": f"ce-{i}", "type": "paragraph", "children": [{"text": c}]} for i, c in enumerate(chunks)]
    v = j(mcp_call("GetTaskByTaskHash", {"workspace": WS, "task_hash": task_hash}))
    doc = ((v.get("data") or {}).get("task") or {}).get("document_hash")
    a = j(mcp_call("PostDocumentDocumentBlockAppend", {"workspace": WS, "document_hash": doc, "requestBody": {
        "blocks": blocks, "client_id": "clip-enrich-" + str(int(time.time())), "time": int(time.time() * 1000)}}))
    attached = 0
    if poster:
        attached += upload_attach(task_hash, poster, "clip poster")
    for fp in frames[:3]:
        attached += upload_attach(task_hash, fp, f"keyframe \u00b7 {fp.stem}")
    post_comment(task_hash, f"{MARKER} \u2014 digest appended to the brief ({len(digest)}c; transcript {len(transcript or '')}c; "
                            f"{len(frames)} keyframes, {attached} attachments). Themes extracted for the planner/reviewer.")
    result.update(status="enriched", detail=f"blocks={len(blocks)} append={bool(a.get('success'))} attachments={attached}")
    return result


def candidates_for_project(project, limit, state):
    r = j(mcp_call("GetTask", {"workspace": WS, "project_hashes": [project], "limit": limit}))
    rows = (r.get("data") or {}).get("result") or []
    out = []
    for t in rows:
        h = t.get("task_hash")
        if not h or t.get("is_trashed"):
            continue
        sts = [(p.get("task_status") or {}).get("title") for p in (t.get("task_project") or [])]
        if sts and sts[0] not in OPEN_STATUSES:
            continue
        if h in state:
            continue
        v = j(mcp_call("GetTaskByTaskHash", {"workspace": WS, "task_hash": h}))
        tt = (v.get("data") or {}).get("task") or {}
        brief = doc_text(brief_blocks(tt.get("document_hash")))
        cms = comments_of(h)
        links = extract_clip_links(brief) + [x for t_ in cms for x in extract_clip_links(t_)]
        if not links:
            continue
        if is_enriched(cms, brief):
            state[h] = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "outcome": "already-enriched"}
            out.append((h, []))
            continue
        out.append((h, links))
    return out


def main():
    ap = argparse.ArgumentParser(description="Clip-intake enrichment worker (dry-run by default).")
    ap.add_argument("--project", action="append", default=[], help="project hash(es); default: all six factory lines")
    ap.add_argument("--task", help="single task hash")
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--execute", action="store_true", help="post the enrichment (default: dry-run)")
    ap.add_argument("--reprocess", action="store_true", help="ignore markers/state")
    a = ap.parse_args()

    state = {} if a.reprocess else load_state()
    todo = []
    if a.task:
        v = j(mcp_call("GetTaskByTaskHash", {"workspace": WS, "task_hash": a.task}))
        tt = (v.get("data") or {}).get("task") or {}
        brief = doc_text(brief_blocks(tt.get("document_hash")))
        cms = comments_of(a.task)
        links = extract_clip_links(brief) + [x for t_ in cms for x in extract_clip_links(t_)]
        if not links:
            log(f"NOOP {a.task}: no clip link found")
            return
        if is_enriched(cms, brief) and not a.reprocess:
            log(f"SKIP {a.task}: already enriched ({MARKER})")
            return
        todo = [(a.task, links)]
    else:
        projects = a.project or DEFAULT_PROJECTS
        for p in projects:
            todo.extend(candidates_for_project(p, a.limit, state))
        save_state(state)

    if not todo:
        log("clip-enrich: no candidates.")
        return
    for h, links in todo:
        if not links:
            log(f"skip {h}: already enriched")
            continue
        res = process_card(h, links, a.execute, WORKDIR / "work")
        log(f"{res['status'].upper()} {h}: {res.get('detail','')}")
        state[h] = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "outcome": res["status"]}
        save_state(state)


if __name__ == "__main__":
    main()
