"""
main.py — CLI entry point for ELITE.
Run: python main.py
"""

import sys
from core.orchestrator import run_command

BANNER = r"""
  ███████╗██╗     ██╗████████╗███████╗
  ██╔════╝██║     ██║╚══██╔══╝██╔════╝
  █████╗  ██║     ██║   ██║   █████╗
  ██╔══╝  ██║     ██║   ██║   ██╔══╝
  ███████╗███████╗██║   ██║   ███████╗
  ╚══════╝╚══════╝╚═╝   ╚═╝   ╚══════╝
  AI Agent System v2.0  |  Ctrl+C to exit
"""

HELP = """
  Agents auto-selected based on your command:
  ┌──────────────┬────────────────────────────────────────────┐
  │  coder       │  write / code / script / program           │
  │  search      │  search / find / what is / who is          │
  │  file        │  file / read / list / directory            │
  │  system      │  cpu / ram / disk / status                 │
  │  telegram    │  alert / notify                            │
  │  orchestrator│  do / task / automate / smart              │
  │  llm         │  anything else → direct LLM answer         │
  └──────────────┴────────────────────────────────────────────┘
  Type 'help' to see this again.  Type 'exit' to quit.
"""


def main():
    print(BANNER)
    print(HELP)

    while True:
        try:
            cmd = input("ELITE >>> ").strip()
        except KeyboardInterrupt:
            print("\nGoodbye.")
            sys.exit(0)

        if not cmd:
            continue
        if cmd.lower() in ("exit", "quit", "q"):
            print("Goodbye.")
            break
        if cmd.lower() == "help":
            print(HELP)
            continue

        try:
            result = run_command(cmd)
            route  = result.get("route", "?").upper()
            text   = result.get("response", "")
            print(f"\n  [{route}]\n{text}\n")
        except Exception as e:
            print(f"\n  [ERROR] {e}\n")


if __name__ == "__main__":
    main()
