"""
elite.core.registry
Self-registering agent plugin system.
Agents register themselves at import time, and the router
looks them up by name from this global registry.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from elite.agents.base import BaseAgent

logger = logging.getLogger(__name__)

# ── Global registry ───────────────────────────────────────────────────
_agents: dict[str, type[BaseAgent]] = {}


class AgentRegistry:
    """
    Central registry for all agent classes.

    Usage:
        @AgentRegistry.register("coder")
        class CoderAgent(BaseAgent):
            ...
    """

    @staticmethod
    def register(name: str):
        """Class decorator that registers an agent under `name`."""
        def decorator(cls):
            if name in _agents:
                logger.warning(
                    "Agent '%s' is being re-registered (was %s, now %s)",
                    name, _agents[name].__name__, cls.__name__,
                )
            _agents[name] = cls
            logger.debug("Registered agent: %s → %s", name, cls.__name__)
            return cls
        return decorator

    @staticmethod
    def get(name: str) -> type[BaseAgent] | None:
        """Retrieve a registered agent class by name."""
        return _agents.get(name)

    @staticmethod
    def get_instance(name: str) -> BaseAgent | None:
        """Instantiate and return an agent by name."""
        cls = _agents.get(name)
        if cls is None:
            return None
        return cls()

    @staticmethod
    def list_agents() -> dict[str, type[BaseAgent]]:
        """Return a copy of the full registry."""
        return dict(_agents)

    @staticmethod
    def names() -> list[str]:
        """Return all registered agent names."""
        return list(_agents.keys())
