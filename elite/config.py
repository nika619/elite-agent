# ─────────────────────────────────────────────
#  ELITE AI Agent System — Global Config
#  Author : Mayank Tiwari | Version: 2.0.0
# ─────────────────────────────────────────────

# ── Ollama / DeepSeek ─────────────────────────
OLLAMA_URL    = "http://localhost:11434/api/generate"
OLLAMA_BASE   = "http://localhost:11434"
MODEL_NAME    = "deepseek-r1:7b"

# ── Flask ─────────────────────────────────────
FLASK_HOST    = "0.0.0.0"
FLASK_PORT    = 5000
FLASK_DEBUG   = False

# ── Telegram Bot ──────────────────────────────
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID   = "YOUR_CHAT_ID_HERE"

# ── Coder Agent ───────────────────────────────
MAX_RETRIES       = 999          # infinite until Ctrl+C
CODE_SAVE_DIR     = "./generated_scripts"

# ── Web Search ────────────────────────────────
MAX_SEARCH_RESULTS = 5

# ── Stats ─────────────────────────────────────
STATS_INTERVAL    = 3
