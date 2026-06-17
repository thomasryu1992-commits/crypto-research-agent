# Crypto Market Research Agent V3.5 External Data Collectors

V3.5 adds external data collectors for ETF flow and stablecoin liquidity.

## New files

```text
collectors/farside_etf_collector.py
collectors/defillama_stablecoin_collector.py
tools/fetch_farside_etf_flow.py
tools/fetch_defillama_stablecoins.py
tools/merge_extra_metrics_csv.py
README_V3_5.md
```

## Install

```powershell
pip install -r requirements.txt
```

## Fetch Farside BTC ETF Flow

```powershell
python tools/fetch_farside_etf_flow.py --output-raw sample_data/etf_flow_raw_farside.csv --output-extra sample_data/extra_metrics_from_farside.csv
```

## Fetch DefiLlama Stablecoin Supply

```powershell
python tools/fetch_defillama_stablecoins.py --output sample_data/extra_metrics_from_defillama_stablecoins.csv
```

## Merge External Metrics

```powershell
python tools/merge_extra_metrics_csv.py --inputs sample_data/extra_metrics_from_farside.csv sample_data/extra_metrics_from_defillama_stablecoins.csv --output sample_data/extra_metrics_merged.csv
```

## Run Daily Backtest With External Data + Calibration

```powershell
python backtest.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --extra-csv sample_data/extra_metrics_merged.csv --calibration-json sample_data/btc_daily_market_only_best_calibration.json
```

## Re-optimize With External Data

```powershell
python tools/optimize_thresholds.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --extra-csv sample_data/extra_metrics_from_farside.csv
```

Then run:

```powershell
python backtest.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --extra-csv sample_data/extra_metrics_from_farside.csv --calibration-json data/backtests/btc_daily_with_extra_best_calibration.json
```

## Notes

- Farside data is shown in US$m. This collector converts it to USD.
- DefiLlama stablecoin collector currently creates a latest-date row.
- ETF flow is useful for historical backtests.
- Stablecoin latest data is more useful for latest reports unless historical rows are provided.
