CREATE INDEX IF NOT EXISTS idx_issue_events_issue_ts
	ON issue_events (issue_id, event_ts);

CREATE INDEX IF NOT EXISTS idx_issue_events_field_ts
	ON issue_events (field_name, event_ts);

CREATE INDEX IF NOT EXISTS idx_residency_project_enter_exit
	ON issue_project_residency (project_key, entered_at, exited_at);

CREATE INDEX IF NOT EXISTS idx_issues_current_project_updated
	ON issues_current (current_project_key, updated_at);

CREATE INDEX IF NOT EXISTS idx_worklogs_issue_started
	ON worklogs (issue_id, started_at);

CREATE INDEX IF NOT EXISTS idx_issues_current_labels_gin
	ON issues_current USING GIN (labels);

CREATE INDEX IF NOT EXISTS idx_issues_current_components_gin
	ON issues_current USING GIN (components);
