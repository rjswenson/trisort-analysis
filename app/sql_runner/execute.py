from __future__ import annotations

import time
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.sql_runner.history import log_query_execution


def run_sql(engine: Engine, sql_text: str, query_name: str | None = None) -> dict[str, Any]:
	start = time.perf_counter()
	try:
		with engine.begin() as conn:
			result = conn.execute(text(sql_text))
			is_rows = bool(result.returns_rows)
			rows = [dict(r) for r in result.mappings().all()] if is_rows else []
			row_count = len(rows) if is_rows else int(result.rowcount or 0)

		duration_ms = int((time.perf_counter() - start) * 1000)
		log_query_execution(
			engine,
			query_name=query_name,
			sql_text=sql_text,
			duration_ms=duration_ms,
			row_count=row_count,
			success=True,
		)
		return {
			"rows": rows,
			"row_count": row_count,
			"duration_ms": duration_ms,
			"success": True,
		}
	except Exception as exc:
		duration_ms = int((time.perf_counter() - start) * 1000)
		log_query_execution(
			engine,
			query_name=query_name,
			sql_text=sql_text,
			duration_ms=duration_ms,
			row_count=None,
			success=False,
			error_message=str(exc),
		)
		raise
