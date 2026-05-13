"""
tests/test_agents.py
Unit tests for agent registration and base functionality.
"""

import pytest


class TestAgentRegistry:
    """Test that all agents register correctly."""

    def setup_method(self):
        # Import agents to trigger registration
        import elite.agents  # noqa: F401
        import elite.orchestrator.engine  # noqa: F401
        from elite.core.registry import AgentRegistry
        self.registry = AgentRegistry

    def test_all_agents_registered(self):
        names = self.registry.names()
        expected = ["coder", "search", "filesystem", "system", "screen", "action", "orchestrator"]
        for agent in expected:
            assert agent in names, f"Agent '{agent}' not registered"

    def test_get_returns_class(self):
        cls = self.registry.get("coder")
        assert cls is not None
        assert hasattr(cls, "execute")

    def test_get_instance_returns_agent(self):
        agent = self.registry.get_instance("system")
        assert agent is not None
        assert agent.name == "system"

    def test_get_nonexistent_returns_none(self):
        assert self.registry.get("nonexistent_agent") is None
        assert self.registry.get_instance("nonexistent_agent") is None

    def test_list_agents_returns_dict(self):
        agents = self.registry.list_agents()
        assert isinstance(agents, dict)
        assert len(agents) >= 6


class TestBaseAgent:
    """Test the BaseAgent abstract contract."""

    def test_agent_has_required_properties(self):
        import elite.agents  # noqa: F401
        from elite.core.registry import AgentRegistry

        for name in AgentRegistry.names():
            agent = AgentRegistry.get_instance(name)
            assert hasattr(agent, "name"), f"{name} missing 'name'"
            assert hasattr(agent, "description"), f"{name} missing 'description'"
            assert hasattr(agent, "execute"), f"{name} missing 'execute'"
            assert isinstance(agent.name, str)
            assert isinstance(agent.description, str)
            assert len(agent.description) > 5, f"{name} description too short"


class TestSystemAgent:
    """Test the system agent (no external deps needed)."""

    def test_get_stats_returns_dict(self):
        from elite.agents.system import SystemAgent
        stats = SystemAgent.get_stats()
        assert isinstance(stats, dict)
        assert "cpu" in stats
        assert "ram_percent" in stats
        assert "disk_percent" in stats
        assert "hostname" in stats
        assert "os" in stats

    def test_get_stats_values_are_reasonable(self):
        from elite.agents.system import SystemAgent
        stats = SystemAgent.get_stats()
        assert 0 <= stats["cpu"] <= 100
        assert 0 <= stats["ram_percent"] <= 100
        assert 0 <= stats["disk_percent"] <= 100
        assert stats["ram_total"] > 0
        assert stats["disk_total"] > 0

    def test_execute_returns_string(self):
        import elite.agents  # noqa: F401
        from elite.core.registry import AgentRegistry
        agent = AgentRegistry.get_instance("system")
        result = agent.execute("show system status")
        assert isinstance(result, str)
        assert "CPU" in result
        assert "RAM" in result


class TestFilesystemAgent:
    """Test filesystem agent (safe operations only)."""

    def test_list_current_dir(self):
        import elite.agents  # noqa: F401
        from elite.core.registry import AgentRegistry
        agent = AgentRegistry.get_instance("filesystem")
        result = agent.execute("list files in current directory")
        assert isinstance(result, str)
        # Should contain the directory indicator
        assert "📁" in result or "empty" in result.lower()

    def test_unknown_command(self):
        import elite.agents  # noqa: F401
        from elite.core.registry import AgentRegistry
        agent = AgentRegistry.get_instance("filesystem")
        result = agent.execute("do something random with filesystem")
        assert "Unknown file command" in result or "Available operations" in result


class TestSettings:
    """Test configuration loading."""

    def test_default_settings(self):
        from elite.config.settings import EliteSettings
        s = EliteSettings()
        assert s.ollama_base_url == "http://localhost:11434"
        assert s.model_name == "deepseek-r1:7b"
        assert s.port == 5000

    def test_ollama_generate_url(self):
        from elite.config.settings import EliteSettings
        s = EliteSettings()
        assert s.ollama_generate_url == "http://localhost:11434/api/generate"

    def test_telegram_not_configured_by_default(self):
        from elite.config.settings import EliteSettings
        s = EliteSettings()
        assert s.telegram_configured is False


class TestExceptions:
    """Test the exception hierarchy."""

    def test_elite_error_is_base(self):
        from elite.core.exceptions import EliteError, LLMError, AgentError, RouterError
        assert issubclass(LLMError, EliteError)
        assert issubclass(AgentError, EliteError)
        assert issubclass(RouterError, EliteError)

    def test_agent_error_has_agent_name(self):
        from elite.core.exceptions import AgentError
        err = AgentError("test error", agent_name="coder")
        assert err.agent_name == "coder"
        assert str(err) == "test error"

    def test_elite_error_has_detail(self):
        from elite.core.exceptions import EliteError
        err = EliteError("msg", detail="extra info")
        assert err.detail == "extra info"
