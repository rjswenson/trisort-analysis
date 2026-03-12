from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from dateutil import parser as dt_parser

from app.config import Settings
from app.db import create_db_engine
from app.jira.client import JiraClient
from app.jira.endpoints import build_issue_search_jql
from app.jira.parsers import flatten_changelog_events, parse_issue_row, parse_worklogs
from app.sync.residency import derive_issue_project_residency
from app.sync.transforms import (
	complete_sync_run,
	create_sync_run,
	get_last_successful_watermark,
	get_max_issue_updated_at,
	insert_issue_events,
	replace_issue_project_residency,
	upsert_issues_current,
	upsert_worklogs,
)

logger = logging.getLogger(__name__)


def compute_updated_since(last_watermark: str | None, lookback_days: int, fallback_start_date: str) -> str:
	if not last_watermark:
		return fallback_start_date
	watermark_dt = dt_parser.parse(last_watermark)
	adjusted = watermark_dt - timedelta(days=lookback_days)
	return adjusted.isoformat()


def determine_watermark_out(issues_rows: list[dict[str, Any]], fallback: str) -> str:
	updated_values = [r.get("updated_at") for r in issues_rows if r.get("updated_at")]
	if not updated_values:
		return fallback
	return max(updated_values)


def run_incremental_sync(settings: Settings) -> dict[str, Any]:
	engine = create_db_engine(settings)
	last_watermark = get_last_successful_watermark(engine) or get_max_issue_updated_at(engine)
	updated_since = compute_updated_since(
		last_watermark=last_watermark,
		lookback_days=settings.sync_lookback_days,
		fallback_start_date=settings.jira_start_date,
	)
	run_id = create_sync_run(engine, mode="incremental", watermark_in=updated_since)

	rows_read = 0
	rows_written = 0
	try:
		with JiraClient(settings) as client:
			jql = build_issue_search_jql(
				settings.parsed_project_keys,
				settings.jira_start_date,
				settings.jira_end_date,
				updated_since=updated_since,
			)
			issues = client.search_issues(jql=jql, expand_changelog=True)

		rows_read = len(issues)
		issues_rows: list[dict[str, Any]] = []
		events_rows: list[dict[str, Any]] = []
		worklog_rows: list[dict[str, Any]] = []
		residency_rows_by_issue: dict[int, list[dict[str, Any]]] = {}

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

			wl_payload = client.get_issue_worklogs(issue.get("key", issue.get("id")))
			worklog_rows.extend(parse_worklogs(issue, wl_payload, run_id=run_id))

		rows_written += upsert_issues_current(engine, issues_rows)
		rows_written += insert_issue_events(engine, events_rows)
		rows_written += upsert_worklogs(engine, worklog_rows)
		for issue_id, residency_rows in residency_rows_by_issue.items():
			rows_written += replace_issue_project_residency(engine, issue_id, residency_rows)

		watermark_out = determine_watermark_out(issues_rows, fallback=last_watermark or updated_since)
		complete_sync_run(
			engine,
			run_id=run_id,
			status="success",
			rows_read=rows_read,
			rows_written=rows_written,
			watermark_out=watermark_out,
		)

		logger.info(
			"Incremental sync complete",
			extra={
				"rows_read": rows_read,
				"rows_written": rows_written,
				"watermark_in": updated_since,
				"watermark_out": watermark_out,
			},
		)
		return {
			"mode": "incremental",
			"rows_read": rows_read,
			"rows_written": rows_written,
			"run_id": run_id,
			"watermark_in": updated_since,
			"watermark_out": watermark_out,
		}
	except Exception as exc:
		complete_sync_run(
			engine,
			run_id=run_id,
			status="failed",
			rows_read=rows_read,
			rows_written=rows_written,
			error_message=str(exc),
		)
		raise
