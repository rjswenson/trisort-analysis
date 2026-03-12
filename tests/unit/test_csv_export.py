from pathlib import Path

from sqlalchemy import create_engine, text

from app.config import Settings
from app.export.csv_export import export_saved_query_to_csv


def _prepare_export_schema(engine) -> None:
	with engine.begin() as conn:
		conn.execute(
			text(
				"""
				CREATE TABLE query_saved (
					saved_query_id INTEGER PRIMARY KEY AUTOINCREMENT,
					name TEXT NOT NULL UNIQUE,
					sql_text TEXT NOT NULL,
					tags TEXT,
					created_at TEXT DEFAULT CURRENT_TIMESTAMP,
					updated_at TEXT DEFAULT CURRENT_TIMESTAMP
				)
				"""
			)
		)
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
		conn.execute(text("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"))
		conn.execute(text("INSERT INTO items (name) VALUES ('alpha'), ('beta')"))
		conn.execute(
			text("INSERT INTO query_saved (name, sql_text) VALUES ('list_items', 'SELECT id, name FROM items ORDER BY id')")
		)


def test_export_saved_query_to_csv_writes_file(tmp_path: Path) -> None:
	db_path = tmp_path / "test.db"
	engine = create_engine(f"sqlite+pysqlite:///{db_path}", future=True)
	_prepare_export_schema(engine)

	settings = Settings(database_url=f"sqlite+pysqlite:///{db_path}")
	out_path = tmp_path / "out.csv"
	result = export_saved_query_to_csv(settings, query_name="list_items", out_path=str(out_path))

	assert result["row_count"] == 2
	content = out_path.read_text(encoding="utf-8")
	assert "id,name" in content
	assert "1,alpha" in content
	assert "2,beta" in content
