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
