from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine


def create_sync_run(engine: Engine, mode: str, watermark_in: str | None = None) -> int:
	query = text(
		"""
		INSERT INTO sync_runs (mode, status, watermark_in)
		VALUES (:mode, 'running', :watermark_in)
		RETURNING run_id
		"""
	)
	with engine.begin() as conn:
		return int(conn.execute(query, {"mode": mode, "watermark_in": watermark_in}).scalar_one())


def complete_sync_run(
	engine: Engine,
	run_id: int,
	status: str,
	rows_read: int,
	rows_written: int,
	error_message: str | None = None,
	watermark_out: str | None = None,
) -> None:
	query = text(
		"""
		UPDATE sync_runs
		SET ended_at = NOW(),
			status = :status,
			rows_read = :rows_read,
			rows_written = :rows_written,
			error_message = :error_message,
			watermark_out = :watermark_out
		WHERE run_id = :run_id
		"""
	)
	with engine.begin() as conn:
		conn.execute(
			query,
			{
				"run_id": run_id,
				"status": status,
				"rows_read": rows_read,
				"rows_written": rows_written,
				"error_message": error_message,
				"watermark_out": watermark_out,
			},
		)


def upsert_issues_current(engine: Engine, rows: list[dict[str, Any]]) -> int:
	if not rows:
		return 0
	query = text(
		"""
		INSERT INTO issues_current (
			issue_id, issue_key, issue_number, current_project_key, issue_type,
			summary, resolution, status, labels, components,
			created_at, updated_at, resolved_at,
			custom_client_name, custom_client_secondary, last_synced_run_id
		) VALUES (
			:issue_id, :issue_key, :issue_number, :current_project_key, :issue_type,
			:summary, :resolution, :status, :labels, :components,
			:created_at, :updated_at, :resolved_at,
			:custom_client_name, :custom_client_secondary, :last_synced_run_id
		)
		ON CONFLICT (issue_id)
		DO UPDATE SET
			issue_key = EXCLUDED.issue_key,
			issue_number = EXCLUDED.issue_number,
			current_project_key = EXCLUDED.current_project_key,
			issue_type = EXCLUDED.issue_type,
			summary = EXCLUDED.summary,
			resolution = EXCLUDED.resolution,
			status = EXCLUDED.status,
			labels = EXCLUDED.labels,
			components = EXCLUDED.components,
			created_at = EXCLUDED.created_at,
			updated_at = EXCLUDED.updated_at,
			resolved_at = EXCLUDED.resolved_at,
			custom_client_name = EXCLUDED.custom_client_name,
			custom_client_secondary = EXCLUDED.custom_client_secondary,
			last_synced_run_id = EXCLUDED.last_synced_run_id
		"""
	)
	with engine.begin() as conn:
		conn.execute(query, rows)
	return len(rows)


def insert_issue_events(engine: Engine, rows: list[dict[str, Any]]) -> int:
	if not rows:
		return 0
	query = text(
		"""
		INSERT INTO issue_events (
			issue_id, issue_key, event_ts, event_type, field_name,
			from_value, to_value, from_project_key, to_project_key,
			author_account_id, source_changelog_id, run_id
		) VALUES (
			:issue_id, :issue_key, :event_ts, :event_type, :field_name,
			:from_value, :to_value, :from_project_key, :to_project_key,
			:author_account_id, :source_changelog_id, :run_id
		)
		ON CONFLICT (issue_id, source_changelog_id, field_name, to_value, event_ts)
		DO NOTHING
		"""
	)
	with engine.begin() as conn:
		conn.execute(query, rows)
	return len(rows)


def upsert_worklogs(engine: Engine, rows: list[dict[str, Any]]) -> int:
	if not rows:
		return 0
	query = text(
		"""
		INSERT INTO worklogs (
			worklog_id, issue_id, issue_key, author_account_id,
			started_at, time_spent_seconds, created_at, updated_at, run_id
		) VALUES (
			:worklog_id, :issue_id, :issue_key, :author_account_id,
			:started_at, :time_spent_seconds, :created_at, :updated_at, :run_id
		)
		ON CONFLICT (worklog_id)
		DO UPDATE SET
			issue_id = EXCLUDED.issue_id,
			issue_key = EXCLUDED.issue_key,
			author_account_id = EXCLUDED.author_account_id,
			started_at = EXCLUDED.started_at,
			time_spent_seconds = EXCLUDED.time_spent_seconds,
			created_at = EXCLUDED.created_at,
			updated_at = EXCLUDED.updated_at,
			run_id = EXCLUDED.run_id
		"""
	)
	with engine.begin() as conn:
		conn.execute(query, rows)
	return len(rows)
