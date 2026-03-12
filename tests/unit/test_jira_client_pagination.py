import respx
from httpx import Response

from app.config import Settings
from app.jira.client import JiraClient


def test_search_issues_paginates_until_total() -> None:
    settings = Settings(
        jira_base_url="https://example.atlassian.net",
        jira_email="u@example.com",
        jira_api_token="token",
        jira_project_keys="EIT",
    )

    with respx.mock(assert_all_called=True) as router:
        router.get("https://example.atlassian.net/rest/api/3/search").mock(
            side_effect=[
                Response(200, json={"total": 2, "issues": [{"id": "1", "key": "EIT-1"}]}),
                Response(200, json={"total": 2, "issues": [{"id": "2", "key": "EIT-2"}]}),
            ]
        )

        with JiraClient(settings) as client:
            issues = client.search_issues(jql="project=EIT", page_size=1)

    assert len(issues) == 2
    assert issues[0]["key"] == "EIT-1"
    assert issues[1]["key"] == "EIT-2"
