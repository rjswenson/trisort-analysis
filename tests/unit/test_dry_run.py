import pytest

from app.config import Settings
from app.sync.full_sync import run_full_sync


def test_dry_run_does_not_initialize_db_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings(
        jira_base_url="https://unused.atlassian.net",
        jira_email="unused@example.com",
        jira_api_token="unused",
        jira_project_keys="EIT",
    )

    def fail_engine_creation(*args, **kwargs):
        raise AssertionError("DB engine should not be created for dry-run")

    monkeypatch.setattr("app.sync.full_sync.create_db_engine", fail_engine_creation)

    result = run_full_sync(settings, dry_run=True, mock_fixture_path="mocks")

    assert result["dry_run"] is True
    assert result["rows_written"] == 0
    assert result["rows_read"] >= 1
