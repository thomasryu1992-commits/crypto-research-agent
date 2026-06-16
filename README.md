# Crypto Research Agent V2

Python-based crypto trading research agent using Binance public data and Ollama local LLM.

## V2 Features

- Uses Ollama local LLM instead of OpenAI API
- Fetches BTC 24h spot market data
- Fetches BTC funding rate
- Fetches BTC open interest
- Fetches recent Binance Futures candles
- Saves market snapshots locally
- Calculates changes versus previous snapshot
- Generates trading-oriented report:
  - Market Bias
  - Futures Positioning
  - Long Scenario
  - Short Scenario
  - Invalidation
  - Risk Level
  - Trading Plan
- Saves reports to `data/reports/`
- Telegram sending is optional and disabled by default

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Install Ollama and pull a model:

```bash
ollama pull qwen2.5:3b
```

Run:

```bash
python main.py
```

## Environment

```text
DEFAULT_SYMBOL=BTCUSDT
REPORT_LANGUAGE=ko

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b

SEND_TELEGRAM=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

## GitHub Security

Never upload `.env`, API keys, wallet keys, or seed phrases.
