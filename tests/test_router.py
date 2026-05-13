"""
tests/test_router.py
Unit tests for the intent classification router.
"""

import pytest
from elite.core.router import Router, RouteResult


class TestRouter:
    """Test suite for the Router intent classifier."""

    def setup_method(self):
        self.router = Router()

    # ── Coder routing ─────────────────────────────────────────────

    def test_routes_code_request_to_coder(self):
        result = self.router.classify("write a Python script to sort a list")
        assert result.agent_name == "coder"
        assert result.confidence > 0

    def test_routes_script_keyword_to_coder(self):
        result = self.router.classify("create a script that downloads images")
        assert result.agent_name == "coder"

    def test_routes_program_to_coder(self):
        result = self.router.classify("write a program to calculate fibonacci")
        assert result.agent_name == "coder"

    # ── Search routing ────────────────────────────────────────────

    def test_routes_search_to_search_agent(self):
        result = self.router.classify("search for latest Python news")
        assert result.agent_name == "search"

    def test_routes_what_is_to_search(self):
        result = self.router.classify("what is machine learning")
        assert result.agent_name == "search"

    def test_routes_who_is_to_search(self):
        result = self.router.classify("who is Elon Musk")
        assert result.agent_name == "search"

    # ── Filesystem routing ────────────────────────────────────────

    def test_routes_list_files_to_filesystem(self):
        result = self.router.classify("list files in the current directory")
        assert result.agent_name == "filesystem"

    def test_routes_read_file_to_filesystem(self):
        result = self.router.classify("read file config.py")
        assert result.agent_name == "filesystem"

    # ── System routing ────────────────────────────────────────────

    def test_routes_cpu_to_system(self):
        result = self.router.classify("show cpu usage")
        assert result.agent_name == "system"

    def test_routes_system_status_to_system(self):
        result = self.router.classify("system status")
        assert result.agent_name == "system"

    def test_routes_ram_to_system(self):
        result = self.router.classify("how much ram is being used")
        assert result.agent_name == "system"

    # ── Telegram routing ──────────────────────────────────────────

    def test_routes_alert_to_telegram(self):
        result = self.router.classify("send alert server is down")
        assert result.agent_name == "telegram"

    def test_routes_notify_to_telegram(self):
        result = self.router.classify("notify me when done")
        assert result.agent_name == "telegram"

    # ── LLM fallback ─────────────────────────────────────────────

    def test_routes_ambiguous_to_llm(self):
        result = self.router.classify("hello how are you")
        assert result.agent_name == "llm"
        assert result.confidence == 0.0

    def test_routes_random_to_llm(self):
        result = self.router.classify("explain quantum mechanics")
        assert result.agent_name == "llm"

    # ── Route result structure ────────────────────────────────────

    def test_route_result_has_all_fields(self):
        result = self.router.classify("write code for a calculator")
        assert isinstance(result, RouteResult)
        assert isinstance(result.agent_name, str)
        assert isinstance(result.confidence, float)
        assert isinstance(result.matched_keywords, list)

    def test_confidence_is_normalized(self):
        result = self.router.classify("write a Python script to sort data")
        assert 0.0 <= result.confidence <= 1.0

    def test_matched_keywords_populated(self):
        result = self.router.classify("search for the latest news")
        assert len(result.matched_keywords) > 0
        assert "search" in result.matched_keywords or "search for" in result.matched_keywords
