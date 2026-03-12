from app.config import Settings


def test_project_keys_parsing_from_csv() -> None:
	settings = Settings(jira_project_keys="EIT, ABC , XYZ")
	assert settings.parsed_project_keys == ["EIT", "ABC", "XYZ"]


def test_missing_runtime_fields_detection() -> None:
	settings = Settings(
		jira_base_url="",
		jira_email="",
		jira_api_token="",
		jira_project_keys="",
	)
	missing = settings.missing_required_runtime_fields()
	assert "JIRA_BASE_URL" in missing
	assert "JIRA_EMAIL" in missing
	assert "JIRA_API_TOKEN" in missing
	assert "JIRA_PROJECT_KEYS" in missing
