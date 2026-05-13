"""
elite.agents.base
Abstract base class that all agents must implement.
Enforces a consistent interface and provides shared utilities.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """
    Abstract base for every ELITE agent.

    Subclasses must implement:
        - name: a unique identifier string
        - description: human-readable description
        - execute(command): the main entry point
    """

    def __init__(self):
        self.logger = logging.getLogger(f"elite.agents.{self.name}")

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this agent (e.g., 'coder', 'search')."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable one-liner describing this agent."""
        ...

    @abstractmethod
    def execute(self, command: str) -> str:
        """
        Process a user command and return a text response.

        Args:
            command: The raw user input.

        Returns:
            A string response to display.

        Raises:
            AgentError: On any handled failure.
        """
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
