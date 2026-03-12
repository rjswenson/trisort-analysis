import typer
from pathlib import Path

from app.config import get_settings
from app.db import check_db_connection, create_db_engine
from app.export.csv_export import export_saved_query_to_csv
from app.logging import configure_logging
from app.sql_runner.execute import run_sql
from app.sql_runner.history import get_query_history
from app.sql_runner.saved_queries import save_query
from app.sync.orchestrator import run_sync_dry_run, run_sync_full, run_sync_incremental, run_sync_mock

app = typer.Typer(help="Trisort local Jira sync and analysis CLI")
sync_app = typer.Typer(help="Synchronization commands")
sql_app = typer.Typer(help="SQL query commands")
export_app = typer.Typer(help="Export commands")
app.add_typer(sync_app, name="sync")
app.add_typer(sql_app, name="sql")
app.add_typer(export_app, name="export")


@app.command("doctor")
def doctor() -> None:
	settings = get_settings()
	configure_logging(settings.log_level)

	missing = settings.missing_required_runtime_fields()
	if missing:
		joined = ", ".join(missing)
		raise typer.BadParameter(f"Missing required environment variables: {joined}")

	engine = create_db_engine(settings)
	check_db_connection(engine)
	typer.echo("OK: runtime config and database connectivity look good.")


@sync_app.command("full")
def sync_full() -> None:
	settings = get_settings()
	configure_logging(settings.log_level)
	result = run_sync_full(settings)
	typer.echo(f"Sync full complete: rows_read={result['rows_read']} rows_written={result['rows_written']}")


@sync_app.command("incremental")
def sync_incremental() -> None:
	settings = get_settings()
	configure_logging(settings.log_level)
	result = run_sync_incremental(settings)
	typer.echo(
		"Sync incremental complete: "
		f"rows_read={result['rows_read']} rows_written={result['rows_written']} "
		f"watermark_in={result['watermark_in']} watermark_out={result['watermark_out']}"
	)


@sync_app.command("dry-run")
def sync_dry_run() -> None:
	settings = get_settings()
	configure_logging(settings.log_level)
	result = run_sync_dry_run(settings)
	typer.echo(f"Sync dry-run complete: rows_read={result['rows_read']} rows_written={result['rows_written']}")


@sync_app.command("mock")
def sync_mock(
	fixture_path: str = typer.Option("mocks", help="Path to mock fixture directory"),
	write_to_db: bool = typer.Option(False, help="Write mock run data into Postgres"),
) -> None:
	settings = get_settings()
	configure_logging(settings.log_level)
	result = run_sync_mock(settings, fixture_path=fixture_path, write_to_db=write_to_db)
	typer.echo(
		f"Sync mock complete: rows_read={result['rows_read']} rows_written={result['rows_written']} write_to_db={write_to_db}"
	)


@sql_app.command("run")
def sql_run(query: str = typer.Option(..., help="SQL statement to execute")) -> None:
	settings = get_settings()
	configure_logging(settings.log_level)
	engine = create_db_engine(settings)
	result = run_sql(engine, query)
	typer.echo(f"rows={result['row_count']} duration_ms={result['duration_ms']}")
	for row in result["rows"][:20]:
		typer.echo(str(row))


@sql_app.command("file")
def sql_file(path: str = typer.Option(..., help="Path to SQL file")) -> None:
	settings = get_settings()
	configure_logging(settings.log_level)
	sql_text = Path(path).read_text(encoding="utf-8")
	engine = create_db_engine(settings)
	result = run_sql(engine, sql_text)
	typer.echo(f"rows={result['row_count']} duration_ms={result['duration_ms']}")
	for row in result["rows"][:20]:
		typer.echo(str(row))


@sql_app.command("save")
def sql_save(
	name: str = typer.Option(..., help="Saved query name"),
	file: str = typer.Option(..., help="SQL file path"),
) -> None:
	settings = get_settings()
	configure_logging(settings.log_level)
	engine = create_db_engine(settings)
	sql_text = Path(file).read_text(encoding="utf-8")
	save_query(engine, name=name, sql_text=sql_text)
	typer.echo(f"Saved query: {name}")


@sql_app.command("history")
def sql_history(limit: int = typer.Option(20, help="Max history rows")) -> None:
	settings = get_settings()
	configure_logging(settings.log_level)
	engine = create_db_engine(settings)
	rows = get_query_history(engine, limit=limit)
	for row in rows:
		typer.echo(str(row))


@export_app.command("csv")
def export_csv(
	query_name: str = typer.Option(..., help="Saved query name"),
	out: str = typer.Option(..., help="Output CSV path"),
) -> None:
	settings = get_settings()
	configure_logging(settings.log_level)
	result = export_saved_query_to_csv(settings, query_name=query_name, out_path=out)
	typer.echo(
		f"CSV export complete: out_path={result['out_path']} row_count={result['row_count']} duration_ms={result['duration_ms']}"
	)


def main() -> None:
	app()


if __name__ == "__main__":
	main()
