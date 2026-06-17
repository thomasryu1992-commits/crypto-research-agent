# V3.5.1 Farside 403 Fix

## Problem

When running:

```powershell
python tools/fetch_farside_etf_flow.py --output-raw sample_data/etf_flow_raw_farside.csv --output-extra sample_data/extra_metrics_from_farside.csv
```

You may get:

```text
HTTP Error 403: Forbidden
```

This means Farside is blocking automated Python access.

## Fix Applied

V3.5.1 changes the collector from:

```text
pandas.read_html(URL)
```

to:

```text
requests.get(URL, browser-like headers)
pandas.read_html(StringIO(html))
```

This makes the request look closer to a normal browser request.

## Try Again

```powershell
python tools/fetch_farside_etf_flow.py --output-raw sample_data/etf_flow_raw_farside.csv --output-extra sample_data/extra_metrics_from_farside.csv
```

## If 403 Still Happens

Some sites block server-side Python access even with browser headers.

Use the manual fallback:

1. Open the Farside BTC ETF Flow All Data page in your browser.
2. Copy the ETF flow table.
3. Paste it into Excel or Google Sheets.
4. Keep or rename columns like this:

```text
date
total_btc_etf_netflow
ibit_netflow
fbtc_netflow
gbtc_netflow
arkb_netflow
bitb_netflow
```

5. Save as:

```text
sample_data/etf_flow_raw_manual.csv
```

6. Run:

```powershell
python tools/build_extra_metrics_from_etf_csv.py --input sample_data/etf_flow_raw_manual.csv --output sample_data/extra_metrics_from_farside.csv
```

7. Backtest:

```powershell
python backtest.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --extra-csv sample_data/extra_metrics_from_farside.csv --calibration-json sample_data/btc_daily_market_only_best_calibration.json
```
