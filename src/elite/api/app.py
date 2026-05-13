"""
elite.api.app
Flask application factory.
"""

from __future__ import annotations

import logging
from pathlib import Path

from flask import Flask

from elite.config.settings import get_settings

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """
    Application factory — creates and configures the Flask app.

    This pattern allows:
    - Multiple app instances for testing
    - Deferred configuration
    - Clean import graph (no circular imports)
    """
    settings = get_settings()

    # Resolve template and static directories
    project_root = settings.project_root
    template_dir = str(project_root / "templates")
    static_dir = str(project_root / "static")

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
    )

    app.config["SECRET_KEY"] = settings.secret_key

    # ── Register middleware ────────────────────────────────────────
    from elite.api.middleware import register_middleware
    register_middleware(app)

    # ── Register routes ───────────────────────────────────────────
    from elite.api.routes import register_routes
    register_routes(app)

    # ── Import agents to trigger registration ─────────────────────
    import elite.agents  # noqa: F401
    import elite.orchestrator.engine  # noqa: F401

    logger.info(
        "Flask app created",
        extra={"template_dir": template_dir, "static_dir": static_dir},
    )

    return app
