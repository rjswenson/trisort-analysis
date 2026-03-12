from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

	jira_base_url: str = Field(default="")
	jira_email: str = Field(default="")
	jira_api_token: str = Field(default="")
	jira_project_keys: str = Field(default="")
	jira_eit_project_key: str = Field(default="EIT")
	jira_start_date: str = Field(default="2024-01-01")
	jira_end_date: str = Field(default="2026-12-31")
	sync_lookback_days: int = Field(default=7)

	database_url: str = Field(default="postgresql+psycopg://postgres:postgres@postgres:5432/trisort")
	log_level: str = Field(default="INFO")

	@field_validator("jira_project_keys", mode="before")
	@classmethod
	def parse_project_keys(cls, value: object) -> str:
		if value is None:
			return ""
		if isinstance(value, str):
			return value
		if isinstance(value, list):
			return ",".join([str(v).strip() for v in value if str(v).strip()])
		raise ValueError("jira_project_keys must be a comma-separated string or list-like value")

	@property
	def parsed_project_keys(self) -> list[str]:
		return [v.strip() for v in self.jira_project_keys.split(",") if v.strip()]

	def missing_required_runtime_fields(self) -> list[str]:
		missing = []
		if not self.jira_base_url:
			missing.append("JIRA_BASE_URL")
		if not self.jira_email:
			missing.append("JIRA_EMAIL")
		if not self.jira_api_token:
			missing.append("JIRA_API_TOKEN")
		if not self.parsed_project_keys:
			missing.append("JIRA_PROJECT_KEYS")
		return missing


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	return Settings()
