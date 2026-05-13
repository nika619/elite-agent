"""
agents/file_agent.py
Read / write / list / search files on the local filesystem.
"""

import os
import glob


def handle_file_command(command: str) -> str:
    cmd = command.lower()

    # ── list ───────────────────────────────────────────────────────
    if any(k in cmd for k in ("list", "ls", "show files", "directory")):
        path = "."
        for word in command.split():
            if os.path.isdir(word):
                path = word
                break
        files = os.listdir(path)
        return f"📁 {os.path.abspath(path)}\n" + "\n".join(sorted(files)) if files else "Directory is empty."

    # ── read ───────────────────────────────────────────────────────
    if any(k in cmd for k in ("read", "open", "show", "cat", "print")):
        for word in command.split():
            if os.path.isfile(word):
                with open(word, "r", errors="replace") as f:
                    content = f.read()
                return f"📄 {word} ({len(content)} chars):\n\n{content[:3000]}"
        return "No file path found in command. Usage: read <path>"

    # ── write ──────────────────────────────────────────────────────
    if any(k in cmd for k in ("write", "create", "save")):
        parts = command.split(" ", 2)
        if len(parts) >= 3:
            path, content = parts[1], parts[2]
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return f"✅ Written to {path}"
        return "Usage: write <path> <content>"

    # ── search ─────────────────────────────────────────────────────
    if "search" in cmd or "find" in cmd:
        words = command.split()
        pattern = words[-1] if len(words) > 1 else "*"
        matches = glob.glob(f"**/{pattern}", recursive=True)
        if matches:
            return "🔍 Found:\n" + "\n".join(matches[:20])
        return f"No files matching '{pattern}' found."

    return "Unknown file command. Try: list, read <file>, write <file> <content>, search <pattern>"
