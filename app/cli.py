import typer

from app.config import get_settings
from app.db import check_db_connection, create_db_engine
from app.logging import configure_logging

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
	typer.echo("Sync full is not implemented yet (Milestone B).")


@sync_app.command("incremental")
def sync_incremental() -> None:
	typer.echo("Sync incremental is not implemented yet (Milestone B).")


@sync_app.command("dry-run")
def sync_dry_run() -> None:
	typer.echo("Sync dry-run is not implemented yet (Milestone B).")


def main() -> None:
	app()


if __name__ == "__main__":
	main()
