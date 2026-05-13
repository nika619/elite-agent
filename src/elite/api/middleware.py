"""
elite.api.middleware
Cross-cutting concerns: error handling, CORS, request logging.
"""

from __future__ import annotations

import logging
import time

from flask import Flask, request, jsonify, g

logger = logging.getLogger(__name__)


def register_middleware(app: Flask) -> None:
    """Register all middleware on the Flask app."""

    # ── Request timing ────────────────────────────────────────────

    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(g, "start_time"):
            elapsed = round((time.time() - g.start_time) * 1000, 1)
            logger.info(
                "%s %s → %d (%sms)",
                request.method,
                request.path,
                response.status_code,
                elapsed,
            )
        # ── CORS headers ─────────────────────────────────────────
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response

    # ── Global error handlers ─────────────────────────────────────

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request", "detail": str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "detail": str(e)}), 404

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("Unhandled server error")
        return jsonify({"error": "Internal server error", "detail": str(e)}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.exception("Unhandled exception: %s", e)
        return jsonify({"error": "Unexpected error", "detail": str(e)}), 500
