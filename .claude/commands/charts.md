---
description: Generate interactive cost-basis-vs-price charts from a brokerage CSV
---

Run the cost-basis charts generator with the provided arguments:
`$ARGUMENTS`.

Execute from the repo root:

```
uv run cost-basis-charts/run_charts.py $ARGUMENTS
```

Common flags: `--symbol TICKER` (single symbol only), `--csv FILE`
(override config), `--brokerage schwab|robinhood|fidelity|merrill`,
`--output-dir DIR`, `--png` (also write static PNGs).

Without flags it uses `cost-basis-charts/config.toml`. If that file
doesn't exist, point the user at `config.toml.example` and ask them
to copy it before running. Show the output path of generated charts.
