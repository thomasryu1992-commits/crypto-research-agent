# Crypto Research Agent V2.2

A Python-based crypto trading research agent using Binance public market data and Ollama local LLM.

## V2.2 Core Upgrade

V2.2 does not let the LLM make all trading judgments by itself.

Instead:

```text
Market data
→ Python rule engine
→ Structured market context
→ LLM report writer
→ Trading scenario report
```

This reduces logical conflicts such as:

- Saying "chasing is favorable" and later saying "avoid chasing"
- Mixing short entry scenario with short covering
- Making unsupported directional claims
- Inventing support/resistance levels

## Features

- Uses Ollama local LLM
- Fetches BTC 24h spot market data
- Fetches Binance Futures funding rate
- Fetches Binance Futures open interest
- Fetches recent 1H futures candles
- Saves market snapshots
- Calculates changes versus previous snapshot
- Adds Python-based market judgment:
  - market bias
  - positioning structure
  - chasing permission
  - long setup status
  - short setup status
  - risk level
  - invalidation logic
- Generates trading-oriented report:
  - Market Bias
  - Current Market Structure
  - Futures Positioning
  - Long Scenario
  - Short Scenario
  - Invalidation
  - Risk Level
  - Trading Plan
  - Key Checkpoints
- Telegram sending is optional and disabled by default

## Setup

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
```

Install Ollama model:

```powershell
ollama pull qwen2.5:3b
```

Run:

```powershell
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

## Important

This project generates trading research scenarios, not automatic buy/sell orders.
