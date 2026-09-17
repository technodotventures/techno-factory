#!/usr/bin/env bash
# spec-advance scheduled runner — native-lane stations for the factory lines (Mt14Eiext).
# Schedule entry point: copy to your hermes profile's scripts dir and adjust the placeholders
# (<home>, <workspaces>). Source of truth: scripts/spec-advance.py.
# Silent unless something moved; failures are printed (watchdog pattern).
set -uo pipefail
export PATH="<home>/.local/bin:$PATH"
cd <workspaces>/techno-factory
[ -f <workspaces>/uploads/factory-local.env ] && set -a && . <workspaces>/uploads/factory-local.env && set +a
rc=0
out="$(python3 scripts/spec-advance.py --execute 2>> runs/spec-advance/cron.err.log)" || rc=$?
if [ "$rc" -ne 0 ]; then
  echo "spec-advance FAILED (rc=$rc) — see runs/spec-advance/cron.err.log"
  exit 0
fi
echo "$out" | grep -E "DISPATCHED|ADVANCED|ERROR" || true
