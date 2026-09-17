#!/usr/bin/env bash
# clip-enrich scheduled runner — clip-intake enrichment for the factory lines.
# Schedule entry point: copy this to your hermes profile's scripts dir and adjust the
# placeholders (<home>, <workspaces>) to your machine. Source of truth: scripts/clip-enrich.py.
# Sweeps all six factory lines and enriches new clip cards.
# Silent unless a card was enriched; failures are printed (watchdog pattern).
set -uo pipefail
export PATH="<home>/.local/bin:$PATH"
cd <workspaces>/techno-factory
[ -f <workspaces>/uploads/clip-enrich.env ] && set -a && . <workspaces>/uploads/clip-enrich.env && set +a
[ -f <workspaces>/uploads/factory-local.env ] && set -a && . <workspaces>/uploads/factory-local.env && set +a
rc=0
out="$(python3 scripts/clip-enrich.py --execute 2>> runs/clip-enrich/cron.err.log)" || rc=$?
if [ "$rc" -ne 0 ]; then
  echo "clip-enrich FAILED (rc=$rc) — see runs/clip-enrich/cron.err.log"
  exit 0
fi
echo "$out" | grep -E "ENRICHED|ERROR" || true
