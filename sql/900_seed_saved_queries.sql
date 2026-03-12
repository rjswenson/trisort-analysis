INSERT INTO query_saved (name, sql_text, tags)
VALUES
(
	'avg_eit_to_first_triage_out_by_window',
	'SELECT AVG(first_eit_duration_seconds) AS avg_seconds FROM v_eit_first_entry_to_first_exit WHERE first_eit_entered_at >= :start_ts AND first_eit_entered_at < :end_ts;',
	ARRAY['eit', 'timing', 'mvp']
),
(
	'eit_bounce_back_count_per_issue',
	'SELECT issue_id, issue_key, COUNT(*) AS eit_entries FROM issue_project_residency WHERE project_key = ''EIT'' GROUP BY issue_id, issue_key ORDER BY eit_entries DESC;',
	ARRAY['eit', 'movement']
)
ON CONFLICT (name) DO NOTHING;
