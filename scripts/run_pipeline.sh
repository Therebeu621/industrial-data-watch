#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"

if [ ! -x "$PYTHON_BIN" ]; then
  echo "Python environment not found at $PYTHON_BIN. Run 'make install' first." >&2
  exit 1
fi

"$PYTHON_BIN" -m src.main all "$@"
