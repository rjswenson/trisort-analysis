from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from app.config import Settings
from app.db import create_db_engine
from app.jira.client import JiraClient
from app.jira.endpoints import build_issue_search_jql
from app.jira.parsers import flatten_changelog_events, parse_issue_row, parse_worklogs
from app.sync.residency import derive_issue_project_residency
from app.sync.transforms import (
	complete_sync_run,
	create_sync_run,
	insert_issue_events,
	replace_issue_project_residency,
	upsert_issues_current,
	upsert_worklogs,
)

logger = logging.getLogger(__name__)


def _load_mock_payloads(mock_fixture_path: str | None) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
	base = Path(mock_fixture_path) if mock_fixture_path else Path("mocks")
	issues = json.loads((base / "jira_search_page_1.json").read_text(encoding="utf-8")).get("issues", [])
	changelog = json.loads((base / "jira_changelog_issue_example.json").read_text(encoding="utf-8"))
	worklog = json.loads((base / "jira_worklog_issue_example.json").read_text(encoding="utf-8"))
	return issues, changelog, worklog


def run_full_sync(settings: Settings, dry_run: bool = False, mock_fixture_path: str | None = None) -> dict[str, Any]:
	if mock_fixture_path:
		issues, mock_changelog_payload, mock_worklog_payload = _load_mock_payloads(mock_fixture_path)
	else:
		with JiraClient(settings) as client:
			jql = build_issue_search_jql(
				settings.parsed_project_keys,
				settings.jira_start_date,
				settings.jira_end_date,
			)
			issues = client.search_issues(jql=jql, expand_changelog=True)
			mock_changelog_payload = {}
			mock_worklog_payload = {}

	rows_read = len(issues)
	issues_rows: list[dict[str, Any]] = []
	events_rows: list[dict[str, Any]] = []
	worklog_rows: list[dict[str, Any]] = []
	residency_rows_by_issue: dict[int, list[dict[str, Any]]] = {}

	run_id: int | None = None
	if not dry_run:
		engine = create_db_engine(settings)
		run_id = create_sync_run(engine, mode="full")
	else:
		engine = None

	try:
		if mock_fixture_path:
			for issue in issues:
				issue["changelog"] = mock_changelog_payload.get("changelog", {"histories": []})

		for issue in issues:
			issue_row = parse_issue_row(issue, run_id=run_id)
			issues_rows.append(issue_row)

			issue_events = flatten_changelog_events(issue, run_id=run_id)
			events_rows.extend(issue_events)

			issue_id = int(issue["id"])
			issue_key = issue.get("key", "")
			residency_rows_by_issue[issue_id] = derive_issue_project_residency(
				issue_id=issue_id,
				issue_key=issue_key,
				events=issue_events,
				run_id=run_id,
			)

			if mock_fixture_path:
				wl_payload = mock_worklog_payload.get("worklogs", [])
			else:
				with JiraClient(settings) as client:
					wl_payload = client.get_issue_worklogs(issue.get("key", issue.get("id")))
			worklog_rows.extend(parse_worklogs(issue, wl_payload, run_id=run_id))

		rows_written = 0
		if not dry_run and engine is not None and run_id is not None:
			rows_written += upsert_issues_current(engine, issues_rows)
			rows_written += insert_issue_events(engine, events_rows)
			rows_written += upsert_worklogs(engine, worklog_rows)
			for issue_id, residency_rows in residency_rows_by_issue.items():
				rows_written += replace_issue_project_residency(engine, issue_id, residency_rows)
			complete_sync_run(
				engine,
				run_id=run_id,
				status="success",
				rows_read=rows_read,
				rows_written=rows_written,
			)
		else:
			rows_written = 0

		logger.info(
			"Full sync complete",
			extra={
				"rows_read": rows_read,
				"rows_written": rows_written,
				"dry_run": dry_run,
				"mock_mode": bool(mock_fixture_path),
			},
		)
		return {
			"mode": "full",
			"dry_run": dry_run,
			"mock_mode": bool(mock_fixture_path),
			"rows_read": rows_read,
			"rows_written": rows_written,
			"run_id": run_id,
		}
	except Exception as exc:
		if not dry_run and engine is not None and run_id is not None:
			complete_sync_run(
				engine,
				run_id=run_id,
				status="failed",
				rows_read=rows_read,
				rows_written=0,
				error_message=str(exc),
			)
		raise
