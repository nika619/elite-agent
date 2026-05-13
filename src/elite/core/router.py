"""
elite.core.router
Intent classification and command routing.

Uses a weighted keyword scoring system with confidence thresholds.
Falls back to direct LLM when no agent matches.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from elite.core.registry import AgentRegistry
from elite.core.exceptions import RouterError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RouteResult:
    """The outcome of intent classification."""
    agent_name: str
    confidence: float  # 0.0 – 1.0
    matched_keywords: list[str]


# ── Keyword → Agent mapping with weights ──────────────────────────────
# Higher weight = stronger signal. Weights are normalized per-agent.
INTENT_MAP: dict[str, list[tuple[str, float]]] = {
    "coder": [
        ("write code", 3.0),
        ("write a script", 3.0),
        ("write a program", 3.0),
        ("python script", 3.0),
        ("code", 2.0),
        ("script", 2.0),
        ("program", 1.5),
        ("function", 1.5),
        ("implement", 1.5),
        ("debug", 1.5),
        ("compile", 1.0),
    ],
    "search": [
        ("search for", 3.0),
        ("look up", 3.0),
        ("search", 2.5),
        ("google", 2.0),
        ("find information", 2.0),
        ("what is", 2.0),
        ("who is", 2.0),
        ("latest news", 1.5),
    ],
    "filesystem": [
        ("list files", 3.0),
        ("read file", 3.0),
        ("write file", 3.0),
        ("show directory", 2.5),
        ("file", 1.5),
        ("directory", 1.5),
        ("folder", 1.5),
        ("ls", 1.5),
        ("cat", 1.0),
    ],
    "system": [
        ("system status", 3.0),
        ("cpu usage", 3.0),
        ("ram usage", 3.0),
        ("disk usage", 3.0),
        ("status", 2.0),
        ("cpu", 2.0),
        ("ram", 2.0),
        ("memory", 1.5),
        ("disk", 1.5),
    ],
    "telegram": [
        ("send alert", 3.0),
        ("send notification", 3.0),
        ("telegram", 2.5),
        ("alert", 2.0),
        ("notify", 2.0),
    ],
    "orchestrator": [
        ("smart task", 3.0),
        ("automate", 2.5),
        ("execute task", 2.5),
        ("do task", 2.0),
        ("multi-step", 2.0),
        ("autonomous", 2.0),
    ],
}

# Minimum confidence to route to a specific agent (otherwise → LLM)
CONFIDENCE_THRESHOLD = 0.25


class Router:
    """
    Routes user commands to the appropriate agent.

    Scoring algorithm:
    1. Normalize command to lowercase
    2. For each agent, sum weights of matched keywords
    3. Normalize by max possible weight for that agent
    4. Select the agent with the highest score above threshold
    5. Fall back to 'llm' if no agent exceeds threshold
    """

    def __init__(self, intent_map: dict | None = None, threshold: float | None = None):
        self._intent_map = intent_map or INTENT_MAP
        self._threshold = threshold or CONFIDENCE_THRESHOLD

        # Pre-compute max weights for normalization
        self._max_weights: dict[str, float] = {}
        for agent, keywords in self._intent_map.items():
            self._max_weights[agent] = sum(w for _, w in keywords)

    def classify(self, command: str) -> RouteResult:
        """
        Classify a command and return the best-matching agent.

        Args:
            command: The raw user input.

        Returns:
            RouteResult with agent_name, confidence, and matched_keywords.
        """
        cmd_lower = command.lower()
        best_agent = "llm"
        best_score = 0.0
        best_keywords: list[str] = []

        for agent, keywords in self._intent_map.items():
            score = 0.0
            matched = []
            for keyword, weight in keywords:
                if keyword in cmd_lower:
                    score += weight
                    matched.append(keyword)

            max_weight = self._max_weights.get(agent, 1.0)
            normalized = score / max_weight if max_weight > 0 else 0.0

            if normalized > best_score:
                best_score = normalized
                best_agent = agent
                best_keywords = matched

        if best_score < self._threshold:
            best_agent = "llm"
            best_keywords = []

        result = RouteResult(
            agent_name=best_agent,
            confidence=round(best_score, 3),
            matched_keywords=best_keywords,
        )

        logger.info(
            "Routed command",
            extra={
                "agent": result.agent_name,
                "confidence": result.confidence,
                "keywords": result.matched_keywords,
                "command_preview": command[:80],
            },
        )
        return result

    def route_and_execute(self, command: str) -> dict:
        """
        Classify command, instantiate the agent, and execute.

        Returns:
            Dict with keys: response, route, success, confidence
        """
        result = self.classify(command)

        # ── Direct LLM fallback ─────────────────────────────────
        if result.agent_name == "llm":
            from elite.core.llm import get_llm_client
            try:
                client = get_llm_client()
                response = client.generate(command)
                return {
                    "response": response,
                    "route": "llm",
                    "success": True,
                    "confidence": 0.0,
                }
            except Exception as e:
                logger.error("LLM fallback failed: %s", e)
                return {
                    "response": f"LLM Error: {e}",
                    "route": "error",
                    "success": False,
                    "confidence": 0.0,
                }

        # ── Agent execution ──────────────────────────────────────
        agent = AgentRegistry.get_instance(result.agent_name)
        if agent is None:
            logger.warning("Agent '%s' not found in registry", result.agent_name)
            # Fall back to LLM
            from elite.core.llm import get_llm_client
            try:
                client = get_llm_client()
                response = client.generate(command)
                return {
                    "response": response,
                    "route": "llm",
                    "success": True,
                    "confidence": 0.0,
                }
            except Exception as e:
                return {
                    "response": f"Error: {e}",
                    "route": "error",
                    "success": False,
                    "confidence": 0.0,
                }

        try:
            response = agent.execute(command)
            return {
                "response": response,
                "route": result.agent_name,
                "success": True,
                "confidence": result.confidence,
            }
        except Exception as e:
            logger.exception("Agent '%s' raised an exception", result.agent_name)
            return {
                "response": f"Agent error ({result.agent_name}): {e}",
                "route": "error",
                "success": False,
                "confidence": result.confidence,
            }
