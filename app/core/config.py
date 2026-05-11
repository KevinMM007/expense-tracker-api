"""Application settings.

Single source of truth for runtime configuration. The values can come from
three layers, in order of priority:

1. AWS Secrets Manager — when ``db_credentials_secret_arn`` is set, the
   master DB credentials are pulled at startup and ``database_url`` is
   rebuilt from them. Used by the AWS Lambda deployment so the password
   never lives in environment variables or container layers.
2. Process environment variables (e.g. ``DATABASE_URL`` on Render).
3. ``.env`` file in the project root (local development).
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ---- Application ----
    app_name: str = "Expense Tracker API"
    app_env: str = "development"
    debug: bool = False

    # ---- Database ----
    database_url: str = "postgresql+psycopg://expense:expense@localhost:5432/expense_tracker"

    # When set (e.g. on AWS Lambda) the app fetches the master credentials
    # JSON from this Secrets Manager ARN at startup and overwrites
    # ``database_url`` with the resulting connection string.
    db_credentials_secret_arn: str | None = None

    # Region for the boto3 Secrets Manager client. Only consulted when
    # ``db_credentials_secret_arn`` is set.
    aws_region: str = "us-east-2"

    # ---- JWT ----
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # ---- CORS ----
    cors_origins: str = "*"

    # ---- Validators ----

    @field_validator("database_url", mode="before")
    @classmethod
    def _coerce_postgres_driver(cls, value: str) -> str:
        """Normalise bare ``postgres://`` or ``postgresql://`` URLs (as Render
        and Heroku hand them out) to the explicit ``postgresql+psycopg://``
        driver string that SQLAlchemy with psycopg 3 requires.
        """
        if not isinstance(value, str):
            return value
        if value.startswith("postgres://"):
            value = "postgresql://" + value[len("postgres://") :]
        if value.startswith("postgresql://"):
            value = "postgresql+psycopg://" + value[len("postgresql://") :]
        return value

    @model_validator(mode="after")
    def _hydrate_db_url_from_secret(self) -> Settings:
        """If running on AWS with a Secrets Manager ARN configured, fetch the
        credentials and rebuild ``database_url``. No-op otherwise.
        """
        if not self.db_credentials_secret_arn:
            return self

        # Lazy import so the dependency is only required when actually used.
        import boto3  # type: ignore[import-untyped]

        client = boto3.client("secretsmanager", region_name=self.aws_region)
        response = client.get_secret_value(SecretId=self.db_credentials_secret_arn)
        creds: dict[str, Any] = json.loads(response["SecretString"])

        username = creds["username"]
        password = creds["password"]
        host = creds["host"]
        port = creds.get("port", 5432)
        dbname = creds["dbname"]

        # Build directly with the psycopg driver - skip the @field_validator.
        self.database_url = (
            f"postgresql+psycopg://{username}:{password}@{host}:{port}/{dbname}"
        )
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
