# Crypto Market Research Agent V3.6 Signal Quality Upgrade

V3.6 improves signal interpretation after ETF Flow integration.

## Why V3.6

V3.5 with ETF Flow improved the model:

```text
Bullish avg 7D return: -0.73% → +0.014%
Constructive avg 7D return: -1.06% → +0.38%
Direction Accuracy: 52.38% → 54.93%
Bearish avg 7D return: -3.08% → -3.41%
```

The key finding:

```text
Constructive was better than Bullish.
```

So V3.6 separates early upside candidates from confirmed bullish signals.

## Main changes

```text
1. Adds Signal Quality Grade
2. Makes Bullish stricter
3. Reframes Constructive as Early Upside Candidate
4. Adds ETF + CVD + OI + RSI confirmation logic
5. Adds signal_quality_summary to backtest summary
6. Adds signal quality section to latest report
```

## Signal Quality Grades

```text
A = High-quality upside setup
B = Constructive / early upside candidate
C = Positive but weak or incomplete confirmation
D = Risk-Off / upside weakening
F = Bearish / downside pressure
N = Neutral / no edge
```

## Run with ETF data

Fetch ETF Flow first:

```powershell
python tools/fetch_farside_etf_flow.py --output-raw sample_data/etf_flow_raw_farside.csv --output-extra sample_data/extra_metrics_from_farside.csv
```

Optimize thresholds with ETF data:

```powershell
python tools/optimize_thresholds.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --extra-csv sample_data/extra_metrics_from_farside.csv
```

Run calibrated backtest:

```powershell
python backtest.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --extra-csv sample_data/extra_metrics_from_farside.csv --calibration-json data/backtests/btc_daily_with_extra_best_calibration.json
```

## Files to send back after running

```text
btc_daily_with_extra_calibrated_backtest_summary.json
btc_daily_with_extra_calibrated_backtest_results.csv
```

## What to check

```text
signal_quality_summary.A.avg_forward_return
signal_quality_summary.B.avg_forward_return
signal_quality_summary.D.avg_forward_return
signal_quality_summary.F.avg_forward_return
```

Ideal result:

```text
A and B should outperform Neutral.
D and F should underperform Neutral.
```
