# Crypto Market Research Agent V3.0 MVP

This is the first V3 MVP for a score-based crypto market research bot.

## Purpose

The bot reads historical BTC 1D / 1W CSV data, calculates market scores, generates scenarios, and backtests whether the scenarios matched future BTC price movement.

## Current Input Data

Included sample files:

```text
sample_data/BTCUSDT_1D.csv
sample_data/BTCUSDT_1W.csv
```

These files currently include:

```text
OHLCV
EMA columns
RSI
Open Interest
CVD
```

They do not yet include:

```text
ETF Flow
Exchange Netflow
Stablecoin Reserve
MVRV
SOPR
Active Addresses
```

Those will be added in later versions.

## Pipeline

```text
CSV Market Data
        ↓
Metric Calculation
        ↓
Metric Scoring
        ↓
Category Score Builder
        ↓
Scenario Engine
        ↓
Forward Return Backtest
        ↓
Performance Evaluation
```

## Run Daily Backtest

```powershell
python backtest.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv
```

## Run Weekly Backtest

```powershell
python backtest.py --timeframe weekly --csv sample_data/BTCUSDT_1W.csv
```

## Run Latest Report

```powershell
python main.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv
python main.py --timeframe weekly --csv sample_data/BTCUSDT_1W.csv
```

## Output

Backtest results:

```text
data/backtests/
```

Latest reports:

```text
data/reports/
```

## Current Score Categories

```text
Market Structure Score
Derivatives Positioning Score
CVD Flow Score
Final Score
```

## Future Expansion

V3.1:

```text
ETF / Institutional Flow Score
Exchange Flow Score
Stablecoin Liquidity Score
```

V3.2:

```text
MVRV / SOPR / NUPL
Active Addresses
Whale Behavior
Holder Behavior
```


---

# V3.3 ETF Flow Bridge

See:

```text
README_V3_3.md
```

Generate ETF-based extra metrics:

```powershell
python tools/build_extra_metrics_from_etf_csv.py --input sample_data/etf_flow_raw_template.csv --output sample_data/extra_metrics_from_etf.csv
```

Run backtest with ETF Flow:

```powershell
python backtest.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --extra-csv sample_data/extra_metrics_from_etf.csv
```


---

# V3.4 Threshold Calibration

See:

```text
README_V3_4.md
```

Optimize thresholds:

```powershell
python tools/optimize_thresholds.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv
```

Use best calibration:

```powershell
python backtest.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --calibration-json data/backtests/btc_daily_market_only_best_calibration.json
```


---

# V3.5 External Data Collectors

See `README_V3_5.md`.

```powershell
python tools/fetch_farside_etf_flow.py --output-raw sample_data/etf_flow_raw_farside.csv --output-extra sample_data/extra_metrics_from_farside.csv
python tools/fetch_defillama_stablecoins.py --output sample_data/extra_metrics_from_defillama_stablecoins.csv
python tools/merge_extra_metrics_csv.py --inputs sample_data/extra_metrics_from_farside.csv sample_data/extra_metrics_from_defillama_stablecoins.csv --output sample_data/extra_metrics_merged.csv
```


---

# V3.5.1 Farside 403 Fix

See:

```text
README_V3_5_1_FARSIDE_403_FIX.md
```

Retry Farside collector:

```powershell
python tools/fetch_farside_etf_flow.py --output-raw sample_data/etf_flow_raw_farside.csv --output-extra sample_data/extra_metrics_from_farside.csv
```

Manual fallback:

```powershell
python tools/build_extra_metrics_from_etf_csv.py --input sample_data/etf_flow_raw_manual.csv --output sample_data/extra_metrics_from_farside.csv
```


---

# V3.6 Signal Quality Upgrade

See:

```text
README_V3_6.md
```

Run calibrated ETF backtest:

```powershell
python backtest.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --extra-csv sample_data/extra_metrics_from_farside.csv --calibration-json sample_data/btc_daily_with_extra_best_calibration.json
```
