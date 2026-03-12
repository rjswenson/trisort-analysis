#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${DATABASE_URL:-}" ]]; then
	echo "DATABASE_URL is required" >&2
	exit 1
fi

echo "Applying schema..."
python - <<'PY'
from sqlalchemy import create_engine, text
from pathlib import Path
import os

engine = create_engine(os.environ["DATABASE_URL"], future=True)
sql_files = [
		Path("sql/001_schema.sql"),
		Path("sql/002_indexes.sql"),
		Path("sql/003_views.sql"),
		Path("sql/900_seed_saved_queries.sql"),
]

with engine.begin() as conn:
		for path in sql_files:
				conn.execute(text(path.read_text(encoding="utf-8")))
				print(f"Applied: {path}")
PY

echo "Database bootstrap complete."
