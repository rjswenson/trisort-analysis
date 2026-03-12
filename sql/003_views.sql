CREATE OR REPLACE VIEW v_eit_intervals AS
SELECT
	issue_id,
	issue_key,
	entered_at,
	exited_at,
	duration_seconds,
	sequence_num
FROM issue_project_residency
WHERE project_key = 'EIT';

CREATE OR REPLACE VIEW v_eit_first_entry_to_first_exit AS
WITH eit_ranked AS (
	SELECT
		issue_id,
		issue_key,
		entered_at,
		exited_at,
		ROW_NUMBER() OVER (PARTITION BY issue_id ORDER BY entered_at ASC) AS rn
	FROM issue_project_residency
	WHERE project_key = 'EIT'
)
SELECT
	issue_id,
	issue_key,
	entered_at AS first_eit_entered_at,
	exited_at AS first_eit_exited_at,
	EXTRACT(EPOCH FROM (exited_at - entered_at))::BIGINT AS first_eit_duration_seconds
FROM eit_ranked
WHERE rn = 1
  AND exited_at IS NOT NULL;

CREATE OR REPLACE VIEW v_issue_project_moves AS
SELECT
	issue_id,
	issue_key,
	event_ts,
	from_project_key,
	to_project_key,
	author_account_id
FROM issue_events
WHERE event_type = 'project_moved';
