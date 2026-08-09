"""Central configuration, loaded from environment.

Every service imports ``settings`` from here rather than reading ``os.environ``
directly, so the set of recognised variables stays visible in one place.
"""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache

from pydantic import AliasChoices, Field, PostgresDsn, RedisDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderMode(StrEnum):
    """Whether provider adapters reach the network.

    ``FAKE`` keeps every adapter fixture-backed, so the full pipeline runs with
    no token and no spend. Tests pin this regardless of the environment.
    """

    REAL = "real"
    FAKE = "fake"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- LLM proxy ----------------------------------------------------------
    llm_base_url: str = "https://api.openai.com/v1"
    # This project's .env predates propai and names the token LLM_AUTH_TOKEN
    # (with LLM_API_KEY as an older duplicate). Accept all three rather than
    # asking the environment to rename around us; first match wins.
    llm_api_token: str = Field(
        default="",
        validation_alias=AliasChoices(
            "llm_api_token", "llm_auth_token", "llm_api_key"
        ),
    )
    llm_model: str = "gpt-5.6-sol"
    llm_model_chat: str = ""
    llm_image_model: str = "gpt-image-2"
    llm_embedding_model: str = "text-embedding-3-small"

    provider_mode: ProviderMode = Field(
        default=ProviderMode.FAKE,
        validation_alias="propai_provider_mode",
    )

    # --- Infrastructure -----------------------------------------------------
    database_url: PostgresDsn
    redis_url: RedisDsn = Field(default="redis://redis:6379/0")

    # --- Security -----------------------------------------------------------
    secret_key: str = ""
    ip_hash_salt: str = ""
    access_token_ttl_minutes: int = 60 * 12

    # --- Public surface -----------------------------------------------------
    public_base_url: str = "http://localhost:8000"

    # --- WhatsApp -----------------------------------------------------------
    whatsapp_agency_number: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = ""

    # --- Embeddings ---------------------------------------------------------
    # pgvector columns are fixed-width, so this participates in the schema.
    # Changing it requires a migration AND a full re-embed: vectors from
    # different models are not comparable, so a dimension change is never
    # only a dimension change.
    embedding_dim: int = 1536

    @property
    def chat_model(self) -> str:
        """Cheaper tier for high-volume conversation, falling back to the main model."""
        return self.llm_model_chat or self.llm_model

    @property
    def is_fake(self) -> bool:
        return self.provider_mode is ProviderMode.FAKE

    @model_validator(mode="after")
    def _require_credentials_in_real_mode(self) -> Settings:
        """Fail fast at startup instead of at the first provider call."""
        if self.provider_mode is ProviderMode.REAL and not self.llm_api_token:
            raise ValueError(
                "PROPAI_PROVIDER_MODE=real requires LLM_API_TOKEN. "
                "Set the token, or use PROPAI_PROVIDER_MODE=fake to run offline."
            )
        return self

    @model_validator(mode="after")
    def _require_secrets_outside_fake(self) -> Settings:
        if self.provider_mode is ProviderMode.REAL:
            for name in ("secret_key", "ip_hash_salt"):
                if not getattr(self, name):
                    raise ValueError(f"{name.upper()} must be set when running for real")
        return self


@lru_cache
def get_settings() -> Settings:
    """Cached accessor. Call ``get_settings.cache_clear()`` in tests that patch env."""
    return Settings()  # type: ignore[call-arg]
