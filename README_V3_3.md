# Crypto Market Research Agent V3.3 ETF Flow Bridge

V3.3 adds a practical ETF Flow data bridge.

## Why this version matters

V3.1 and V3.2 showed that BTC price/OI/CVD alone is not enough for strong Daily 7D forward return performance.

V3.3 focuses on the most important missing data layer:

```text
ETF / Institutional Flow
```

## What V3.3 does

V3.3 converts raw BTC ETF flow data into the `extra_metrics.csv` format used by the V3.2 scoring engine.

```text
ETF Raw CSV
        ↓
ETF Flow Transformer
        ↓
extra_metrics_from_etf.csv
        ↓
V3.2 Backtest Engine
        ↓
Daily / Weekly Backtest
```

## Input file

Use this template:

```text
sample_data/etf_flow_raw_template.csv
```

Required columns:

```text
date
total_btc_etf_netflow
ibit_netflow
```

Optional columns:

```text
fbtc_netflow
gbtc_netflow
arkb_netflow
bitb_netflow
btco_netflow
hodl_netflow
brk_netflow
ezbc_netflow
btc_netflow
```

Values should be in USD.

Examples:

```text
250000000
-120000000
0
```

## Generate extra metrics from ETF raw CSV

```powershell
python tools/build_extra_metrics_from_etf_csv.py --input sample_data/etf_flow_raw_template.csv --output sample_data/extra_metrics_from_etf.csv
```

## Run Daily Backtest with ETF Flow

```powershell
python backtest.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --extra-csv sample_data/extra_metrics_from_etf.csv
```

## Run Weekly Backtest with ETF Flow

```powershell
python backtest.py --timeframe weekly --csv sample_data/BTCUSDT_1W.csv --extra-csv sample_data/extra_metrics_from_etf.csv
```

## Run Latest Report with ETF Flow

```powershell
python main.py --timeframe daily --csv sample_data/BTCUSDT_1D.csv --extra-csv sample_data/extra_metrics_from_etf.csv
```

## Output columns

The transformer generates:

```text
date
total_btc_etf_netflow
ibit_netflow
etf_5d_netflow
etf_consecutive_inflow_days
etf_consecutive_outflow_days
```

It also preserves blank columns for future metrics:

```text
exchange_netflow
exchange_reserve
stablecoin_supply
stablecoin_exchange_reserve
mvrv
sopr
active_addresses
tx_count
```

## Interpretation

```text
Positive total_btc_etf_netflow
→ institutional inflow

Negative total_btc_etf_netflow
→ institutional outflow

Positive etf_5d_netflow
→ sustained institutional demand

Negative etf_5d_netflow
→ sustained institutional outflow

Consecutive inflow days >= 3
→ stronger institutional accumulation signal

Consecutive outflow days >= 3
→ stronger institutional risk-off signal
```

## Next step after V3.3

After ETF Flow is tested, V3.4 should add:

```text
Exchange Flow Bridge
- exchange_netflow
- exchange_reserve

Stablecoin Liquidity Bridge
- stablecoin_supply
- stablecoin_exchange_reserve
```
