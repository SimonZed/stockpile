# CLAUDE.md — stockpile

Claude Code instructions for this monorepo.

## Running the tools

Always run from the **repo root** using `uv run`. Never use `python`
or `python3` directly.

### Positions tracker (Google Sheets)

```bash
uv run positions/run_tracker.py
uv run positions/run_tracker.py --brokerage schwab
uv run positions/run_tracker.py --csv input/OTHER.csv
```

Reads `positions/config.toml` (account sheet IDs + CSV paths).
Credentials at `~/.config/google-sheets-oauth.json`. First run opens
a browser for OAuth; subsequent runs are silent.

### Cost basis charts

```bash
uv run cost-basis-charts/run_charts.py
uv run cost-basis-charts/run_charts.py --symbol SCHW
```

Reads `cost-basis-charts/config.toml`. Writes HTML (and optional PNG)
to `cost-basis-charts/output/`.

### Options scanner — web UI (recommended)

```bash
uv run streamlit run options-scanner/run_app.py
```

Opens at `http://localhost:8501`. Single Ticker tab or Portfolio tab
(drag in a brokerage CSV).

### Options scanner — CLI (single ticker)

```bash
uv run options-scanner/run_scanner.py AMD --calls
uv run options-scanner/run_scanner.py AMD --puts
uv run options-scanner/run_scanner.py AMD
uv run options-scanner/run_scanner.py AMD --roll \
    --type call --strike 600 --expiration 2026-01-16
```

### Options scanner — portfolio (brokerage CSV)

```bash
uv run options-scanner/run_portfolio.py --csv input/schwab028.csv
uv run options-scanner/run_portfolio.py --csv input/schwab028.csv \
    --html --tickers AAPL AMD
```

## Project structure

- `shared/` — pip-installable `stocks-shared` package: CSV parsers,
  Yahoo Finance helpers, FIFO analysis, Black-Scholes pricing
- `positions/` — Google Sheets position tracker
- `cost-basis-charts/` — cost basis vs. price charts
- `options-scanner/` — LEAPS scanner (web UI + CLI)
- `google-sheets-setup/` — Google Sheets API setup docs
- `input/` — brokerage CSV exports (gitignored)

## Slash commands

Inside a Claude Code session, `/` shows available project commands:

| Command | What it does |
|---------|--------------|
| `/scan TICKER [flags]` | Options scanner CLI for one ticker |
| `/scan-portfolio --csv FILE` | Scan every open position in a CSV |
| `/scan-ui` | Launch the options scanner web UI |
| `/charts [--symbol X]` | Generate cost-basis charts |
| `/positions` | Run the Google Sheets position tracker |

## Environment

- Python 3.12+, managed by `uv`
- Single shared `.venv/` at repo root (`uv sync` to create/update)
- `stocks-shared` is installed as an editable local package
- Brokerage CSVs go in `input/` (gitignored)
- Config files are gitignored; examples are in `*.toml.example`
