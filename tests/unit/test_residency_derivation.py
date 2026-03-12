from app.sync.residency import derive_issue_project_residency


def test_single_exit_from_eit_creates_closed_and_open_intervals() -> None:
	events = [
		{
			"event_type": "created",
			"event_ts": "2026-03-01T10:00:00+00:00",
			"to_project_key": "EIT",
		},
		{
			"event_type": "project_moved",
			"event_ts": "2026-03-02T10:00:00+00:00",
			"from_project_key": "EIT",
			"to_project_key": "ABC",
		},
	]
	rows = derive_issue_project_residency(issue_id=1, issue_key="EIT-1", events=events, run_id=10)

	assert len(rows) == 2
	assert rows[0]["project_key"] == "EIT"
	assert rows[0]["duration_seconds"] == 86400
	assert rows[1]["project_key"] == "ABC"
	assert rows[1]["exited_at"] is None


def test_bounce_back_sequence_counts_multiple_eit_entries() -> None:
	events = [
		{
			"event_type": "created",
			"event_ts": "2026-03-01T00:00:00+00:00",
			"to_project_key": "EIT",
		},
		{
			"event_type": "project_moved",
			"event_ts": "2026-03-02T00:00:00+00:00",
			"from_project_key": "EIT",
			"to_project_key": "ABC",
		},
		{
			"event_type": "project_moved",
			"event_ts": "2026-03-03T00:00:00+00:00",
			"from_project_key": "ABC",
			"to_project_key": "EIT",
		},
		{
			"event_type": "project_moved",
			"event_ts": "2026-03-04T00:00:00+00:00",
			"from_project_key": "EIT",
			"to_project_key": "XYZ",
		},
	]
	rows = derive_issue_project_residency(issue_id=1, issue_key="EIT-1", events=events, run_id=11)

	eit_rows = [r for r in rows if r["project_key"] == "EIT"]
	assert len(eit_rows) == 2
	assert rows[-1]["project_key"] == "XYZ"
	assert rows[-1]["exited_at"] is None


def test_missing_created_uses_first_project_move_from_value() -> None:
	events = [
		{
			"event_type": "project_moved",
			"event_ts": "2026-03-02T00:00:00+00:00",
			"from_project_key": "EIT",
			"to_project_key": "ABC",
		}
	]
	rows = derive_issue_project_residency(issue_id=7, issue_key="EIT-7", events=events, run_id=12)

	assert len(rows) == 2
	assert rows[0]["project_key"] == "EIT"
	assert rows[0]["duration_seconds"] == 0
	assert rows[1]["project_key"] == "ABC"
