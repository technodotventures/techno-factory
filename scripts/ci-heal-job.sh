#!/usr/bin/env bash
# ci-heal scheduled runner — CI failure watchdog for the factory.
# Schedule entry point: copy this to your hermes profile's scripts dir and adjust the
# placeholders (<home>, <workspaces>) to your machine. Source of truth: scripts/ci-heal.py.
set -euo pipefail
export PATH="<home>/.local/bin:$PATH"
cd <workspaces>/techno-factory
[ -f <workspaces>/uploads/factory-local.env ] && set -a && . <workspaces>/uploads/factory-local.env && set +a
exec python3 scripts/ci-heal.py
