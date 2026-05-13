"""
core/orchestrator.py
Routes every user command to the correct agent.
"""

import requests
from config import OLLAMA_URL, MODEL_NAME


# ── Low-level LLM call ────────────────────────────────────────────────
def ask_ollama(prompt: str, model: str = MODEL_NAME) -> str:
    try:
        r = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=120,
        )
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"ERROR: {e}"


# ── Router ────────────────────────────────────────────────────────────
def run_command(command: str) -> dict:
    cmd = command.lower()

    # ── code / script ──────────────────────────────────────────────
    if any(k in cmd for k in ("write", "code", "script", "python", "program")):
        from agents.coder_agent import write_and_run
        result = write_and_run(command)
        return {"response": result, "route": "coder", "route_color": "g", "success": True}

    # ── web search ─────────────────────────────────────────────────
    if any(k in cmd for k in ("search", "find", "google", "look up", "what is", "who is")):
        from agents.web_search_agent import search_web
        result = search_web(command)
        return {"response": result, "route": "search", "route_color": "b", "success": True}

    # ── file ops ───────────────────────────────────────────────────
    if any(k in cmd for k in ("file", "read", "write", "list", "folder", "directory")):
        from agents.file_agent import handle_file_command
        result = handle_file_command(command)
        return {"response": result, "route": "file", "route_color": "y", "success": True}

    # ── system stats ───────────────────────────────────────────────
    if any(k in cmd for k in ("status", "cpu", "ram", "memory", "disk", "system")):
        from agents.system_agent import get_system_stats
        stats = get_system_stats()
        lines = [
            f"CPU:  {stats['cpu']}%",
            f"RAM:  {stats['ram_used']} / {stats['ram_total']} GB  ({stats['ram_percent']}%)",
            f"Disk: {stats['disk_used']} / {stats['disk_total']} GB  ({stats['disk_percent']}%)",
        ]
        return {"response": "\n".join(lines), "route": "system", "route_color": "c", "success": True}

    # ── telegram alert ─────────────────────────────────────────────
    if any(k in cmd for k in ("alert", "notify", "telegram", "send message")):
        from alerts.telegram_bot import send_alert
        msg = command.replace("alert", "").replace("notify", "").strip()
        send_alert(msg or "ping from ELITE")
        return {"response": "✅ Alert sent via Telegram.", "route": "telegram", "route_color": "m", "success": True}

    # ── smart autonomous task ──────────────────────────────────────
    if any(k in cmd for k in ("do", "task", "automate", "run", "execute", "smart")):
        from elite_orchestrator import smart_task
        result = smart_task(command)
        return {"response": result, "route": "orchestrator", "route_color": "p", "success": True}

    # ── default: direct LLM ────────────────────────────────────────
    response = ask_ollama(command)
    return {"response": response, "route": "llm", "route_color": "c", "success": True}
