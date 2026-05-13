"""
elite.core.llm
Ollama LLM client with connection pooling, retry logic,
and structured error handling.
"""

from __future__ import annotations

import logging
from functools import lru_cache

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from elite.config.settings import get_settings
from elite.core.exceptions import LLMError

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Production-grade Ollama client.

    Features:
    - Connection pooling via requests.Session
    - Automatic retries on transient failures
    - Structured logging of every call
    - Clean error propagation via LLMError
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
    ):
        settings = get_settings()
        self._base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self._model = model or settings.model_name
        self._timeout = timeout or settings.llm_timeout
        self._generate_url = f"{self._base_url}/api/generate"

        # ── Session with retry policy ─────────────────────────────
        self._session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[502, 503, 504],
            allowed_methods=["POST"],
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=5,
            pool_maxsize=10,
        )
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        logger.info(
            "OllamaClient initialized",
            extra={"model": self._model, "base_url": self._base_url},
        )

    @property
    def model(self) -> str:
        return self._model

    def generate(
        self,
        prompt: str,
        *,
        model: str | None = None,
        system: str | None = None,
        temperature: float | None = None,
        stream: bool = False,
    ) -> str:
        """
        Send a prompt to Ollama and return the response text.

        Args:
            prompt: The user prompt.
            model: Override the default model for this call.
            system: Optional system prompt.
            temperature: Sampling temperature (0.0–2.0).
            stream: Whether to stream (not implemented yet).

        Returns:
            The model's response text.

        Raises:
            LLMError: On any failure communicating with Ollama.
        """
        payload: dict = {
            "model": model or self._model,
            "prompt": prompt,
            "stream": stream,
        }
        if system:
            payload["system"] = system
        if temperature is not None:
            payload["options"] = {"temperature": temperature}

        logger.debug(
            "LLM request",
            extra={"model": payload["model"], "prompt_len": len(prompt)},
        )

        try:
            response = self._session.post(
                self._generate_url,
                json=payload,
                timeout=self._timeout,
            )
            response.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            raise LLMError(
                "Cannot connect to Ollama. Is it running?",
                detail=f"URL: {self._generate_url}, Error: {e}",
            ) from e
        except requests.exceptions.Timeout as e:
            raise LLMError(
                f"Ollama request timed out after {self._timeout}s",
                detail=str(e),
            ) from e
        except requests.exceptions.HTTPError as e:
            raise LLMError(
                f"Ollama returned HTTP {response.status_code}",
                detail=response.text[:500],
            ) from e

        try:
            data = response.json()
        except ValueError as e:
            raise LLMError(
                "Ollama returned invalid JSON",
                detail=response.text[:500],
            ) from e

        text = data.get("response", "").strip()
        logger.debug(
            "LLM response",
            extra={"response_len": len(text), "model": payload["model"]},
        )
        return text

    def is_healthy(self) -> bool:
        """Check if Ollama is reachable and the model is available."""
        try:
            r = self._session.get(f"{self._base_url}/api/tags", timeout=5)
            if not r.ok:
                return False
            models = [m.get("name", "") for m in r.json().get("models", [])]
            return any(self._model in m for m in models)
        except Exception:
            return False

    def close(self) -> None:
        """Close the underlying session."""
        self._session.close()


@lru_cache(maxsize=1)
def get_llm_client() -> OllamaClient:
    """Return a cached singleton LLM client."""
    return OllamaClient()
