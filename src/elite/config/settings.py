"""
elite.config.settings
Pydantic-based, env-driven configuration.

All settings are read from environment variables (prefixed ELITE_)
or from a .env file in the project root. No hardcoded secrets.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_dotenv() -> str:
    """Walk up from CWD to find the closest .env file."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        candidate = parent / ".env"
        if candidate.is_file():
            return str(candidate)
    return ".env"


class EliteSettings(BaseSettings):
    """
    Central configuration for the ELITE AI Agent.
    Every field maps to an ELITE_<FIELD_NAME> env var.
    """

    model_config = SettingsConfigDict(
        env_prefix="ELITE_",
        env_file=_find_dotenv(),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── LLM / Ollama ────────────────────────────────────────────────
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Base URL for the Ollama server",
    )
    model_name: str = Field(
        default="deepseek-r1:7b",
        description="Ollama model identifier",
    )
    llm_timeout: int = Field(
        default=120,
        description="Timeout in seconds for LLM requests",
    )

    # ── Flask ────────────────────────────────────────────────────────
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=5000)
    debug: bool = Field(default=False)
    secret_key: str = Field(default="change-me-to-a-random-secret")

    # ── Telegram ─────────────────────────────────────────────────────
    telegram_bot_token: str = Field(default="")
    telegram_chat_id: str = Field(default="")

    # ── Agent-specific ───────────────────────────────────────────────
    coder_max_retries: int = Field(default=10)
    coder_timeout: int = Field(default=30)
    coder_save_dir: str = Field(default="./generated_scripts")
    search_max_results: int = Field(default=5)

    # ── Logging ──────────────────────────────────────────────────────
    log_level: str = Field(default="INFO")
    log_format: str = Field(
        default="text",
        description="'text' for human-readable or 'json' for structured logs",
    )

    # ── Derived properties ───────────────────────────────────────────
    @property
    def ollama_generate_url(self) -> str:
        return f"{self.ollama_base_url.rstrip('/')}/api/generate"

    @property
    def telegram_configured(self) -> bool:
        return bool(self.telegram_bot_token and self.telegram_chat_id)

    @property
    def project_root(self) -> Path:
        """Return the root directory of the project (where pyproject.toml lives)."""
        current = Path.cwd()
        for parent in [current, *current.parents]:
            if (parent / "pyproject.toml").is_file():
                return parent
        return current


@lru_cache(maxsize=1)
def get_settings() -> EliteSettings:
    """Return a cached settings singleton."""
    return EliteSettings()
