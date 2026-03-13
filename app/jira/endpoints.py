from urllib.parse import quote


def search_url(base_url: str) -> str:
	return f"{base_url.rstrip('/')}/rest/api/3/search/jql"


def issue_url(base_url: str, issue_id_or_key: str) -> str:
	encoded = quote(issue_id_or_key, safe="")
	return f"{base_url.rstrip('/')}/rest/api/3/issue/{encoded}"


def issue_worklog_url(base_url: str, issue_id_or_key: str) -> str:
	return f"{issue_url(base_url, issue_id_or_key)}/worklog"


def issue_changelog_url(base_url: str, issue_id_or_key: str) -> str:
	return f"{issue_url(base_url, issue_id_or_key)}/changelog"


def build_issue_search_jql(
	project_keys: list[str],
	start_date: str,
	end_date: str,
	updated_since: str | None = None,
) -> str:
	projects = ",".join(project_keys)
	base = (
		f"project in ({projects}) "
		f"AND created >= \"{start_date}\" "
		f"AND created <= \"{end_date}\""
	)
	if updated_since:
		return f"{base} AND updated >= \"{updated_since}\""
	return base
