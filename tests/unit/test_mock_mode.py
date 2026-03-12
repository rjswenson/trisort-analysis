from app.config import Settings
from app.sync.orchestrator import run_sync_mock


def test_mock_mode_dry_run_reads_fixture_data() -> None:
    settings = Settings(
        jira_base_url="https://unused.atlassian.net",
        jira_email="unused@example.com",
        jira_api_token="unused",
        jira_project_keys="EIT",
    )

    result = run_sync_mock(settings, fixture_path="mocks", write_to_db=False)

    assert result["mock_mode"] is True
    assert result["dry_run"] is True
    assert result["rows_read"] >= 1
    assert result["rows_written"] == 0
