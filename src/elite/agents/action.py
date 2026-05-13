"""
elite.agents.action
Mouse/keyboard automation agent via PyAutoGUI.
Gracefully degrades when pyautogui is not installed.
"""

from __future__ import annotations

import re

from elite.agents.base import BaseAgent
from elite.core.registry import AgentRegistry


@AgentRegistry.register("action")
class ActionAgent(BaseAgent):
    """Mouse and keyboard automation via PyAutoGUI."""

    @property
    def name(self) -> str:
        return "action"

    @property
    def description(self) -> str:
        return "Mouse clicks, keyboard typing, scrolling, and screenshots"

    def execute(self, command: str) -> str:
        try:
            import pyautogui
        except ImportError:
            return (
                "Action agent unavailable — pyautogui not installed.\n"
                "Install with: pip install elite-ai-agent[action]"
            )

        instr = command.lower()

        if "click" in instr:
            return self._click(pyautogui)
        if "type" in instr or "write" in instr:
            return self._type_text(pyautogui, command)
        if "screenshot" in instr:
            return self._screenshot(pyautogui)
        if "scroll" in instr:
            return self._scroll(pyautogui, instr)
        if "position" in instr or "mouse" in instr:
            return self._get_position(pyautogui)

        return (
            "Available actions:\n"
            "  • click        — Click at current position\n"
            "  • type \"text\"  — Type text via keyboard\n"
            "  • screenshot   — Take a screenshot\n"
            "  • scroll up/down — Scroll the mouse wheel\n"
            "  • mouse position — Get current cursor position"
        )

    @staticmethod
    def _click(pyautogui) -> str:
        x, y = pyautogui.position()
        pyautogui.click(x, y)
        return f"✅ Clicked at ({x}, {y})"

    @staticmethod
    def _type_text(pyautogui, command: str) -> str:
        match = re.search(r'["\'](.+?)["\']', command)
        text = match.group(1) if match else command
        pyautogui.typewrite(text, interval=0.05)
        return f"✅ Typed: {text[:50]}"

    @staticmethod
    def _screenshot(pyautogui) -> str:
        from datetime import datetime

        path = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        pyautogui.screenshot(path)
        return f"✅ Screenshot saved: {path}"

    @staticmethod
    def _scroll(pyautogui, instr: str) -> str:
        amount = 3 if "down" in instr else -3
        direction = "down" if amount > 0 else "up"
        pyautogui.scroll(amount)
        return f"✅ Scrolled {direction}"

    @staticmethod
    def _get_position(pyautogui) -> str:
        x, y = pyautogui.position()
        return f"🖱 Mouse position: ({x}, {y})"
