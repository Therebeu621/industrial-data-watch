#!/usr/bin/env bash
set -euo pipefail

psql "${DATABASE_URL:-postgresql://industrial_user:industrial_pass@localhost:55432/industrial_watch}" \
  -f sql/schema.sql
