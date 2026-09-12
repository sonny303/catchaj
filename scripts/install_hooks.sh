#!/usr/bin/env bash
# Helper script to install pre-commit leak-prevention hooks.
set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

echo "=== Installing Pre-Commit Leak-Prevention Hooks ==="

# Ensure scripts and hooks are executable
chmod +x scripts/pre_commit_scan.py
chmod +x .githooks/pre-commit

# Resolve git directory (handles standard repos, worktrees, submodules)
GIT_DIR="$(git rev-parse --git-dir 2>/dev/null || echo ".git")"
if [ -d "$GIT_DIR" ]; then
    mkdir -p "$GIT_DIR/hooks"
    cp .githooks/pre-commit "$GIT_DIR/hooks/pre-commit"
    chmod +x "$GIT_DIR/hooks/pre-commit"
    echo "[✓] Pre-commit hook successfully copied to $GIT_DIR/hooks/pre-commit"
fi

# Configure git core.hooksPath to point to .githooks as well
git config core.hooksPath .githooks
echo "[✓] Git core.hooksPath configured to .githooks"

# Select Python binary for test execution
if [ -n "$VIRTUAL_ENV" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
    PYTHON_BIN="$VIRTUAL_ENV/bin/python"
elif [ -x ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
else
    PYTHON_BIN="python"
fi

echo "[✓] Test run pre-commit scanner:"
"$PYTHON_BIN" scripts/pre_commit_scan.py --test
