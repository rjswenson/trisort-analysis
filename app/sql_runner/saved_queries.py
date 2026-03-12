from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine


def save_query(engine: Engine, name: str, sql_text: str) -> None:
	query = text(
		"""
		INSERT INTO query_saved (name, sql_text, updated_at)
		VALUES (:name, :sql_text, CURRENT_TIMESTAMP)
		ON CONFLICT (name)
		DO UPDATE SET
			sql_text = EXCLUDED.sql_text,
			updated_at = CURRENT_TIMESTAMP
		"""
	)
	with engine.begin() as conn:
		conn.execute(query, {"name": name, "sql_text": sql_text})


def get_saved_query_sql(engine: Engine, name: str) -> str:
	query = text("SELECT sql_text FROM query_saved WHERE name = :name")
	with engine.begin() as conn:
		value = conn.execute(query, {"name": name}).scalar_one_or_none()
		if value is None:
			raise ValueError(f"Saved query not found: {name}")
		return str(value)
