from app.config import Settings
from app.db import build_database_url


def test_build_database_url_uses_settings_value() -> None:
	db_url = "postgresql+psycopg://u:p@localhost:5432/x"
	settings = Settings(database_url=db_url)
	assert build_database_url(settings) == db_url
