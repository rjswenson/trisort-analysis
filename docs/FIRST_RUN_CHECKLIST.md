# First Real Jira Full Sync Checklist

Use this checklist before the first production-like local run against Jira Cloud.

## Environment And Access

1. Confirm `.env` exists and all required values are set.
2. Verify `JIRA_BASE_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN` are valid.
3. Verify `JIRA_PROJECT_KEYS` includes EIT and target projects.
4. Confirm API token has access to issue, changelog, and worklog data.
5. Confirm local Postgres is reachable from the app container/session.

## Dry Validation

1. Run `python -m app.cli doctor`.
2. Run `python -m app.cli sync dry-run` and verify non-zero `rows_read`.
3. Review dry-run output for obvious field-mapping issues.
4. If dry-run fails, resolve auth/JQL/schema errors before continuing.

## Full Backfill Run

1. Ensure schema is applied (`make bootstrap-db` if needed).
2. Run `python -m app.cli sync full`.
3. Confirm command exits successfully.
4. Inspect `sync_runs` for `status = success` and expected `rows_read`.

## Post-Run Data Checks

1. Verify row counts in `issues_current`, `issue_events`, `worklogs`, and `issue_project_residency`.
2. Spot check 5-10 known issues for project movement and timestamps.
3. Validate at least one EIT move-out and one EIT bounce-back scenario.
4. Run a saved EIT metric query and confirm plausible output.

## Incremental And Repeatability

1. Run `python -m app.cli sync incremental` twice.
2. Confirm second run does not cause unexpected growth in deduped event rows.
3. Validate `watermark_in` and `watermark_out` progression in `sync_runs`.

## Operational Readiness

1. Keep a local backup/export of Postgres volume or DB before major schema changes.
2. Enable scheduled incremental sync only after one clean full sync and one clean incremental rerun.
3. Save baseline analysis queries in `query_saved` for repeatability.
