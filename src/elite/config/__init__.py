"""
elite.config — Configuration subpackage.

Exports the global Settings singleton for easy access:
    from elite.config import settings
"""

from elite.config.settings import get_settings

settings = get_settings()

__all__ = ["settings", "get_settings"]
