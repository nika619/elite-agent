"""
agents/coder_agent.py
Writes a Python script from a natural-language task,
runs it, auto-fixes errors, and retries until it works.
"""

import os
import subprocess
import tempfile

import requests
from config import OLLAMA_URL, MODEL_NAME, MAX_RETRIES, CODE_SAVE_DIR

_TAG = "```"


def _ask(prompt: str) -> str:
    try:
        r = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=120,
        )
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"ERROR: {e}"


def _extract_code(text: str) -> str:
    """Pull the first code block out of a markdown response."""
    py_tag = _TAG + "python"
    if py_tag in text:
        return text.split(py_tag)[1].split(_TAG)[0].strip()
    if _TAG in text:
        parts = text.split(_TAG)
        if len(parts) >= 2:
            return parts[1].strip()
    # fallback: strip conversational opener lines
    lines = [
        l for l in text.strip().splitlines()
        if not l.lower().startswith(("here", "sure", "this", "below", "of course"))
    ]
    return "\n".join(lines).strip()


def _run_code(code: str, timeout: int = 30) -> tuple[str, str]:
    """Write code to a temp file, execute it, return (stdout, stderr)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        tmp = f.name
    try:
        res = subprocess.run(
            ["python", tmp], capture_output=True, text=True, timeout=timeout
        )
        return res.stdout, res.stderr
    except subprocess.TimeoutExpired:
        return "", "TimeoutError: script took too long"
    except Exception as e:
        return "", str(e)
    finally:
        os.unlink(tmp)


def write_and_run(task: str, save_path: str | None = None) -> str:
    """
    Generate + run code for `task`.
    Retries up to MAX_RETRIES times on failure.
    Returns the final stdout output (or the working code itself).
    """
    print(f"\n[CODER] Task: {task}")
    print("  Press Ctrl+C to stop\n")

    errors: list[str] = []
    prompt = (
        f"Write a complete Python script that does: {task}\n"
        f"Return ONLY the code inside a {_TAG}python block. No explanation."
    )

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"  [attempt {attempt}] generating...")
        response = _ask(prompt)
        code = _extract_code(response)

        if not code:
            print("  No code extracted — retrying...")
            continue

        print("  [running]")
        stdout, stderr = _run_code(code)

        if stderr and "rror" in stderr:
            short_err = stderr[:300]
            print(f"  ✗ {short_err}")
            errors.append(f"Attempt {attempt}: {short_err}")
            history = "\n".join(errors)
            prompt = (
                f"Task: {task}\n"
                f"Previous errors:\n{history}\n"
                f"Fix the code. Return ONLY code in a {_TAG}python block."
            )
        else:
            print(f"  ✅ SUCCESS on attempt #{attempt}")
            print(f"  Output: {stdout[:500]}")
            if save_path:
                os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
                with open(save_path, "w") as fh:
                    fh.write(code)
            elif CODE_SAVE_DIR:
                os.makedirs(CODE_SAVE_DIR, exist_ok=True)
            return stdout or code

    return "ERROR: all attempts exhausted without success."
