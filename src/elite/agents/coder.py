"""
elite.agents.coder
Code generation agent — writes Python scripts from natural language,
executes them in a sandboxed subprocess, and auto-retries on errors.
"""

from __future__ import annotations

import os
import subprocess
import tempfile

from elite.agents.base import BaseAgent
from elite.core.registry import AgentRegistry
from elite.core.llm import get_llm_client
from elite.core.exceptions import AgentError
from elite.config.settings import get_settings

_TAG = "```"


def _extract_code(text: str) -> str:
    """Extract the first code block from an LLM markdown response."""
    py_tag = _TAG + "python"
    if py_tag in text:
        return text.split(py_tag)[1].split(_TAG)[0].strip()
    if _TAG in text:
        parts = text.split(_TAG)
        if len(parts) >= 2:
            return parts[1].strip()
    # Fallback: strip common conversational openers
    lines = [
        line
        for line in text.strip().splitlines()
        if not line.lower().startswith(("here", "sure", "this", "below", "of course"))
    ]
    return "\n".join(lines).strip()


def _run_code(code: str, timeout: int = 30) -> tuple[str, str]:
    """Write code to a temp file, execute, return (stdout, stderr)."""
    fd, tmp_path = tempfile.mkstemp(suffix=".py", prefix="elite_")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return "", f"TimeoutError: script exceeded {timeout}s limit"
    except Exception as e:
        return "", str(e)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


@AgentRegistry.register("coder")
class CoderAgent(BaseAgent):
    """Generates and executes Python code from natural language tasks."""

    @property
    def name(self) -> str:
        return "coder"

    @property
    def description(self) -> str:
        return "Writes and runs Python scripts from natural language descriptions"

    def execute(self, command: str) -> str:
        settings = get_settings()
        client = get_llm_client()
        max_retries = settings.coder_max_retries
        code_timeout = settings.coder_timeout

        self.logger.info("Coder task: %s", command[:100])

        errors: list[str] = []
        prompt = (
            f"Write a complete Python script that does: {command}\n"
            f"Return ONLY the code inside a ```python block. No explanation."
        )

        for attempt in range(1, max_retries + 1):
            self.logger.debug("Attempt %d/%d", attempt, max_retries)

            try:
                response = client.generate(prompt)
            except Exception as e:
                self.logger.error("LLM call failed on attempt %d: %s", attempt, e)
                errors.append(f"Attempt {attempt}: LLM error — {e}")
                continue

            code = _extract_code(response)
            if not code:
                self.logger.warning("No code extracted on attempt %d", attempt)
                continue

            stdout, stderr = _run_code(code, timeout=code_timeout)

            if stderr and "rror" in stderr:
                short_err = stderr[:300]
                self.logger.warning("Attempt %d failed: %s", attempt, short_err)
                errors.append(f"Attempt {attempt}: {short_err}")
                history = "\n".join(errors[-5:])  # Keep last 5 errors for context
                prompt = (
                    f"Task: {command}\n"
                    f"Previous errors:\n{history}\n"
                    f"Fix the code. Return ONLY code in a ```python block."
                )
            else:
                self.logger.info("Success on attempt %d", attempt)
                # Optionally save the working script
                if settings.coder_save_dir:
                    os.makedirs(settings.coder_save_dir, exist_ok=True)
                return stdout if stdout else code

        raise AgentError(
            f"All {max_retries} attempts exhausted",
            agent_name=self.name,
            detail="\n".join(errors[-3:]),
        )
