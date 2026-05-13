"""
elite.agents.system
System monitoring agent — live CPU, RAM, and disk stats via psutil.
"""

from __future__ import annotations

import platform
from datetime import datetime

import psutil

from elite.agents.base import BaseAgent
from elite.core.registry import AgentRegistry


def _gb(n: float) -> float:
    """Convert bytes to GB, rounded to 1 decimal."""
    return round(n / (1024**3), 1)


@AgentRegistry.register("system")
class SystemAgent(BaseAgent):
    """Reports live system resource utilization."""

    @property
    def name(self) -> str:
        return "system"

    @property
    def description(self) -> str:
        return "Real-time CPU, RAM, and disk usage monitoring"

    def execute(self, command: str) -> str:
        stats = self.get_stats()
        lines = [
            "── System Status ──",
            f"  Host:    {stats['hostname']}",
            f"  OS:      {stats['os']}",
            f"  Python:  {stats['python']}",
            f"  Uptime:  {stats['uptime']}",
            "",
            "── Resources ──",
            f"  CPU:     {stats['cpu']}% ({stats['cpu_count']} cores)",
            f"  RAM:     {stats['ram_used']} / {stats['ram_total']} GB ({stats['ram_percent']}%)",
            f"  Disk:    {stats['disk_used']} / {stats['disk_total']} GB ({stats['disk_percent']}%)",
        ]
        return "\n".join(lines)

    @staticmethod
    def get_stats() -> dict:
        """Return a dict of system stats — also used by the REST API."""
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # Calculate uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)

        return {
            "hostname": platform.node(),
            "os": f"{platform.system()} {platform.release()}",
            "python": platform.python_version(),
            "uptime": f"{hours}h {minutes}m",
            "cpu": psutil.cpu_percent(interval=0.5),
            "cpu_count": psutil.cpu_count(),
            "ram_percent": ram.percent,
            "ram_used": _gb(ram.used),
            "ram_total": _gb(ram.total),
            "disk_percent": disk.percent,
            "disk_used": _gb(disk.used),
            "disk_total": _gb(disk.total),
        }
