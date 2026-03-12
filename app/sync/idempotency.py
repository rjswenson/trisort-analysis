from __future__ import annotations


def event_dedup_key(event: dict) -> tuple:
	return (
		event.get("issue_id"),
		event.get("source_changelog_id"),
		event.get("field_name"),
		event.get("to_value"),
		event.get("event_ts"),
	)
