"""
agents/screen_agent.py
Captures the screen and extracts readable text via OCR (pytesseract).
Falls back gracefully if dependencies are missing.
"""


def describe_screen() -> str:
    try:
        import pytesseract
        from PIL import ImageGrab
        img = ImageGrab.grab()
        text = pytesseract.image_to_string(img)
        return text.strip() or "Screen captured but no text detected."
    except ImportError:
        return "Screen agent unavailable: install Pillow + pytesseract"
    except Exception as e:
        return f"Screen capture error: {e}"
