"""
elite.api.routes
All API endpoints for the ELITE web interface.
"""

from __future__ import annotations

import logging
from datetime import datetime

from flask import Flask, request, jsonify, render_template

from elite.core.router import Router
from elite.core.registry import AgentRegistry

logger = logging.getLogger(__name__)

# Single router instance
_router = Router()


def register_routes(app: Flask) -> None:
    """Register all routes on the Flask app."""

    # ── Pages ─────────────────────────────────────────────────────

    @app.route("/")
    def index():
        """Serve the main web UI."""
        return render_template("index.html")

    # ── Chat API ──────────────────────────────────────────────────

    @app.route("/api/chat", methods=["POST"])
    def chat():
        """
        Main chat endpoint.
        Receives a message, routes it to the appropriate agent,
        and returns the response.
        """
        data = request.get_json(silent=True) or {}
        command = data.get("message", "").strip()

        if not command:
            return jsonify({
                "response": "Please enter a command.",
                "route": "error",
                "success": False,
            }), 400

        logger.info("Chat request: %s", command[:100])

        result = _router.route_and_execute(command)
        return jsonify(result)

    # ── System Status API ─────────────────────────────────────────

    @app.route("/api/status")
    def status():
        """Return live system stats."""
        agent = AgentRegistry.get_instance("system")
        if agent is None:
            return jsonify({"error": "System agent not available"}), 503

        from elite.agents.system import SystemAgent
        stats = SystemAgent.get_stats()
        return jsonify(stats)

    # ── Coder API ─────────────────────────────────────────────────

    @app.route("/api/coder", methods=["POST"])
    def run_coder():
        """Direct endpoint for the coder agent."""
        data = request.get_json(silent=True) or {}
        task = data.get("task", "").strip()

        if not task:
            return jsonify({"error": "No task provided"}), 400

        agent = AgentRegistry.get_instance("coder")
        if agent is None:
            return jsonify({"error": "Coder agent not available"}), 503

        try:
            result = agent.execute(task)
            return jsonify({"result": result, "success": True})
        except Exception as e:
            return jsonify({"error": str(e), "success": False}), 500

    # ── Screen API ────────────────────────────────────────────────

    @app.route("/api/screen")
    def screen_read():
        """Capture and return screen text."""
        agent = AgentRegistry.get_instance("screen")
        if agent is None:
            return jsonify({"error": "Screen agent not available"}), 503

        try:
            result = agent.execute("describe screen")
            return jsonify({"screen_text": result, "success": True})
        except Exception as e:
            return jsonify({"error": str(e), "success": False}), 500

    # ── Health Check ──────────────────────────────────────────────

    @app.route("/api/health")
    def health():
        """Health check endpoint for monitoring."""
        from elite.core.llm import get_llm_client

        client = get_llm_client()
        ollama_ok = client.is_healthy()
        agents = AgentRegistry.names()

        return jsonify({
            "status": "healthy" if ollama_ok else "degraded",
            "ollama": "connected" if ollama_ok else "disconnected",
            "model": client.model,
            "agents": agents,
            "agent_count": len(agents),
            "timestamp": datetime.now().isoformat(),
        })

    # ── Agent Registry Info ───────────────────────────────────────

    @app.route("/api/agents")
    def list_agents():
        """List all registered agents and their descriptions."""
        agents = []
        for name, cls in AgentRegistry.list_agents().items():
            instance = cls()
            agents.append({
                "name": name,
                "description": instance.description,
                "class": cls.__name__,
            })
        return jsonify({"agents": agents})
