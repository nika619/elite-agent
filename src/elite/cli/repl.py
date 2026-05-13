"""
elite.cli.repl
Interactive CLI using Rich for premium terminal output.
"""

from __future__ import annotations

import sys
import argparse

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.theme import Theme

# ── Custom theme ──────────────────────────────────────────────────────
elite_theme = Theme({
    "info": "cyan",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "agent.coder": "green",
    "agent.search": "blue",
    "agent.filesystem": "yellow",
    "agent.system": "cyan",
    "agent.telegram": "magenta",
    "agent.orchestrator": "bright_magenta",
    "agent.llm": "white",
    "agent.error": "red",
})

console = Console(theme=elite_theme)

BANNER = r"""
[green]  ███████╗██╗     ██╗████████╗███████╗[/green]
[green]  ██╔════╝██║     ██║╚══██╔══╝██╔════╝[/green]
[green]  █████╗  ██║     ██║   ██║   █████╗[/green]
[green]  ██╔══╝  ██║     ██║   ██║   ██╔══╝[/green]
[green]  ███████╗███████╗██║   ██║   ███████╗[/green]
[green]  ╚══════╝╚══════╝╚═╝   ╚═╝   ╚══════╝[/green]
  [dim]AI Agent System v2.0  │  Enterprise Edition[/dim]
"""


def _build_help_table() -> Table:
    """Build a Rich table showing available commands."""
    table = Table(
        title="Agent Routing",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        pad_edge=False,
    )
    table.add_column("Agent", style="green", width=14)
    table.add_column("Trigger Keywords", style="white")

    table.add_row("coder", "write / code / script / program / implement")
    table.add_row("search", "search / find / what is / who is / google")
    table.add_row("filesystem", "file / read / list / directory / folder")
    table.add_row("system", "cpu / ram / disk / status / system")
    table.add_row("telegram", "alert / notify / telegram")
    table.add_row("orchestrator", "smart task / automate / autonomous")
    table.add_row("[dim]llm[/dim]", "[dim]anything else → direct LLM[/dim]")

    return table


def _run_cli():
    """Run the interactive REPL."""
    # Initialize logging and settings
    from elite.config.settings import get_settings
    from elite.utils.logging import setup_logging

    settings = get_settings()
    setup_logging(level=settings.log_level, format_type=settings.log_format)

    # Import agents to trigger registration
    import elite.agents  # noqa: F401
    import elite.orchestrator.engine  # noqa: F401

    from elite.core.router import Router
    from elite.core.registry import AgentRegistry

    router = Router()

    # Show banner
    console.print(BANNER)
    console.print(_build_help_table())
    console.print()

    # Show registered agents
    agents = AgentRegistry.names()
    console.print(f"  [dim]Registered agents: {', '.join(agents)}[/dim]")
    console.print(f"  [dim]Model: {settings.model_name} via {settings.ollama_base_url}[/dim]")
    console.print(f"  [dim]Type 'help' for commands, 'exit' to quit.[/dim]\n")

    while True:
        try:
            cmd = console.input("[green bold]ELITE ❯❯❯ [/green bold]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye.[/dim]")
            sys.exit(0)

        if not cmd:
            continue

        if cmd.lower() in ("exit", "quit", "q"):
            console.print("[dim]Goodbye.[/dim]")
            break

        if cmd.lower() == "help":
            console.print(_build_help_table())
            continue

        if cmd.lower() == "health":
            from elite.core.llm import get_llm_client
            client = get_llm_client()
            healthy = client.is_healthy()
            status = "[green]● Connected[/green]" if healthy else "[red]● Disconnected[/red]"
            console.print(f"  Ollama: {status}")
            console.print(f"  Model:  {client.model}")
            console.print(f"  Agents: {', '.join(agents)}")
            continue

        if cmd.lower() == "agents":
            for name, cls in AgentRegistry.list_agents().items():
                inst = cls()
                console.print(f"  [green]{name:15}[/green] {inst.description}")
            continue

        # ── Route and execute ─────────────────────────────────────
        try:
            result = router.route_and_execute(cmd)
            route = result.get("route", "llm")
            text = result.get("response", "")
            confidence = result.get("confidence", 0)

            style = f"agent.{route}" if f"agent.{route}" in elite_theme.styles else "white"

            header = Text()
            header.append(f"  [{route.upper()}]", style=style)
            if confidence > 0:
                header.append(f"  confidence: {confidence:.0%}", style="dim")

            console.print(header)
            console.print(Panel(
                text,
                border_style="dim",
                padding=(0, 1),
                expand=False,
            ))
            console.print()

        except Exception as e:
            console.print(f"  [error]ERROR: {e}[/error]\n")


def _run_web():
    """Run the Flask web server."""
    from elite.config.settings import get_settings
    from elite.utils.logging import setup_logging

    settings = get_settings()
    setup_logging(level=settings.log_level, format_type=settings.log_format)

    from elite.api.app import create_app

    app = create_app()
    console.print(BANNER)
    console.print(f"  [cyan]Starting web server on http://{settings.host}:{settings.port}[/cyan]")
    console.print(f"  [dim]Model: {settings.model_name}[/dim]\n")

    app.run(
        host=settings.host,
        port=settings.port,
        debug=settings.debug,
        use_reloader=False,
    )


def main():
    """Main entry point — supports both CLI and web modes."""
    parser = argparse.ArgumentParser(
        prog="elite",
        description="ELITE AI Agent System v2.0",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Start the Flask web UI instead of CLI",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Override the port (default: 5000)",
    )

    args = parser.parse_args()

    if args.port:
        import os
        os.environ["ELITE_PORT"] = str(args.port)

    if args.web:
        _run_web()
    else:
        _run_cli()


if __name__ == "__main__":
    main()
