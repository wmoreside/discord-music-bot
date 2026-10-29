#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$PROJECT_DIR/.venv/bin/python"

if [[ ! -x "$PYTHON" ]]; then
    echo "Virtual environment not found at $PROJECT_DIR/.venv" >&2
    echo "Create it and install the bot with: python3 -m venv .venv && .venv/bin/pip install ." >&2
    exit 1
fi

cd "$PROJECT_DIR"
exec "$PYTHON" bot.py
