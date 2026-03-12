from __future__ import annotations

import csv
from pathlib import Path

from app.config import Settings
from app.db import create_db_engine
from app.sql_runner.execute import run_sql
from app.sql_runner.saved_queries import get_saved_query_sql


def export_saved_query_to_csv(settings: Settings, query_name: str, out_path: str) -> dict:
	engine = create_db_engine(settings)
	sql_text = get_saved_query_sql(engine, query_name)
	result = run_sql(engine, sql_text, query_name=query_name)
	rows = result["rows"]

	output = Path(out_path)
	output.parent.mkdir(parents=True, exist_ok=True)
	with output.open("w", newline="", encoding="utf-8") as f:
		if rows:
			writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
			writer.writeheader()
			writer.writerows(rows)
		else:
			f.write("")

	return {
		"out_path": str(output),
		"row_count": result["row_count"],
		"duration_ms": result["duration_ms"],
	}
