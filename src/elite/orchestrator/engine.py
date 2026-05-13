"""
elite.orchestrator.engine
Autonomous multi-step task runner.
See → Plan → Do → Report cycle.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime

from elite.core.llm import get_llm_client
from elite.core.registry import AgentRegistry
from elite.core.exceptions import AgentError
from elite.integrations.telegram import send_alert

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Multi-step task executor using the See → Plan → Do → Report pattern.

    1. SEE:   Capture screen context (if available)
    2. PLAN:  Ask the LLM to decompose the task into steps
    3. DO:    Execute each step via the action agent
    4. REPORT: Summarize results and optionally notify via Telegram
    """

    def __init__(self):
        self.history: list[dict] = []

    def smart_task(self, task: str) -> str:
        """
        Execute a multi-step autonomous task.

        Args:
            task: Natural language task description.

        Returns:
            A human-readable execution report.
        """
        logger.info("Starting smart task: %s", task[:100])
        send_alert(f"🧠 New task: {task}")

        client = get_llm_client()
        steps: list[str] = [task]

        # ── 1. SEE ────────────────────────────────────────────────
        screen_ctx = ""
        screen_agent = AgentRegistry.get_instance("screen")
        if screen_agent:
            try:
                logger.info("Phase 1/4: Analysing screen...")
                screen_ctx = screen_agent.execute("describe screen")
                self.history.append({
                    "ts": datetime.now().isoformat(),
                    "phase": "see",
                    "context": screen_ctx[:500],
                })
            except Exception as e:
                logger.warning("Screen capture failed: %s", e)
                screen_ctx = "Screen capture unavailable"

        # ── 2. PLAN ───────────────────────────────────────────────
        logger.info("Phase 2/4: Planning steps...")
        plan_prompt = (
            f'Screen context: "{screen_ctx[:400]}"\n'
            f'Task: "{task}"\n'
            "Write a JSON object with a 'steps' key containing a list of 3 concrete steps "
            "to complete this task. Return ONLY the JSON, no explanation."
        )

        try:
            plan_output = client.generate(plan_prompt)
            # Try to extract JSON from the response
            json_start = plan_output.find("{")
            json_end = plan_output.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                parsed = json.loads(plan_output[json_start:json_end])
                steps = parsed.get("steps", [task])
                logger.info("Planned %d steps", len(steps))
        except (json.JSONDecodeError, Exception) as e:
            logger.warning("Plan parsing failed, using single-step fallback: %s", e)
            steps = [task]

        # ── 3. DO ─────────────────────────────────────────────────
        logger.info("Phase 3/4: Executing %d steps...", len(steps))
        results = []
        action_agent = AgentRegistry.get_instance("action")

        for i, step in enumerate(steps[:5], 1):  # Cap at 5 steps
            logger.info("  Step %d: %s", i, step[:80])
            if action_agent:
                try:
                    result = action_agent.execute(step)
                    results.append(f"Step {i}: ✅ {step} → {result}")
                except Exception as e:
                    results.append(f"Step {i}: ⚠️ {step} → Error: {e}")
            else:
                results.append(f"Step {i}: ⏭ {step} (action agent unavailable)")
            time.sleep(0.5)

        # ── 4. REPORT ─────────────────────────────────────────────
        logger.info("Phase 4/4: Generating report...")
        report = f"Task: '{task}'\n\n" + "\n".join(results)

        self.history.append({
            "ts": datetime.now().isoformat(),
            "phase": "report",
            "task": task,
            "steps": len(steps),
            "results": len(results),
        })

        send_alert(report)
        return report


# ── Module-level convenience ──────────────────────────────────────────
_orchestrator = Orchestrator()


@AgentRegistry.register("orchestrator")
class OrchestratorAgent:
    """Wrapper to make the orchestrator accessible via the registry."""

    name = "orchestrator"
    description = "Multi-step autonomous task execution"

    def __init__(self):
        self.logger = logging.getLogger("elite.agents.orchestrator")

    def execute(self, command: str) -> str:
        return _orchestrator.smart_task(command)
