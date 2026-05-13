"""
elite.core.exceptions
Typed exception hierarchy for the entire application.
Every layer catches/raises these — no raw Exception leaks.
"""


class EliteError(Exception):
    """Base exception for all ELITE errors."""

    def __init__(self, message: str, *, detail: str | None = None):
        self.detail = detail
        super().__init__(message)


class LLMError(EliteError):
    """Raised when the LLM backend (Ollama) fails."""
    pass


class AgentError(EliteError):
    """Raised when an agent fails to process a command."""

    def __init__(self, message: str, *, agent_name: str = "unknown", **kwargs):
        self.agent_name = agent_name
        super().__init__(message, **kwargs)


class RouterError(EliteError):
    """Raised when intent classification / routing fails."""
    pass


class ConfigError(EliteError):
    """Raised when configuration is invalid or missing."""
    pass


class IntegrationError(EliteError):
    """Raised when an external integration (Telegram, etc.) fails."""
    pass
