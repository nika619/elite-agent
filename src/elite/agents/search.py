"""
elite.agents.search
Web search agent — DuckDuckGo search with AI-powered summarization.
"""

from __future__ import annotations

from elite.agents.base import BaseAgent
from elite.core.registry import AgentRegistry
from elite.core.llm import get_llm_client
from elite.core.exceptions import AgentError
from elite.config.settings import get_settings


def _ddg_search(query: str, max_results: int = 5) -> list[dict]:
    """Perform a DuckDuckGo search and return structured results."""
    try:
        from duckduckgo_search import DDGS

        results = []
        with DDGS() as ddg:
            for r in ddg.text(query, max_results=max_results):
                results.append(
                    {
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", ""),
                    }
                )
        return results
    except ImportError:
        return [
            {
                "title": "duckduckgo-search not installed",
                "url": "",
                "snippet": "pip install duckduckgo-search",
            }
        ]
    except Exception as e:
        return [{"title": "Search error", "url": "", "snippet": str(e)}]


@AgentRegistry.register("search")
class SearchAgent(BaseAgent):
    """Searches the web and provides AI-summarized results."""

    @property
    def name(self) -> str:
        return "search"

    @property
    def description(self) -> str:
        return "Web search via DuckDuckGo with AI-powered summarization"

    def execute(self, command: str) -> str:
        settings = get_settings()
        client = get_llm_client()

        self.logger.info("Search query: %s", command[:100])

        results = _ddg_search(command, max_results=settings.search_max_results)
        if not results:
            return "No search results found."

        # Format raw results
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r['title']}\n   {r['url']}\n   {r['snippet']}\n")

        # Generate AI summary
        snippets = "\n".join(
            f"{i+1}. {r['title']}: {r['snippet']}" for i, r in enumerate(results)
        )
        prompt = (
            f"The user searched for: {command}\n\n"
            f"Search snippets:\n{snippets}\n\n"
            "Summarize the key information in 3-5 clear sentences."
        )

        try:
            summary = client.generate(prompt)
        except Exception as e:
            self.logger.error("Summary generation failed: %s", e)
            summary = f"Summary unavailable: {e}"

        return f"── AI Summary ──\n{summary}\n\n── Sources ──\n" + "\n".join(lines)
