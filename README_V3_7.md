# Crypto Market Research Agent V3.7 Signal Timing Calibration

V3.7 improves the signal grading system after the V3.6.1 result showed that C-grade signals outperformed A-grade signals.

## Why V3.7

V3.6.1 result:

```text
A / High-Quality Upside Setup:
avg 7D return +0.596%

C / Constructive but Incomplete:
avg 7D return +0.909%
```

This does not necessarily mean A is bad.

It likely means:

```text
A = more confirmed, but later
C = less confirmed, but earlier
```

So V3.7 separates:

```text
Signal Quality
Signal Timing
```

## New concept

```text
Signal Quality:
A = high-quality upside
B = constructive upside
C = weak/incomplete positive setup
D = risk-off
F = bearish
N = neutral

Signal Timing:
Early = early upside candidate
Confirmed = confirmed trend setup
Late = possible late/overheated setup
Risk-Off = upside weakening
Bearish = downside pressure
Neutral = no edge
```

## New fields in backtest result

```text
signal_quality
signal_quality_label
signal_timing
signal_timing_label
confirmation_count
warning_count
signal_reasons
```

## New summary fields

```text
signal_quality_summary
signal_timing_summary
signal_timing_label_summary
```

## Run ETF backtest with calibration

```powershell
python backtest.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --extra-csv sample_data/extra_metrics_from_farside.csv --calibration-json sample_data/btc_daily_with_extra_best_calibration.json
```

## Analyze signal timing

After running backtest, run:

```powershell
python tools/analyze_signal_quality.py --results data/backtests/btc_daily_with_extra_calibrated_backtest_results.csv --window 7
```

This creates:

```text
data/backtests/signal_quality_analysis.json
```

## What to check

```text
signal_timing_summary.Early.avg_forward_return
signal_timing_summary.Confirmed.avg_forward_return
signal_timing_summary.Late.avg_forward_return
signal_timing_summary.Risk-Off.avg_forward_return
signal_timing_summary.Bearish.avg_forward_return
```

Ideal structure:

```text
Early / Confirmed > Neutral
Risk-Off / Bearish < Neutral
Late should not be chased
```
