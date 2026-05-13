"""
Test configuration and shared fixtures.
"""

import pytest
from elite.config.settings import EliteSettings


@pytest.fixture
def settings():
    """Return a test settings instance (no .env loading)."""
    return EliteSettings(
        ollama_base_url="http://localhost:11434",
        model_name="test-model",
        llm_timeout=5,
        coder_max_retries=2,
        coder_timeout=5,
        search_max_results=3,
        log_level="DEBUG",
    )


@pytest.fixture
def router():
    """Return a Router instance."""
    from elite.core.router import Router
    return Router()
