"""
agents/system_agent.py
Returns live CPU / RAM / Disk stats via psutil.
"""

import psutil


def get_system_stats() -> dict:
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    def gb(n):
        return round(n / 1024 ** 3, 1)

    return {
        "cpu":          psutil.cpu_percent(interval=0.5),
        "ram_percent":  ram.percent,
        "ram_used":     gb(ram.used),
        "ram_total":    gb(ram.total),
        "disk_percent": disk.percent,
        "disk_used":    gb(disk.used),
        "disk_total":   gb(disk.total),
    }
