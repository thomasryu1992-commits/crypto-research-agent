# Crypto Market Research Agent V3.6.1 Clean Package

This is a clean rebuild with no Git merge conflict artifacts.

## Included

```text
V3.5.1 Farside 403 Fix
V3.6 Signal Quality Upgrade
Clean config.py
Clean .gitignore
Clean requirements.txt
```

## First install

```powershell
pip install -r requirements.txt
```

## Fetch ETF Flow

```powershell
python tools/fetch_farside_etf_flow.py --output-raw sample_data/etf_flow_raw_farside.csv --output-extra sample_data/extra_metrics_from_farside.csv
```

## Run Daily Backtest With ETF Flow + Calibration

```powershell
python backtest.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --extra-csv sample_data/extra_metrics_from_farside.csv --calibration-json sample_data/btc_daily_with_extra_best_calibration.json
```

## If calibration file is missing

```powershell
python tools/optimize_thresholds.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --extra-csv sample_data/extra_metrics_from_farside.csv
```

Then run:

```powershell
python backtest.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --extra-csv sample_data/extra_metrics_from_farside.csv --calibration-json data/backtests/btc_daily_with_extra_best_calibration.json
```
