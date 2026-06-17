# Crypto Market Research Agent V3.2 Data Expansion

V3.2 adds external market research data support.

## Main Upgrade

V3.1 used only:

```text
BTC OHLCV
RSI
Open Interest
CVD
```

V3.2 adds optional external metrics via CSV:

```text
ETF / Institutional Flow
Exchange Flow
Stablecoin Liquidity
Valuation / Cycle
Network Activity
```

## Pipeline

```text
BTC TradingView CSV
        +
External Metrics CSV
        ↓
Date-based merge
        ↓
Feature builder
        ↓
Category scoring
        ↓
Scenario engine
        ↓
Backtest
```

## Required market CSV

```text
sample_data/BTCUSDT_1D.csv
sample_data/BTCUSDT_1W.csv
```

## Optional external metrics CSV

Template:

```text
sample_data/extra_metrics_template.csv
```

Supported columns:

```text
date

total_btc_etf_netflow
ibit_netflow
etf_5d_netflow
etf_consecutive_inflow_days
etf_consecutive_outflow_days

exchange_netflow
exchange_reserve

stablecoin_supply
stablecoin_exchange_reserve

mvrv
sopr

active_addresses
tx_count
```

If a column is missing or empty, the score defaults to neutral for that metric.

## Run Daily Backtest without extra metrics

```powershell
python backtest.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv
```

## Run Daily Backtest with extra metrics

```powershell
python backtest.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --extra-csv sample_data/extra_metrics_template.csv
```

## Run Weekly Backtest with extra metrics

```powershell
python backtest.py --timeframe weekly --csv sample_data/BTCUSDT_1W.csv --extra-csv sample_data/extra_metrics_template.csv
```

## Run Latest Report

```powershell
python main.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --extra-csv sample_data/extra_metrics_template.csv
```

## V3.2 Score Categories

```text
Market Structure Score
Derivatives Positioning Score
CVD Flow Score
Volume Score
ETF / Institutional Flow Score
Exchange Flow Score
Stablecoin Liquidity Score
Valuation / Cycle Score
Network Activity Score
Final Score
```

## Important

V3.2 does not require paid APIs yet.

The reason is intentional:

```text
1. Backtesting needs historical data.
2. Historical ETF/on-chain data often comes from different providers.
3. CSV ingestion lets us test the scoring logic first.
4. API collectors can be added after the scoring and backtesting structure is validated.
```

## Next Version

V3.3 can add real collectors:

```text
Farside / SoSoValue ETF collector
DefiLlama stablecoin collector
Glassnode / CryptoQuant CSV/API bridge
Dune query exporter
```
