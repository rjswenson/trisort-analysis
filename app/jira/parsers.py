from __future__ import annotations

from typing import Any

from dateutil import parser as dt_parser


def _parse_ts(value: str | None) -> str | None:
	if not value:
		return None
	return dt_parser.parse(value).isoformat()


def parse_issue_row(issue: dict[str, Any], run_id: int | None = None) -> dict[str, Any]:
	fields = issue.get("fields", {})
	issue_key = issue.get("key", "")
	issue_number = None
	if "-" in issue_key:
		suffix = issue_key.split("-")[-1]
		issue_number = int(suffix) if suffix.isdigit() else None

	components = [c.get("name") for c in fields.get("components", []) if c.get("name")]

	return {
		"issue_id": int(issue["id"]),
		"issue_key": issue_key,
		"issue_number": issue_number,
		"current_project_key": (fields.get("project") or {}).get("key"),
		"issue_type": (fields.get("issuetype") or {}).get("name"),
		"summary": fields.get("summary"),
		"resolution": (fields.get("resolution") or {}).get("name"),
		"status": (fields.get("status") or {}).get("name"),
		"labels": fields.get("labels", []) or [],
		"components": components,
		"created_at": _parse_ts(fields.get("created")),
		"updated_at": _parse_ts(fields.get("updated")),
		"resolved_at": _parse_ts(fields.get("resolutiondate")),
		"custom_client_name": fields.get("Elastic Client Name[Dropdown]"),
		"custom_client_secondary": fields.get("Elastic Client(s): Secondary[Select List (multiple choices)]")
		or [],
		"last_synced_run_id": run_id,
	}


def flatten_changelog_events(issue: dict[str, Any], run_id: int | None = None) -> list[dict[str, Any]]:
	issue_id = int(issue["id"])
	issue_key = issue.get("key", "")
	fields = issue.get("fields", {})
	created_at = _parse_ts(fields.get("created"))
	events: list[dict[str, Any]] = []

	if created_at:
		events.append(
			{
				"issue_id": issue_id,
				"issue_key": issue_key,
				"event_ts": created_at,
				"event_type": "created",
				"field_name": None,
				"from_value": None,
				"to_value": None,
				"from_project_key": None,
				"to_project_key": (fields.get("project") or {}).get("key"),
				"author_account_id": None,
				"source_changelog_id": "created",
				"run_id": run_id,
			}
		)

	histories = (issue.get("changelog") or {}).get("histories", [])
	for history in histories:
		history_id = str(history.get("id", ""))
		event_ts = _parse_ts(history.get("created"))
		author_id = ((history.get("author") or {}).get("accountId"))
		for item in history.get("items", []):
			field_name = item.get("field")
			from_val = item.get("fromString")
			to_val = item.get("toString")
			event_type = "field_changed"
			from_project_key = None
			to_project_key = None
			if field_name == "project":
				event_type = "project_moved"
				from_project_key = from_val
				to_project_key = to_val
			elif field_name == "status":
				event_type = "status_changed"
			elif field_name == "resolution":
				event_type = "resolution_changed"
			elif field_name == "labels":
				event_type = "label_changed"
			elif field_name == "Component" or field_name == "components":
				event_type = "component_changed"

			events.append(
				{
					"issue_id": issue_id,
					"issue_key": issue_key,
					"event_ts": event_ts,
					"event_type": event_type,
					"field_name": field_name,
					"from_value": from_val,
					"to_value": to_val,
					"from_project_key": from_project_key,
					"to_project_key": to_project_key,
					"author_account_id": author_id,
					"source_changelog_id": history_id,
					"run_id": run_id,
				}
			)

	return events


def parse_worklogs(issue: dict[str, Any], worklogs: list[dict[str, Any]], run_id: int | None = None) -> list[dict[str, Any]]:
	issue_id = int(issue["id"])
	issue_key = issue.get("key", "")
	rows: list[dict[str, Any]] = []
	for wl in worklogs:
		rows.append(
			{
				"worklog_id": int(wl["id"]),
				"issue_id": issue_id,
				"issue_key": issue_key,
				"author_account_id": ((wl.get("author") or {}).get("accountId")),
				"started_at": _parse_ts(wl.get("started")),
				"time_spent_seconds": int(wl.get("timeSpentSeconds", 0)),
				"created_at": _parse_ts(wl.get("created")),
				"updated_at": _parse_ts(wl.get("updated")),
				"run_id": run_id,
			}
		)
	return rows
