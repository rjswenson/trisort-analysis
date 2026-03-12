CREATE TABLE IF NOT EXISTS sync_runs (
	run_id BIGSERIAL PRIMARY KEY,
	mode TEXT NOT NULL,
	started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	ended_at TIMESTAMPTZ,
	status TEXT NOT NULL,
	error_message TEXT,
	rows_read INTEGER NOT NULL DEFAULT 0,
	rows_written INTEGER NOT NULL DEFAULT 0,
	watermark_in TIMESTAMPTZ,
	watermark_out TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS issues_current (
	issue_id BIGINT PRIMARY KEY,
	issue_key TEXT NOT NULL,
	issue_number INTEGER,
	current_project_key TEXT,
	issue_type TEXT,
	summary TEXT,
	resolution TEXT,
	status TEXT,
	labels TEXT[] NOT NULL DEFAULT '{}',
	components TEXT[] NOT NULL DEFAULT '{}',
	created_at TIMESTAMPTZ,
	updated_at TIMESTAMPTZ,
	resolved_at TIMESTAMPTZ,
	custom_client_name TEXT,
	custom_client_secondary TEXT[] NOT NULL DEFAULT '{}',
	last_synced_run_id BIGINT REFERENCES sync_runs(run_id)
);

CREATE TABLE IF NOT EXISTS issue_events (
	event_id BIGSERIAL PRIMARY KEY,
	issue_id BIGINT NOT NULL,
	issue_key TEXT NOT NULL,
	event_ts TIMESTAMPTZ NOT NULL,
	event_type TEXT NOT NULL,
	field_name TEXT,
	from_value TEXT,
	to_value TEXT,
	from_project_key TEXT,
	to_project_key TEXT,
	author_account_id TEXT,
	source_changelog_id TEXT,
	run_id BIGINT REFERENCES sync_runs(run_id),
	UNIQUE (issue_id, source_changelog_id, field_name, to_value, event_ts)
);

CREATE TABLE IF NOT EXISTS worklogs (
	worklog_id BIGINT PRIMARY KEY,
	issue_id BIGINT NOT NULL,
	issue_key TEXT NOT NULL,
	author_account_id TEXT,
	started_at TIMESTAMPTZ,
	time_spent_seconds INTEGER NOT NULL DEFAULT 0,
	created_at TIMESTAMPTZ,
	updated_at TIMESTAMPTZ,
	run_id BIGINT REFERENCES sync_runs(run_id)
);

CREATE TABLE IF NOT EXISTS issue_project_residency (
	residency_id BIGSERIAL PRIMARY KEY,
	issue_id BIGINT NOT NULL,
	issue_key TEXT NOT NULL,
	project_key TEXT NOT NULL,
	entered_at TIMESTAMPTZ NOT NULL,
	exited_at TIMESTAMPTZ,
	duration_seconds BIGINT,
	sequence_num INTEGER NOT NULL,
	run_id BIGINT REFERENCES sync_runs(run_id)
);

CREATE TABLE IF NOT EXISTS query_saved (
	saved_query_id BIGSERIAL PRIMARY KEY,
	name TEXT NOT NULL UNIQUE,
	sql_text TEXT NOT NULL,
	tags TEXT[] NOT NULL DEFAULT '{}',
	created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS query_history (
	query_id BIGSERIAL PRIMARY KEY,
	query_name TEXT,
	sql_text TEXT NOT NULL,
	executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	duration_ms INTEGER,
	row_count INTEGER,
	success BOOLEAN NOT NULL,
	error_message TEXT
);
