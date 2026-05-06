# CLAUDE.md — options-scanner

## Purpose

Scan a LEAPS option chain (1 year+ DTE) to find overpriced options
worth selling: covered calls, cash-secured puts, and roll candidates.
Ranks by IV excess — how much the option's implied volatility sits
above a fitted 2-D surface — to surface genuinely rich premium vs.
options that merely look expensive because they're deep ITM.

## How it works

1. Fetch all expirations with DTE >= min_dte from Yahoo Finance
2. Build a 2-D IV surface: IV ≈ f(log-moneyness, √T)
3. Compute IV excess = actual IV − fitted IV (positive = overpriced)
4. Annotate each option with earnings events within its expiration
   window (elevated IV around earnings is expected, not anomalous)
5. Display ranked table including delta, annualized yield, and OI

## Running the tool

Always run from the **repo root** using `uv run`:

```bash
# Both calls and puts (default)
uv run options-scanner/run_scanner.py AAPL

# Covered call selection only
uv run options-scanner/run_scanner.py AAPL --calls

# Cash-secured put selection only
uv run options-scanner/run_scanner.py AAPL --puts

# Roll an existing short call
uv run options-scanner/run_scanner.py AAPL --roll \
    --type call --strike 185 --expiration 2026-01-16

# Adjust filters
uv run options-scanner/run_scanner.py AAPL --calls \
    --min-dte 400 --min-oi 50 --top 20
```

Never use `python` directly — dependencies won't be resolved.
Run `uv sync` from repo root after any `pyproject.toml` change.

## Output columns

| Column  | Meaning                                            |
|---------|----------------------------------------------------|
| Strike  | Option strike price                                |
| Expiration | Expiration date; trailing `2E` = 2 earnings before exp |
| DTE     | Days to expiration                                 |
| Bid/Ask/Mid | Market prices                                 |
| IV%     | Implied volatility (annualized %)                  |
| IV+pp   | IV excess above surface fit (positive = rich)      |
| Delta   | Black-Scholes delta (call: 0–1, put: −1–0)         |
| Ann%    | Annualized yield: calls vs. spot, puts vs. strike  |
| OI      | Open interest                                      |
| NetCr   | Roll mode only: net credit received if rolled here |

## LT capital gains note

Selling an option and holding the short position for 366+ days
qualifies the premium for long-term capital gains rates. The tool
prints the earliest qualifying close date for a position opened today.
