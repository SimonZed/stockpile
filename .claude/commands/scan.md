---
description: Scan an option chain for mispriced LEAPS (sell or buy candidates)
---

Run the options scanner for the provided ticker and any extra flags:
`$ARGUMENTS`.

Execute from the repo root:

```
uv run options-scanner/run_scanner.py $ARGUMENTS
```

Common flags: `--calls`, `--puts`, `--buy`, `--min-dte N`, `--max-dte N`,
`--min-oi N`, `--min-delta D`, `--max-delta D`, `--top N`, `--html`,
`--roll --type call --strike S --expiration YYYY-MM-DD`.

If `$ARGUMENTS` is empty, ask for a ticker before running. Show the
scanner's stdout to the user. If `--html` was passed, surface the
output path so they can open it.
