# Crypto Market Research Agent V3.4 Threshold Calibration

V3.4 adds a threshold optimizer.

## Purpose

Daily 7D forward return was still weak in V3.1~V3.3.  
V3.4 lets the bot test many threshold combinations and find which classification rules worked better historically.

## New files

```text
core/calibration_loader.py
backtesting/threshold_optimizer.py
tools/optimize_thresholds.py
calibration/default_calibration.json
README_V3_4.md
```

## Run Daily Threshold Optimization

```powershell
python tools/optimize_thresholds.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv
```

## Run Weekly Threshold Optimization

```powershell
python tools/optimize_thresholds.py --timeframe weekly --csv sample_data/BTCUSDT_1W.csv
```

## Run With ETF Extra CSV

```powershell
python tools/optimize_thresholds.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --extra-csv sample_data/extra_metrics_from_etf.csv
```

## Output

```text
data/backtests/btc_daily_market_only_threshold_optimization.csv
data/backtests/btc_daily_market_only_best_calibration.json

data/backtests/btc_weekly_market_only_threshold_optimization.csv
data/backtests/btc_weekly_market_only_best_calibration.json
```

## Use Best Calibration in Backtest

```powershell
python backtest.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --calibration-json data/backtests/btc_daily_market_only_best_calibration.json
```

## Use Best Calibration in Latest Report

```powershell
python main.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --calibration-json data/backtests/btc_daily_market_only_best_calibration.json
```

## Warning

Threshold optimization can overfit.  
Use it as a research tool, not as final proof.
