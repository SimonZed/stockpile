# options-scanner

Scans a LEAPS option chain (1 year+ out) to find overpriced options
worth selling: covered calls, cash-secured puts, and roll candidates.
Ranked by how much each option's implied volatility sits above a
fitted volatility surface — the higher the excess, the richer the
premium relative to the rest of the chain.

## Running

Always run from the **repo root** using `uv run`:

```bash
# Covered call selection
uv run options-scanner/run_scanner.py AMD --calls

# Cash-secured put selection
uv run options-scanner/run_scanner.py AMD --puts

# Both calls and puts
uv run options-scanner/run_scanner.py AMD

# Narrow to a delta range (e.g. 0.20–0.45 sweet spot)
uv run options-scanner/run_scanner.py AMD --calls \
    --delta-min 0.20 --delta-max 0.45

# Roll an existing short call
uv run options-scanner/run_scanner.py AMD --roll \
    --type call --strike 600 --expiration 2026-01-16
```

### All options

| Flag | Default | Meaning |
|------|---------|---------|
| `--calls` / `--puts` | both | Show only calls or only puts |
| `--buy` | off | Buy mode: rank by lowest IV (underpriced) |
| `--min-dte` | 365 | Minimum days to expiration |
| `--max-dte` | none | Maximum days to expiration |
| `--min-oi` | 25 | Minimum open interest |
| `--delta-min` | 0.10 | Exclude abs(delta) below this |
| `--delta-max` | 0.50 | Exclude abs(delta) above this |
| `--top` | 10 | Max rows shown in terminal |
| `--html` | off | Save an HTML report (see below) |
| `--output-dir` | `options-scanner/output/` | Directory for HTML files |
| `--roll` | — | Roll mode (requires `--type`, `--strike`, `--expiration`) |

### HTML report

Add `--html` to save a self-contained HTML file alongside the
terminal output:

```bash
uv run options-scanner/run_scanner.py AMD --calls --html
```

The file is written to `options-scanner/output/` by default, named
`{TICKER}_{type}_{action}_{date}.html` (e.g.
`AMD_call_sell_20260505.html`). Open it in any browser — columns are
sortable by clicking the headers, and the IV+pp column is
color-coded (red/orange = overpriced sell signal; green/blue =
underpriced buy signal).

Override the directory with `--output-dir path/to/dir`.

## Output columns

| Column | What it means |
|--------|--------------|
| Strike | Option strike price |
| Expiration | Expiration date; `2E` = 2 earnings events before expiry |
| DTE | Days to expiration |
| Bid / Ask / Mid | Market prices |
| IV% | Implied volatility (annualized) |
| IV+pp | IV excess above the fitted surface (see below) |
| Delta | Approx. probability of expiring in the money |
| Ann% | Annualized yield on premium (calls vs. spot; puts vs. strike) |
| OI | Open interest |
| NetCr | Roll mode only: new mid minus close cost |

## Example output and how to read it

```
--------------------------------------------------------------------
  AMD   spot: $355.26   LT close if opened today: May 06 '27
  Upcoming earnings: May 05
--------------------------------------------------------------------

  CALLS
Strike  Expiration      DTE  Bid     Ask     Mid      IV%  IV+pp  Delta  Ann%    OI
------  ------------  -----  ------  ------  ------  ----  -----  -----  ----  ----
$700    Jun 17 '27      408  $27.15  $29.60  $28.38  65.1   +1.6   0.29   7.1   461
$590    Jun 17 '27      408  $39.40  $42.55  $40.97  65.2   +1.3   0.38  10.3    59
$600    Jun 17 '27      408  $37.90  $40.45  $39.17  64.9   +1.1   0.36   9.9   473
$530    Jun 17 '27      408  $48.75  $52.30  $50.52  65.2   +1.0   0.44  12.7  2179
$520    Jun 17 '27      408  $50.45  $54.45  $52.45  65.3   +1.0   0.45  13.2   474
```

### Is there a genuine anomaly?

Look at the `IV+pp` column first. If the top value is under ~3pp, the
chain is uniformly priced and the ranking is mostly noise — there is
no standout overpriced option. In the AMD example above, the max is
+1.6pp, which is small. All these options are priced fairly relative
to each other; AMD's volatility surface is smooth right now.

When you see IV+pp of 5pp or more on a specific strike, that option
is genuinely expensive versus its neighbors — a meaningful signal.

### Picking a strike

When IV+pp is flat across the chain (as above), the decision comes
down to your own risk tolerance:

**Lower delta (e.g. $700, delta 0.29):**
- ~29% chance of assignment at expiration
- Collects $28.38 per share (~7% annualized)
- More room for the stock to run before you're called away

**Higher delta (e.g. $530, delta 0.44):**
- ~44% chance of assignment — roughly a coin flip
- Collects $50.52 per share (~12.7% annualized)
- Much better premium, but real risk of losing the shares

A common covered call sweet spot is delta 0.25–0.40, which balances
premium against assignment risk. Use `--delta-min 0.25 --delta-max
0.40` to filter to that range.

### Earnings tag

`1E` next to an expiration means one earnings event falls before that
date. Elevated IV near earnings is expected and is not a free lunch —
the market is pricing in the uncertainty of the announcement. Selling
into earnings IV is a strategy in itself, but goes beyond anomaly
detection.

### LT capital gains

The header shows the earliest date you could close to qualify for
long-term capital gains treatment (open date + 366 days). If you sell
today and close after that date, the premium is taxed at the LT rate.
In the example: sell today, close any time after **May 06 '27**.

### Ann% for puts

For puts, `Ann%` is calculated as premium divided by the **strike
price** (the capital you'd need to buy 100 shares if assigned),
annualized. This gives the true return on capital at risk.

## Roll mode example

```bash
uv run options-scanner/run_scanner.py AMD --roll \
    --type call --strike 600 --expiration 2026-01-16
```

Adds a `NetCr` column showing what you'd receive net after buying
back the existing position. Positive = net credit roll. The table
shows only calls (same type as the position being rolled), ranked
by IV excess so the richest new premium surfaces first.

## TODO

 - Write a YouTube script

### Plan: portfolio scan (`run_portfolio.py`)

A new entry point that reads a brokerage CSV, finds all open stock
positions, and auto-generates a scan report for each one.

**Implementation sketch:**

1. Parse CSV using existing `stocks_shared` parsers (Schwab etc.)
2. For each ticker: count shares held (sum Buy - Sell on Stock rows)
3. For each ticker with shares > 0: call `detect_open_positions` to
   find any existing short calls against that position
4. For **uncovered** tickers (no open call): run a standard sell scan
   — same as `run_scanner.py TICKER --calls`
5. For **covered** tickers (has open call): run a roll scan for each
   open call — same as `run_scanner.py TICKER --roll ...` — showing
   the NetCr column so the best roll jumps out
6. Generate one combined HTML report:
   - Summary table at top: Ticker | Shares | Spot | Status | Open call
   - One section per ticker with its scan table
   - Reuses all existing `chain`, `iv_surface`, `earnings`, `report`
     machinery

**CLI sketch:**

```bash
uv run options-scanner/run_portfolio.py --csv input/schwab028.csv
uv run options-scanner/run_portfolio.py --csv input/schwab028.csv \
    --html --tickers AAPL AMD
```

**New files needed:**
- `run_portfolio.py` — thin entry point
- `src/portfolio.py` — position parsing + per-ticker scan loop
- extend `src/report.py` — add `save_portfolio_html()`

### Plan: Streamlit web UI (`run_app.py`)

A browser-based UI so no CLI knowledge is needed. One command (or
a double-clickable `.bat`) starts a local web server and opens the
tool in the browser.

**Two tabs:**

- **Single Ticker** — form with ticker, Calls/Puts/Both, Sell/Buy
  toggle, delta slider, DTE range, OI filter. Hit Scan; results
  appear as an interactive sortable table. Download HTML button
  generates the report in-browser (no file saved unless wanted).

- **Portfolio** — drag-and-drop the brokerage CSV, pick brokerage,
  hit Scan. Progress bar while fetching each ticker. Results appear
  in collapsible sections per position. Download full portfolio
  HTML report button.

**Why Streamlit:**
- Pure Python — no HTML/JS needed beyond what already exists
- Runs locally (no hosting, no account)
- `@st.cache_data` means re-adjusting filters doesn't re-fetch
  option chains from Yahoo Finance

**New files needed:**
- `run_app.py` — Streamlit entry point
- `pyproject.toml` — add `streamlit` dependency

**To run:**
```bash
uv run streamlit run options-scanner/run_app.py
```