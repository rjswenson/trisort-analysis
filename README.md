# trisort-analysis

Local Jira Cloud to PostgreSQL sync toolkit for EIT lifecycle analysis.

## Quick Start

1. Copy env template:
	 - `cp .env.example .env`
2. Update Jira credentials and project keys in `.env`.
3. Start services (when Docker is enabled in WSL):
	 - `make up`
4. Bootstrap database schema:
	 - `make bootstrap-db`
5. Validate runtime configuration:
	 - `make doctor`

## Sync Commands

- Full sync:
	- `python -m app.cli sync full`
- Incremental sync:
	- `python -m app.cli sync incremental`
- Dry run (no DB writes):
	- `python -m app.cli sync dry-run`
- Mock mode:
	- `python -m app.cli sync mock --fixture-path mocks`

## SQL Commands

- Run direct SQL:
	- `python -m app.cli sql run --query "SELECT COUNT(*) FROM issues_current"`
- Run SQL from file:
	- `python -m app.cli sql file --path queries/my_query.sql`
- Save SQL file as named query:
	- `python -m app.cli sql save --name my_query --file queries/my_query.sql`
- Show query execution history:
	- `python -m app.cli sql history --limit 20`

## Export

- Export saved query to CSV:
	- `python -m app.cli export csv --query-name my_query --out exports/my_query.csv`

## Tests

- Run unit tests:
	- `pytest -q`

## Troubleshooting

1. Jira returns 401 or 403:
- Re-check `JIRA_EMAIL` and `JIRA_API_TOKEN`.
- Confirm token scope and Jira project permissions.
- Verify `JIRA_BASE_URL` uses your Jira Cloud tenant hostname.

2. Jira returns 429 (rate limit):
- Reduce run frequency and avoid concurrent sync runs.
- Narrow JQL date/project windows for large backfills.
- Retry after cool-down; the client already retries transient failures.

3. Sync fails with SQL errors:
- Re-apply schema using `make bootstrap-db`.
- Confirm app uses the intended `DATABASE_URL`.

4. Dry run succeeds but full sync fails:
- Confirm DB credentials and connectivity from the runtime context.
- Check `sync_runs.error_message` for first failing operation.

5. Running from host shell vs app container:
- Host-shell commands should use `DATABASE_URL` with `localhost`.
- Container-run commands should use Postgres service host `postgres`.
- Compose can override container DB URL separately from host `.env` values.

## First Run Checklist

- See [docs/FIRST_RUN_CHECKLIST.md](docs/FIRST_RUN_CHECKLIST.md) before the first real Jira full sync.
