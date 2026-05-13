# 🤖 ELITE AI Agent v2.0 — Enterprise Edition

> Fully local, autonomous AI agent system powered by **DeepSeek-R1 + Ollama**.
> Enterprise-grade architecture with proper separation of concerns, structured logging, and a plugin-based agent system.

---

## ⚡ Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/elite-v2.git
cd elite-v2

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/macOS

# 3. Install dependencies
pip install -e .

# 4. Pull the LLM model (requires Ollama)
ollama pull deepseek-r1:7b

# 5. Copy environment config
copy .env.example .env     # Windows
# cp .env.example .env     # Linux/macOS

# 6. Run!
elite              # CLI mode
elite --web        # Web UI mode (http://localhost:5000)
```

---

## 📁 Architecture

```
elite_v2/
├── .env.example              ← Environment template (never commit .env)
├── .gitignore
├── pyproject.toml            ← Modern Python packaging + tool config
├── requirements.txt
│
├── src/elite/                ← Source package
│   ├── config/
│   │   └── settings.py       ← Pydantic Settings (env-driven, validated)
│   │
│   ├── core/
│   │   ├── llm.py            ← Ollama client (connection pooling, retries)
│   │   ├── router.py         ← Weighted keyword intent classifier
│   │   ├── registry.py       ← Self-registering agent plugin system
│   │   └── exceptions.py     ← Typed exception hierarchy
│   │
│   ├── agents/
│   │   ├── base.py           ← Abstract base agent (enforced interface)
│   │   ├── coder.py          ← Code generation + sandboxed execution
│   │   ├── search.py         ← DuckDuckGo + AI summarization
│   │   ├── filesystem.py     ← File read/write/list/search
│   │   ├── system.py         ← CPU/RAM/Disk monitoring
│   │   ├── screen.py         ← Screen capture + OCR
│   │   └── action.py         ← Mouse/keyboard automation
│   │
│   ├── orchestrator/
│   │   └── engine.py         ← Multi-step autonomous task runner
│   │
│   ├── integrations/
│   │   └── telegram.py       ← Push notifications
│   │
│   ├── api/
│   │   ├── app.py            ← Flask app factory pattern
│   │   ├── routes.py         ← REST API endpoints
│   │   └── middleware.py     ← Error handling, CORS, request logging
│   │
│   ├── cli/
│   │   └── repl.py           ← Rich-powered interactive CLI
│   │
│   └── utils/
│       └── logging.py        ← Structured logging (text + JSON)
│
├── templates/
│   └── index.html            ← Premium web UI
│
├── tests/
│   ├── conftest.py
│   ├── test_router.py
│   └── test_agents.py
│
└── elite/                    ← (legacy v1 — can be removed)
```

---

## 🧠 How Routing Works

The router uses **weighted keyword scoring** with confidence thresholds:

| Agent         | Trigger Keywords                              |
|---------------|-----------------------------------------------|
| `coder`       | write code / script / program / implement     |
| `search`      | search / find / what is / who is / google     |
| `filesystem`  | file / read / list / directory / folder       |
| `system`      | cpu / ram / disk / status / system            |
| `telegram`    | alert / notify / telegram                     |
| `orchestrator`| smart task / automate / autonomous            |
| `llm`         | anything else → direct LLM response           |

Each keyword has a weight. The agent with the highest normalized score above the confidence threshold wins. Below threshold → direct LLM fallback.

---

## 🔧 Configuration

All settings are environment-driven via **Pydantic Settings**. No hardcoded secrets.

| Env Variable                | Default                    | Description                    |
|-----------------------------|----------------------------|--------------------------------|
| `ELITE_OLLAMA_BASE_URL`     | `http://localhost:11434`   | Ollama server URL              |
| `ELITE_MODEL_NAME`          | `deepseek-r1:7b`          | Ollama model identifier        |
| `ELITE_PORT`                | `5000`                     | Web UI port                    |
| `ELITE_TELEGRAM_BOT_TOKEN`  | *(empty)*                  | Telegram bot token             |
| `ELITE_TELEGRAM_CHAT_ID`    | *(empty)*                  | Telegram chat ID               |
| `ELITE_CODER_MAX_RETRIES`   | `10`                       | Max code generation retries    |
| `ELITE_LOG_LEVEL`           | `INFO`                     | Logging level                  |
| `ELITE_LOG_FORMAT`          | `text`                     | `text` or `json`               |

---

## 🧪 Testing

```bash
pip install -e ".[dev]"
pytest
```

---

## 📡 REST API

| Endpoint        | Method | Description                     |
|-----------------|--------|---------------------------------|
| `/`             | GET    | Web UI                          |
| `/api/chat`     | POST   | Send command, get routed response |
| `/api/status`   | GET    | Live system stats               |
| `/api/health`   | GET    | Health check + agent registry   |
| `/api/agents`   | GET    | List all registered agents      |
| `/api/coder`    | POST   | Direct coder agent endpoint     |
| `/api/screen`   | GET    | Screen capture + OCR            |

---

## 🏗 Design Principles

1. **Zero hardcoded secrets** — everything via `.env` + Pydantic validation
2. **Plugin architecture** — agents self-register via `@AgentRegistry.register`
3. **Structured logging** — zero `print()`, proper `logging` with JSON option
4. **Typed exceptions** — `EliteError` → `LLMError`, `AgentError`, `RouterError`
5. **Graceful degradation** — optional agents fail silently with install hints
6. **App factory pattern** — `create_app()` for testable Flask instances
7. **Connection pooling** — `requests.Session` with retry policies for Ollama

---

## 🛠 Built With

Python · Flask · Ollama · DeepSeek-R1 · Pydantic · Rich · DuckDuckGo Search · psutil

---

## 👤 Author

**Mayank Tiwari** — ELITE AI Agent System v2.0
