# Crypto Market Research Agent V3.1 Scoring Upgrade

V3.1 improves the V3.0 MVP scoring and backtesting logic.

## What changed from V3.0

```text
1. Added 3-period / 7-period rolling changes
2. Added rolling percentile ranking for OI, CVD, and volume changes
3. Split Daily and Weekly scoring logic
4. Made Daily signals more conservative
5. Reframed weak bearish signals as Risk-Off instead of direct bearish prediction
6. Strengthened Weekly Momentum Continuation rules
7. Added hit-rate and average return by bias/scenario/score bucket
```

## Current data source

The bot still uses your uploaded TradingView BTCUSDT CSV files.

```text
sample_data/BTCUSDT_1D.csv
sample_data/BTCUSDT_1W.csv
```

Current available metrics:

```text
OHLCV
RSI
Open Interest
CVD
```

Not yet included:

```text
ETF Flow
Exchange Netflow
Stablecoin Reserve
MVRV
SOPR
Active Addresses
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

```text
data/backtests/btc_daily_backtest_results.csv
data/backtests/btc_daily_backtest_summary.json

data/backtests/btc_weekly_backtest_results.csv
data/backtests/btc_weekly_backtest_summary.json
```

## V3.1 Interpretation

Daily signals are intentionally more conservative.

```text
Bullish = stronger upside condition
Bearish = stronger downside condition
Risk-Off = upside weakening / risk management condition
Neutral = no strong edge
```

Weekly signals focus more on momentum continuation and risk regime.

```text
Momentum Continuation = strong weekly trend with supportive CVD/positioning
Risk-Off = weak structure or deteriorating positioning, not necessarily a short signal
```
