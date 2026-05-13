"""
elite.agents — Agent subpackage.

Importing this module triggers registration of all agents
into the AgentRegistry.
"""

# Import all agents so they self-register via @AgentRegistry.register
from elite.agents import (
    coder,
    search,
    filesystem,
    system,
    screen,
    action,
)

__all__ = ["coder", "search", "filesystem", "system", "screen", "action"]
