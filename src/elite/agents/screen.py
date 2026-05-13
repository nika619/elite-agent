"""
elite.agents.screen
Screen capture agent — screenshots + OCR via pytesseract.
Gracefully degrades when optional dependencies are missing.
"""

from __future__ import annotations

from elite.agents.base import BaseAgent
from elite.core.registry import AgentRegistry


@AgentRegistry.register("screen")
class ScreenAgent(BaseAgent):
    """Captures the screen and extracts readable text via OCR."""

    @property
    def name(self) -> str:
        return "screen"

    @property
    def description(self) -> str:
        return "Screen capture with OCR text extraction"

    def execute(self, command: str) -> str:
        return self.describe_screen()

    @staticmethod
    def describe_screen() -> str:
        """Capture the screen and return extracted text."""
        try:
            import pytesseract
            from PIL import ImageGrab

            img = ImageGrab.grab()
            text = pytesseract.image_to_string(img)
            return text.strip() or "Screen captured but no text detected."
        except ImportError:
            return (
                "Screen agent unavailable — optional dependencies missing.\n"
                "Install with: pip install elite-ai-agent[screen]"
            )
        except Exception as e:
            return f"Screen capture error: {e}"
