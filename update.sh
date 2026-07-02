#!/usr/bin/env bash
#
# update.sh — sync APP CODE ONLY to git.
#
# Commits your editable web-app code (sensor_server.py, wind_refresh.py, the
# weather/sensor helper modules, templates, static assets) and a fresh
# requirements.txt snapshot. It deliberately does NOT touch:
#   - the venv/        (rebuilt from requirements.txt, never committed)
#   - infrastructure/  (system configs/units — committed separately, on purpose)
#   - runtime data     (*.jsonl, *.log, caches)
#
# Run from the repo root:  ./update.sh "your commit message"
#
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # repo root = where this lives

MSG="${1:-Update app code}"

# 1. Snapshot the venv's packages so a rebuild can recreate the environment.
#    Prefer the venv's own pip; fall back to active python -m pip.
if [[ -x venv/bin/pip ]]; then
  venv/bin/pip freeze > requirements.txt
  echo "requirements.txt updated ($(wc -l < requirements.txt) packages)"
else
  echo "WARNING: venv/bin/pip not found — requirements.txt NOT updated" >&2
fi

# 2. Stage ONLY app code. List the things you actually edit; the .gitignore
#    (below) is the backstop, but being explicit here means an accidental
#    stray file never sneaks into an app commit.
git add \
  sensor_server.py \
  wind_refresh.py \
  weather_calc.py \
  sensor_data.py \
  config_py.py \
  requirements.txt \
  templates/ \
  static/ \
  2>/dev/null || true

# Also pick up any other tracked .py at repo root that changed, but never the
# venv or infrastructure (those are handled by .gitignore + explicit excludes).
git add ./*.py 2>/dev/null || true

# 3. Show what's about to be committed and bail if nothing changed.
if git diff --cached --quiet; then
  echo "No app-code changes to commit."
  exit 0
fi

echo
echo "=== About to commit: ==="
git diff --cached --name-only
echo "========================"
read -rp "Proceed? [y/N] " ok
[[ "$ok" =~ ^[Yy]$ ]] || { git reset -q; echo "Aborted (unstaged)."; exit 1; }

git commit -m "$MSG"
git push
echo "Done."
