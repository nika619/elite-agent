"""
agents/action_agent.py
Mouse / keyboard automation via PyAutoGUI.
Falls back gracefully if pyautogui is not installed.
"""


def get_mouse_position() -> tuple[int, int] | str:
    try:
        import pyautogui
        return pyautogui.position()
    except ImportError:
        return "pyautogui not installed"
    except Exception as e:
        return str(e)


def take_action(instruction: str) -> bool:
    """
    Interpret a plain-English instruction and execute it via pyautogui.
    Returns True on success, False on failure.
    """
    try:
        import pyautogui
        instr = instruction.lower()

        if "click" in instr:
            x, y = pyautogui.position()
            pyautogui.click(x, y)
            return True

        if "type" in instr or "write" in instr:
            # extract quoted text if present
            import re
            match = re.search(r'["\'](.+?)["\']', instruction)
            text = match.group(1) if match else instruction
            pyautogui.typewrite(text, interval=0.05)
            return True

        if "screenshot" in instr:
            import datetime
            path = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            pyautogui.screenshot(path)
            return True

        if "scroll" in instr:
            amount = 3 if "down" in instr else -3
            pyautogui.scroll(amount)
            return True

        # default: do nothing but report
        print(f"  [action] No handler for: {instruction}")
        return False

    except ImportError:
        print("  pyautogui not installed — action skipped")
        return False
    except Exception as e:
        print(f"  action error: {e}")
        return False
