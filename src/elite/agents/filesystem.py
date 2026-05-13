"""
elite.agents.filesystem
File operations agent — read, write, list, and search files.
"""

from __future__ import annotations

import glob
import os

from elite.agents.base import BaseAgent
from elite.core.registry import AgentRegistry
from elite.core.exceptions import AgentError


@AgentRegistry.register("filesystem")
class FilesystemAgent(BaseAgent):
    """Performs local filesystem operations: read, write, list, search."""

    @property
    def name(self) -> str:
        return "filesystem"

    @property
    def description(self) -> str:
        return "Read, write, list, and search files on the local filesystem"

    def execute(self, command: str) -> str:
        cmd = command.lower()

        if any(k in cmd for k in ("list", "ls", "show files", "directory")):
            return self._list_dir(command)
        if any(k in cmd for k in ("read", "open", "show", "cat", "print")):
            return self._read_file(command)
        if any(k in cmd for k in ("write", "create", "save")):
            return self._write_file(command)
        if any(k in cmd for k in ("search", "find", "locate")):
            return self._search_files(command)

        return (
            "Unknown file command. Available operations:\n"
            "  • list <directory>  — List directory contents\n"
            "  • read <file>       — Read a file\n"
            "  • write <file> <content> — Write to a file\n"
            "  • search <pattern>  — Search for files"
        )

    def _list_dir(self, command: str) -> str:
        """List contents of a directory."""
        path = "."
        for word in command.split():
            if os.path.isdir(word):
                path = word
                break

        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            return f"Permission denied: {path}"
        except FileNotFoundError:
            return f"Directory not found: {path}"

        if not entries:
            return f"📁 {os.path.abspath(path)} — empty"

        lines = [f"📁 {os.path.abspath(path)}"]
        for entry in entries:
            full = os.path.join(path, entry)
            indicator = "📂" if os.path.isdir(full) else "📄"
            try:
                size = os.path.getsize(full)
                size_str = self._human_size(size)
            except OSError:
                size_str = "?"
            lines.append(f"  {indicator} {entry}  ({size_str})")

        return "\n".join(lines)

    def _read_file(self, command: str) -> str:
        """Read and return file contents."""
        for word in command.split():
            if os.path.isfile(word):
                try:
                    with open(word, "r", errors="replace") as f:
                        content = f.read()
                    truncated = " (truncated)" if len(content) > 5000 else ""
                    return f"📄 {word} ({len(content)} chars){truncated}:\n\n{content[:5000]}"
                except PermissionError:
                    return f"Permission denied: {word}"
        return "No valid file path found in command. Usage: read <filepath>"

    def _write_file(self, command: str) -> str:
        """Write content to a file."""
        parts = command.split(maxsplit=2)
        if len(parts) >= 3:
            path, content = parts[1], parts[2]
            try:
                os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
                with open(path, "w") as f:
                    f.write(content)
                return f"✅ Written {len(content)} chars to {path}"
            except PermissionError:
                return f"Permission denied: {path}"
            except Exception as e:
                return f"Write error: {e}"
        return "Usage: write <filepath> <content>"

    def _search_files(self, command: str) -> str:
        """Search for files matching a glob pattern."""
        words = command.split()
        pattern = words[-1] if len(words) > 1 else "*"
        matches = glob.glob(f"**/{pattern}", recursive=True)

        if not matches:
            return f"No files matching '{pattern}' found."

        lines = [f"🔍 Found {len(matches)} match(es):"]
        for m in matches[:30]:
            lines.append(f"  • {m}")
        if len(matches) > 30:
            lines.append(f"  … and {len(matches) - 30} more")

        return "\n".join(lines)

    @staticmethod
    def _human_size(size: int) -> str:
        """Convert bytes to a human-readable string."""
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
