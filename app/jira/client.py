from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import Settings
from app.jira.endpoints import (
	issue_changelog_url,
	issue_worklog_url,
	search_url,
)


class JiraClient:
	def __init__(self, settings: Settings, timeout: float = 30.0) -> None:
		self.settings = settings
		self._client = httpx.Client(
			auth=(settings.jira_email, settings.jira_api_token),
			headers={"Accept": "application/json"},
			timeout=timeout,
		)

	def close(self) -> None:
		self._client.close()

	def __enter__(self) -> "JiraClient":
		return self

	def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
		self.close()

	@retry(
		retry=retry_if_exception_type(httpx.HTTPStatusError),
		wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
		stop=stop_after_attempt(3),
		reraise=True,
	)
	def _request(self, method: str, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
		response = self._client.request(method, url, params=params)
		if response.status_code in {429, 500, 502, 503, 504}:
			response.raise_for_status()
		if response.status_code >= 400:
			# Do not retry client-side auth/permission/data errors.
			raise RuntimeError(f"Jira API request failed ({response.status_code}): {response.text}")
		return response.json()

	def search_issues(
		self,
		jql: str,
		fields: list[str] | None = None,
		expand_changelog: bool = True,
		page_size: int = 100,
	) -> list[dict[str, Any]]:
		start_at = 0
		results: list[dict[str, Any]] = []
		url = search_url(self.settings.jira_base_url)
		expand = "changelog" if expand_changelog else None

		while True:
			params: dict[str, Any] = {
				"jql": jql,
				"startAt": start_at,
				"maxResults": page_size,
			}
			if fields:
				params["fields"] = ",".join(fields)
			if expand:
				params["expand"] = expand

			payload = self._request("GET", url, params=params)
			issues = payload.get("issues", [])
			results.extend(issues)

			total = int(payload.get("total", 0))
			start_at += len(issues)
			if start_at >= total or not issues:
				break

		return results

	def get_issue_worklogs(self, issue_id_or_key: str) -> list[dict[str, Any]]:
		url = issue_worklog_url(self.settings.jira_base_url, issue_id_or_key)
		payload = self._request("GET", url)
		return payload.get("worklogs", [])

	def get_issue_changelog(self, issue_id_or_key: str) -> list[dict[str, Any]]:
		url = issue_changelog_url(self.settings.jira_base_url, issue_id_or_key)
		payload = self._request("GET", url)
		return payload.get("values", [])
