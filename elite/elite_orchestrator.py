"""
elite_orchestrator.py
Autonomous multi-step task runner:
  1. See  (screen)
  2. Plan (LLM)
  3. Do   (action agent)
  4. Report
"""

import json
import time
from datetime import datetime

from agents.screen_agent import describe_screen
from agents.coder_agent import write_and_run
from agents.action_agent import take_action, get_mouse_position
from alerts.telegram_bot import send_alert


class EliteOrchestrator:
    def __init__(self):
        self.history: list[dict] = []

    def smart_task(self, task: str) -> str:
        print(f"\n🧠 Smart task: '{task}'")
        send_alert(f"🧠 New task: {task}")

        # 1 ── EYES
        print("👁  1/4 Analysing screen...")
        screen_ctx = describe_screen()
        self.history.append({"ts": datetime.now().isoformat(), "screen": screen_ctx[:500]})

        # 2 ── BRAIN – plan
        print("🧠 2/4 Planning steps...")
        plan_prompt = (
            f'Screen context: "{screen_ctx[:400]}"\n'
            f'Task: "{task}"\n'
            'Write a Python script that prints ONLY a JSON object: '
            '{"steps": ["step1", "step2", "step3"]} — 3 concrete steps to complete the task.'
        )
        plan_output = write_and_run(plan_prompt)

        steps: list[str] = [task]
        try:
            parsed = json.loads(plan_output)
            steps = parsed.get("steps", [task])
        except Exception:
            pass  # keep default single-step fallback

        # 3 ── HANDS – execute
        print("🖱  3/4 Executing steps...")
        results = []
        for i, step in enumerate(steps[:3], 1):
            print(f"   Step {i}: {step}")
            ok = take_action(step)
            results.append(f"Step {i}: {'✅' if ok else '⚠️'} {step}")
            time.sleep(1)

        # 4 ── REPORT
        print("📊 4/4 Done!")
        pos = get_mouse_position()
        report = (
            f"Task '{task}' completed.\n"
            + "\n".join(results)
            + f"\nMouse at: {pos}"
        )
        send_alert(report)
        return report


# ── Module-level convenience ──────────────────────────────────────────
_orch = EliteOrchestrator()

def smart_task(task: str) -> str:
    return _orch.smart_task(task)
