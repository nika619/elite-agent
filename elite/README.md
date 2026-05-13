# 🤖 ELITE AI Agent v2.0

A fully local, autonomous AI agent system powered by **DeepSeek-R1:7B + Ollama**.

---

## 📁 Project Structure

```
elite/
├── main.py               ← CLI entry point
├── app.py                ← Flask web UI
├── config.py             ← All settings in one place
├── elite_orchestrator.py ← Smart multi-step task runner
│
├── core/
│   └── orchestrator.py   ← Routes commands to agents
│
├── agents/
│   ├── coder_agent.py    ← Writes & runs Python (auto-retry)
│   ├── web_search_agent.py ← DuckDuckGo + AI summary
│   ├── file_agent.py     ← Read / write / list / search files
│   ├── system_agent.py   ← CPU / RAM / Disk stats
│   ├── screen_agent.py   ← Screen capture + OCR
│   └── action_agent.py   ← Mouse / keyboard automation
│
├── alerts/
│   └── telegram_bot.py   ← Send Telegram alerts
│
└── templates/
    └── index.html        ← Web chat UI
```

---

## ⚡ Setup

```bash
# 1. Clone / copy the project
cd elite

# 2. Install Python deps
pip install -r requirements.txt

# 3. Pull the model (needs Ollama installed)
ollama pull deepseek-r1:7b

# 4. (Optional) Set Telegram credentials in config.py
```

---

## 🚀 Run

**CLI mode:**
```bash
python main.py
```

**Web UI mode:**
```bash
python app.py
# then open http://localhost:5000
```

---

## 🧠 How commands are routed

| You say…                        | Agent        |
|---------------------------------|--------------|
| write / code / script / program | coder        |
| search / find / what is         | web_search   |
| file / read / list / directory  | file         |
| cpu / ram / disk / status       | system       |
| alert / notify / telegram       | telegram     |
| do / task / automate / smart    | orchestrator |
| anything else                   | direct LLM   |

---

## ⚙️ Config (`config.py`)

| Key                  | Default                           | Description               |
|----------------------|-----------------------------------|---------------------------|
| `MODEL_NAME`         | `deepseek-r1:7b`                  | Ollama model              |
| `OLLAMA_URL`         | `http://localhost:11434/api/generate` | Ollama endpoint       |
| `FLASK_PORT`         | `5000`                            | Web UI port               |
| `MAX_RETRIES`        | `999`                             | Coder auto-retry limit    |
| `TELEGRAM_BOT_TOKEN` | `YOUR_BOT_TOKEN_HERE`             | Set to enable alerts      |
| `MAX_SEARCH_RESULTS` | `5`                               | Web search result count   |

---

## 🛠 Built With

Python · Flask · Ollama · DeepSeek-R1 · DuckDuckGo Search · psutil · PyAutoGUI · pytesseract
