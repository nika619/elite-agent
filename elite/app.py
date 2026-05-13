"""
app.py — Flask web server for ELITE.
Run: python app.py
"""

import os
from flask import Flask, request, jsonify, render_template
from core.orchestrator import run_command

app = Flask(__name__, template_folder="templates", static_folder="static")


# ── Pages ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── Chat API ──────────────────────────────────────────────────────────

@app.route("/chat", methods=["POST"])
def chat():
    data    = request.json or {}
    command = data.get("message", "").strip()
    if not command:
        return jsonify({"response": "Please enter a command.", "route": "—", "success": False})
    try:
        result = run_command(command)
        return jsonify(result if isinstance(result, dict) else {"response": str(result), "route": "llm", "success": True})
    except Exception as e:
        return jsonify({"response": f"ERROR: {e}", "route": "error", "success": False})


# ── System status API ─────────────────────────────────────────────────

@app.route("/status")
def status():
    from agents.system_agent import get_system_stats
    return jsonify(get_system_stats())


# ── Coder shortcut API ────────────────────────────────────────────────

@app.route("/api/coder", methods=["POST"])
def run_coder():
    data = request.json or {}
    task = data.get("task", "").strip()
    if not task:
        return jsonify({"error": "No task provided"}), 400
    from agents.coder_agent import write_and_run
    return jsonify({"result": write_and_run(task)})


# ── Screen reader API ─────────────────────────────────────────────────

@app.route("/api/screen")
def screen_read():
    from agents.screen_agent import describe_screen
    return jsonify({"screen_text": describe_screen()})


# ── Entry point ───────────────────────────────────────────────────────

if __name__ == "__main__":
    from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG, use_reloader=False)
