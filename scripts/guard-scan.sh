#!/usr/bin/env bash
# guard-scan — mechanical diff-integrity scan for factory branches.
#
# Usage: scripts/guard-scan.sh <repo-path> [base-ref]
#   base-ref defaults to origin/main.
#
# This is the BLOCKING mechanical check at Review (LLM review and mechanical
# review are not interchangeable — see docs/techno-os.md §5). It is a
# heuristic + blocklist scanner, not a proof; human review still reads the
# diff. Exit 0 = clean, 1 = findings (fix or justify in the PR).

set -u

REPO="${1:?usage: guard-scan.sh <repo-path> [base-ref]}"
BASE="${2:-origin/main}"
cd "$REPO" || exit 2

FINDINGS=0
note() { printf '%s\n' "$*"; }
flag() { FINDINGS=$((FINDINGS + 1)); printf '⚠️  %s\n' "$*"; }

DIFF=$(git diff "$BASE"...HEAD --stat=200 2>/dev/null) || { echo "cannot diff $BASE...HEAD"; exit 2; }
FULL=$(git diff "$BASE"...HEAD 2>/dev/null)

note "== guard-scan =="
note "repo: $REPO | base: $BASE | head: $(git rev-parse --short HEAD)"
note
note "$DIFF"
note

# 1. Changed-file census
CHANGED=$(git diff "$BASE"...HEAD --name-only | cat)
COUNT=$(printf '%s\n' "$CHANGED" | grep -c . || true)
note "changed files: $COUNT"

# 2. Blocked paths — secrets, VCS internals, vendored trees
while IFS= read -r f; do
  [ -z "$f" ] && continue
  case "$f" in
    .env|.env.*|*.pem|*.key|*.p12|.npmrc|.netrc) flag "blocked path changed: $f" ;;
    .git/*) flag "VCS internals touched: $f" ;;
    node_modules/*) flag "vendored tree touched: $f" ;;
  esac
done <<EOF
$CHANGED
EOF

# 3. Added-line heuristics
ADDED=$(printf '%s\n' "$FULL" | grep -E '^\+' | grep -v '^\+\+\+' || true)

LONGLINES=$(printf '%s\n' "$ADDED" | awk 'length($0) > 300 { c++ } END { print c+0 }')
[ "$LONGLINES" -gt 0 ] && flag "long added lines (>300 chars): $LONGLINES — minification/obfuscation hazard"

printf '%s\n' "$ADDED" | grep -Eq 'atob\(' && flag "added 'atob(' — encoded payload signature"
printf '%s\n' "$ADDED" | grep -Eq 'eval\("global\.' && flag "added 'eval(\"global.' — codegen signature"
printf '%s\n' "$ADDED" | grep -Eq "global\.[a-zA-Z_]+ *= *['\"][0-9]{3,}-" && flag "added 'global.x=\"<digits>-' codegen signature"

# 4. Lockfile churn — allowed, must be justified in the PR
printf '%s\n' "$CHANGED" | grep -qE '^package-lock\.json$' && flag "package-lock.json changed — lockfile churn requires justification in the PR"

# 5. Binary additions without explicit naming
BINS=$(git diff "$BASE"...HEAD --numstat | awk -F'\t' '$1=="-" && $2=="-" {print $3}')
[ -n "$BINS" ] && flag "binary file(s) in diff: $(printf '%s' "$BINS" | tr '\n' ' ')"

# 6. Scale guard
if [ "$COUNT" -gt 25 ]; then flag "diff touches $COUNT files — confirm no unrelated-file edits"; fi

note
if [ "$FINDINGS" -eq 0 ]; then
  note "clean — no findings"
  exit 0
else
  note "findings: $FINDINGS (each must be fixed or justified in the PR)"
  exit 1
fi
