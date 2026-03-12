from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine


def log_query_execution(
	engine: Engine,
	query_name: str | None,
	sql_text: str,
	duration_ms: int,
	row_count: int | None,
	success: bool,
	error_message: str | None = None,
) -> None:
	query = text(
		"""
		INSERT INTO query_history (
			query_name, sql_text, duration_ms, row_count, success, error_message
		) VALUES (
			:query_name, :sql_text, :duration_ms, :row_count, :success, :error_message
		)
		"""
	)
	with engine.begin() as conn:
		conn.execute(
			query,
			{
				"query_name": query_name,
				"sql_text": sql_text,
				"duration_ms": duration_ms,
				"row_count": row_count,
				"success": success,
				"error_message": error_message,
			},
		)


def get_query_history(engine: Engine, limit: int = 20) -> list[dict[str, Any]]:
	query = text(
		"""
		SELECT query_id, query_name, sql_text, executed_at, duration_ms, row_count, success, error_message
		FROM query_history
		ORDER BY query_id DESC
		LIMIT :limit
		"""
	)
	with engine.begin() as conn:
		rows = conn.execute(query, {"limit": limit}).mappings().all()
		return [dict(r) for r in rows]
