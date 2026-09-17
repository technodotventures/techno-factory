#!/usr/bin/env bash
# clip-enrich scheduled runner — clip-intake enrichment for the factory lines.
# Schedule entry point: copy this to your hermes profile's scripts dir and adjust the
# placeholders (<home>, <workspaces>) to your machine. Source of truth: scripts/clip-enrich.py.
# Sweeps all six factory lines and enriches new clip cards. Silent unless something moved.
set -euo pipefail
export PATH="<home>/.local/bin:$PATH"
cd <workspaces>/techno-factory
[ -f <workspaces>/uploads/clip-enrich.env ] && set -a && . <workspaces>/uploads/clip-enrich.env && set +a
python3 scripts/clip-enrich.py --execute 2>> runs/clip-enrich/cron.err.log | grep -E "ENRICHED|ERROR" || true
