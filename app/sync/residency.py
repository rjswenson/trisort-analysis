from __future__ import annotations

from typing import Any

from dateutil import parser as dt_parser


def _duration_seconds(start_ts: str, end_ts: str) -> int:
	return int((dt_parser.parse(end_ts) - dt_parser.parse(start_ts)).total_seconds())


def derive_issue_project_residency(
	issue_id: int,
	issue_key: str,
	events: list[dict[str, Any]],
	run_id: int | None = None,
) -> list[dict[str, Any]]:
	if not events:
		return []

	ordered = sorted(
		[e for e in events if e.get("event_ts")],
		key=lambda e: (e.get("event_ts"), 0 if e.get("event_type") == "created" else 1),
	)
	if not ordered:
		return []

	created = next((e for e in ordered if e.get("event_type") == "created"), None)
	project_moves = [e for e in ordered if e.get("event_type") == "project_moved"]

	initial_project = None
	if created:
		initial_project = created.get("to_project_key")
	if not initial_project:
		first_move = next((m for m in project_moves if m.get("from_project_key")), None)
		if first_move:
			initial_project = first_move.get("from_project_key")

	if not initial_project and project_moves:
		initial_project = project_moves[0].get("to_project_key")

	if not initial_project:
		return []

	entered_at = created.get("event_ts") if created else ordered[0].get("event_ts")
	if not entered_at:
		return []

	current_project = initial_project
	sequence_num = 1
	rows: list[dict[str, Any]] = []

	for move in project_moves:
		moved_at = move.get("event_ts")
		to_project = move.get("to_project_key")
		if not moved_at or not to_project:
			continue
		if to_project == current_project:
			continue

		rows.append(
			{
				"issue_id": issue_id,
				"issue_key": issue_key,
				"project_key": current_project,
				"entered_at": entered_at,
				"exited_at": moved_at,
				"duration_seconds": _duration_seconds(entered_at, moved_at),
				"sequence_num": sequence_num,
				"run_id": run_id,
			}
		)

		sequence_num += 1
		current_project = to_project
		entered_at = moved_at

	rows.append(
		{
			"issue_id": issue_id,
			"issue_key": issue_key,
			"project_key": current_project,
			"entered_at": entered_at,
			"exited_at": None,
			"duration_seconds": None,
			"sequence_num": sequence_num,
			"run_id": run_id,
		}
	)
	return rows
