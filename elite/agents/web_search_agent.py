"""
agents/web_search_agent.py
DuckDuckGo search + AI summary via Ollama.
"""

import requests
from config import OLLAMA_URL, MODEL_NAME, MAX_SEARCH_RESULTS


def _ddg_search(query: str) -> list[dict]:
    """Hit DuckDuckGo Lite and return a list of {title, url, snippet}."""
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddg:
            for r in ddg.text(query, max_results=MAX_SEARCH_RESULTS):
                results.append({
                    "title":   r.get("title", ""),
                    "url":     r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
        return results
    except ImportError:
        return [{"title": "duckduckgo-search not installed",
                 "url": "", "snippet": "pip install duckduckgo-search"}]
    except Exception as e:
        return [{"title": "Search error", "url": "", "snippet": str(e)}]


def _summarize(query: str, results: list[dict]) -> str:
    snippets = "\n".join(
        f"{i+1}. {r['title']}: {r['snippet']}" for i, r in enumerate(results)
    )
    prompt = (
        f"The user searched for: {query}\n\n"
        f"Search snippets:\n{snippets}\n\n"
        "Summarize the key information in 3-5 clear sentences."
    )
    try:
        r = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=90,
        )
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"Summary unavailable: {e}"


def search_web(query: str) -> str:
    results = _ddg_search(query)
    if not results:
        return "No results found."

    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']}\n   {r['url']}\n   {r['snippet']}\n")

    summary = _summarize(query, results)
    return "── AI Summary ──\n" + summary + "\n\n── Sources ──\n" + "\n".join(lines)
