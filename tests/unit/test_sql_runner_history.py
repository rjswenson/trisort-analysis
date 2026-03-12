from sqlalchemy import create_engine, text

from app.sql_runner.execute import run_sql
from app.sql_runner.history import get_query_history


def _prepare_history_schema(engine) -> None:
	with engine.begin() as conn:
		conn.execute(
			text(
				"""
				CREATE TABLE query_history (
					query_id INTEGER PRIMARY KEY AUTOINCREMENT,
					query_name TEXT,
					sql_text TEXT NOT NULL,
					executed_at TEXT DEFAULT CURRENT_TIMESTAMP,
					duration_ms INTEGER,
					row_count INTEGER,
					success BOOLEAN NOT NULL,
					error_message TEXT
				)
				"""
			)
		)


def test_successful_query_logged_with_row_count() -> None:
	engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
	_prepare_history_schema(engine)

	result = run_sql(engine, "SELECT 1 AS n", query_name="smoke")
	assert result["success"] is True
	assert result["row_count"] == 1

	history = get_query_history(engine, limit=5)
	assert len(history) == 1
	assert history[0]["query_name"] == "smoke"
	assert bool(history[0]["success"]) is True
	assert history[0]["row_count"] == 1


def test_failed_query_logged_with_error() -> None:
	engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
	_prepare_history_schema(engine)

	try:
		run_sql(engine, "SELECT * FROM does_not_exist")
	except Exception:
		pass

	history = get_query_history(engine, limit=5)
	assert len(history) == 1
	assert bool(history[0]["success"]) is False
	assert history[0]["error_message"] is not None
