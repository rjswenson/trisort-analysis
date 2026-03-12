import typer

from app.config import get_settings
from app.db import check_db_connection, create_db_engine
from app.logging import configure_logging
from app.sync.orchestrator import run_sync_dry_run, run_sync_full, run_sync_mock

app = typer.Typer(help="Trisort local Jira sync and analysis CLI")
sync_app = typer.Typer(help="Synchronization commands")
app.add_typer(sync_app, name="sync")


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
	typer.echo("Sync incremental is not implemented yet (Milestone B).")


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


def main() -> None:
	app()


if __name__ == "__main__":
	main()
