#!/usr/bin/env bash
# ci-heal scheduled runner — scans for red CI on factory branches and notifies via Coffee.
# Runs every 30 minutes (hermes cron, no_agent mode). Deterministic; no LLM.
set -euo pipefail
export PATH="<home>/home/.local/bin:$PATH"   # gh lives here (cron PATH safety)
cd <workspaces>/techno-factory
exec python3 scripts/ci-heal.py
