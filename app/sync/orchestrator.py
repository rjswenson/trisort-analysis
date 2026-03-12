from __future__ import annotations

from app.config import Settings
from app.sync.full_sync import run_full_sync
from app.sync.incremental_sync import run_incremental_sync


def run_sync_full(settings: Settings) -> dict:
	return run_full_sync(settings=settings, dry_run=False, mock_fixture_path=None)


def run_sync_dry_run(settings: Settings) -> dict:
	return run_full_sync(settings=settings, dry_run=True, mock_fixture_path=None)


def run_sync_mock(settings: Settings, fixture_path: str | None = None, write_to_db: bool = False) -> dict:
	return run_full_sync(settings=settings, dry_run=not write_to_db, mock_fixture_path=fixture_path)


def run_sync_incremental(settings: Settings) -> dict:
	return run_incremental_sync(settings)
