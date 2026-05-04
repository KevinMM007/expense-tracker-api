from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Expense Tracker API"
    app_env: str = "development"
    debug: bool = False

    database_url: str = "postgresql+psycopg://expense:expense@localhost:5432/expense_tracker"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    cors_origins: str = "*"

    @field_validator("database_url", mode="before")
    @classmethod
    def _coerce_postgres_driver(cls, value: str) -> str:
        """Render (and Heroku) hand out URLs like ``postgres://`` or ``postgresql://``.

        SQLAlchemy with psycopg 3 needs the explicit ``postgresql+psycopg://`` driver,
        so normalise the prefix here instead of forcing the operator to remember.
        """
        if not isinstance(value, str):
            return value
        if value.startswith("postgres://"):
            value = "postgresql://" + value[len("postgres://") :]
        if value.startswith("postgresql://"):
            value = "postgresql+psycopg://" + value[len("postgresql://") :]
        return value

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
