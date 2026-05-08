---
description: Scan every open stock position in a brokerage CSV
---

Run the portfolio scanner against the provided arguments: `$ARGUMENTS`.

Execute from the repo root:

```
uv run options-scanner/run_portfolio.py $ARGUMENTS
```

The portfolio scanner reads a brokerage CSV, finds open stock
positions, and runs a sell or roll scan per ticker. Required flag:
`--csv path/to/export.csv`. Optional: `--brokerage schwab|robinhood|fidelity|merrill`,
`--tickers AAPL AMD`, `--html`.

If `$ARGUMENTS` is empty or no `--csv` is given, list any CSVs in the
top-level `input/` directory and ask which to use before running.
