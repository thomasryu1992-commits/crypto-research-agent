# Crypto Research Agent

A Python-based crypto research AI agent that collects market data, analyzes BTC market conditions, generates a daily research report using an LLM, saves the report locally, and optionally sends it to Telegram.

## Features

- Fetch BTC spot price data from Binance
- Fetch BTC funding rate from Binance Futures
- Fetch BTC open interest from Binance Futures
- Generate a structured market research report using OpenAI
- Save reports to `data/reports/`
- Send reports to Telegram
- GitHub-safe environment variable setup

## Project Structure

```text
crypto-research-agent/
│
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
│
├── agents/
│   ├── __init__.py
│   ├── research_agent.py
│   ├── market_agent.py
│   └── report_agent.py
│
├── tools/
│   ├── __init__.py
│   ├── price_tool.py
│   ├── funding_tool.py
│   ├── oi_tool.py
│   └── telegram_tool.py
│
├── services/
│   ├── __init__.py
│   └── llm_service.py
│
├── memory/
│   ├── __init__.py
│   └── report_memory.py
│
├── prompts/
│   └── daily_report_prompt.txt
│
└── data/
    └── reports/
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/crypto-research-agent.git
cd crypto-research-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

Copy `.env.example` and rename it to `.env`.

Windows PowerShell:

```bash
copy .env.example .env
```

Mac/Linux:

```bash
cp .env.example .env
```

Then fill in your keys:

```text
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

Telegram settings are optional. If they are empty, the report will only be printed and saved locally.

## Run

```bash
python main.py
```

## GitHub Security Notes

Never upload these files or values to GitHub:

- `.env`
- OpenAI API key
- Telegram bot token
- Exchange API keys
- Wallet private key
- Seed phrase

This project currently uses public Binance endpoints, so no Binance API key is required.
