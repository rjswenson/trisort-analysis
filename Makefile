.PHONY: up down logs test bootstrap-db doctor

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

test:
	docker compose run --rm app bash -lc "pip install --no-cache-dir -e .[dev] && pytest -q"

bootstrap-db:
	docker compose run --rm app bash -lc "chmod +x scripts/bootstrap_db.sh && ./scripts/bootstrap_db.sh"

doctor:
	docker compose run --rm app bash -lc "trisort doctor"
