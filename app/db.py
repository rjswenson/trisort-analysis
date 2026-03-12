from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.config import Settings


def build_database_url(settings: Settings) -> str:
	return settings.database_url


def create_db_engine(settings: Settings) -> Engine:
	return create_engine(build_database_url(settings), future=True, pool_pre_ping=True)


def check_db_connection(engine: Engine) -> None:
	with engine.connect() as conn:
		conn.execute(text("SELECT 1"))
