#!/usr/bin/env bash
set -euo pipefail

# Sanity checks
command -v uv >/dev/null 2>&1 || { echo "uv not found on PATH"; exit 1; }
test -f pyproject.toml || { echo "pyproject.toml missing in workspace root"; exit 1; }

# Read Python version from python-version file if it exists
if [ -f python-version ]; then
  PYTHON_VERSION=$(cat python-version | tr -d '[:space:]')
  echo "Using Python version from python-version file: $PYTHON_VERSION"
  export UV_PYTHON="$PYTHON_VERSION"
fi

# Ensure the target dir exists
mkdir -p "${UV_PROJECT_ENVIRONMENT:-/home/vscode/.venv}"

# If there is no lockfile yet, create one. Then sync.
if [ -f uv.lock ]; then
  uv sync --frozen --no-install-project
else
  uv lock
  uv sync --no-install-project
fi

# Optional: print the interpreter that VS Code should use
echo "----------------------"
echo "UV virtual environment details:"
uv run python -c "import sys,sysconfig; print(sys.executable); print(sys.version)"
