# YouTube Script: Options Scanner

## Title Ideas

- "Find Overpriced Options in 30 Seconds (Free Python Tool)"
- "Stop Guessing Which Options to Sell — Use This"
- "The Options Screener Your Broker Doesn't Have"
- "Scan Any Option Chain for Mispriced Premium with Python"
- "I Built an Options Scanner with Claude Code — Here's How to
  Use It"

---

## Thumbnail Ideas

**Concept 1 — The Terminal IS the Thumbnail** *(recommended)*
Background: the scanner output table — NVDA calls, IV+pp column
color-coded, a few rows clearly highlighted in red/orange. Bold
white text overlaid:
- Large: FIND THE BEST OPTION TO SELL
- Small: Free Python Tool — Any Ticker

**Concept 2 — Split Screen**
Left: brokerage option chain — wall of undifferentiated numbers.
Right: scanner output — 10 clean rows, one clearly glowing. Text:
- Which one? → THIS one.

**Concept 3 — The Hook**
Dark background, terminal on screen, big number in orange:
- +7.2 pp
- "That option is overpriced. Here's how to find them."

---

## HOOK (0:00–1:15)

*[SHOW TERMINAL — run the NVDA --calls scan live]*

```
uv run options-scanner/run_scanner.py NVDA --calls
```

I typed one command. In about ten seconds it fetched NVDA's
entire LEAPS option chain, fit a volatility surface to it, and
ranked every call by how overpriced it is relative to its
neighbors.

*[SHOW OUTPUT TABLE — point to IV+pp column]*

This column here — IV+pp — is doing all the work. It's telling
you how many percentage points each option's implied volatility
sits above where the model says it should be. Positive and
climbing means the option is priced rich. The higher this number,
the more premium you're collecting for a given amount of risk
compared to the rest of the chain.

*[POINT TO TOP ROW]*

So right now, this $[STRIKE] call expiring [DATE] has the most
excess premium of anything on the NVDA chain. Everything you
need to decide whether to sell it is right here — the strike,
expiration, bid-ask, delta, annualized yield, open interest.

I'm going to spend this video showing you how this works, what
the output actually means, and how to set it up and run it for
your own positions. This is only scratching the surface — there's
a portfolio scan, a roll mode, a full web UI, and more. Let's get
into it.

---

## WHAT THE TOOL IS DOING (1:15–2:45)

*[SWITCH TO DIAGRAM OR SIMPLE SLIDE]*

The core idea is this: a stock's option chain should form a
smooth surface. If you plot implied volatility against strike
price and time to expiration, the shape should be consistent —
higher IV for farther out-of-the-money strikes, smooth
transitions between expirations. Market makers keep it that way.

When an option's IV sits noticeably above the fitted surface,
something made it more expensive than its neighbors — a stale
quote, a thin market, event risk that isn't evenly distributed,
or just an inefficiency. That's the option you want to sell.

*[RETURN TO TERMINAL OUTPUT]*

The IV+pp column is the gap between each option's actual IV and
what the surface fit predicts. Small values — under three
percentage points — mean the chain is uniformly priced and the
ranking is mostly noise. Values of five or more are a genuine
signal.

Two more things in the output worth knowing before we dive in.

*[POINT TO DELTA COLUMN]*

Delta is your approximate probability of being assigned at
expiration. A delta of 0.30 means roughly a thirty percent chance
the stock closes above your strike. Lower delta means you keep
the stock more often — you give up some premium to get that
safety margin.

*[POINT TO ANN% COLUMN]*

Ann% is the annualized yield on the premium you'd collect —
for calls, relative to the stock's current price. For puts,
relative to the strike, which is the capital you'd be putting
at risk. This lets you compare options across different
expirations on the same footing.

*[POINT TO HEADER — LT CLOSE DATE]*

And up here — LT close date. If you open a short position today
and hold it for three hundred and sixty-six days before closing,
the premium is taxed at the long-term capital gains rate. This
tells you the earliest you could close for that treatment.

---

## SELLING COVERED CALLS — THE MAIN USE CASE (2:45–5:00)

*[SHOW TERMINAL — same NVDA output]*

Let's say you own NVDA shares and you want to sell a covered
call. You want LEAPS — options a year or more out — so the
premium qualifies for long-term capital gains when you close.
You also want the call to be genuinely overpriced, not just any
call.

*[POINT TO IV+pp COLUMN — HIGHLIGHT TOP ROWS]*

These top rows are ranked exactly for that. The default filter
is delta between 0.10 and 0.50 — real candidates, not deep in
the money or lottery tickets. And minimum open interest of
twenty-five, so you're not staring at options nobody is trading.

*[ADD --delta-min --delta-max flags to command]*

You can narrow the delta range. A lot of covered call sellers
like the 0.25 to 0.40 range — enough premium to be worthwhile,
enough strike distance to not get called away every time the
stock moves.

```
uv run options-scanner/run_scanner.py NVDA --calls \
    --delta-min 0.25 --delta-max 0.40
```

*[SHOW FILTERED OUTPUT]*

Now you're looking at a much tighter slice — real candidates for
a covered call that won't keep you up at night.

*[POINT TO EXPIRATION COLUMN — EARNINGS TAG]*

See the 2E here? That means two earnings events fall before this
expiration. IV tends to spike around earnings — that's the market
pricing in uncertainty, not a free lunch. Worth knowing before
you commit.

*[SHOW --html FLAG]*

Add --html and it saves a report you can open in any browser.
The table is sortable — click any column to re-rank. The IV+pp
column is color-coded: deeper red means more overpriced.

```
uv run options-scanner/run_scanner.py NVDA --calls --html
```

*[OPEN BROWSER — SHOW HTML REPORT]*

You can share this with someone, save it for your records, come
back to it later. It writes to the options-scanner/output folder.

**One honest caveat about the data source.** Everything here
comes from Yahoo Finance, which is free and requires no account.
That's a real advantage for getting started. But Yahoo Finance
has limitations worth knowing.

The implied volatility numbers it returns are sometimes stale
— especially on thinly traded strikes where the last trade was
hours or days ago. The Greeks aren't provided at all; delta
here is calculated from Black-Scholes using Yahoo's IV, which
means if the IV is stale, the delta is too. And for LEAPS
specifically, wide bid-ask spreads and low volume mean some of
the IV readings are noise rather than signal.

None of this breaks the tool — it still surfaces real
patterns — but you should treat the output as a starting
point for further research, not a trading signal on its own.
Always verify the bid-ask spread before acting on anything
the scanner surfaces.

A natural future enhancement would be plugging in a better
data source. Schwab has a developer API — free for account
holders — that returns full option chains with real-time
quotes and proper Greeks: delta, gamma, theta, vega, all
of it. That would make this significantly more accurate,
especially for the IV surface fitting. It's on the roadmap.

---

## MORE FEATURES (5:00–7:15)

*[SHOW TERMINAL]*

That's the core use case, but there's more here.

**Selling puts.** Same idea — swap --calls for --puts. The tool
shows put candidates ranked by IV excess. For puts, Ann% is
calculated relative to the strike price, not the stock price,
because that's the capital you'd be committing if assigned.

```
uv run options-scanner/run_scanner.py NVDA --puts
```

*[SHOW OUTPUT]*

**Rolling an existing position.** You have a call on expiring
in a few months and want to roll it out. Pass --roll with your
current position's details and a NetCr column appears — the
net credit you'd receive after paying to close the old position.
Positive means you'd collect cash on the roll. Negative is a
debit.

```
uv run options-scanner/run_scanner.py NVDA --roll \
    --type call --strike 145 --expiration 2026-03-20
```

*[SHOW ROLL OUTPUT — POINT TO NetCr COLUMN]*

These are ranked by IV excess, so the top row is the new
contract where you'd collect the most excess premium, not just
the most raw premium.

**Short-dated options.** The default is one year or more — LEAPS.
But add --max-dte to look at shorter expirations. This is useful
if you're scanning for near-term premium, or if you want to see
the full picture across timeframes.

```
uv run options-scanner/run_scanner.py NVDA --calls \
    --min-dte 30 --max-dte 90
```

**Buy mode.** Flip the ranking for finding underpriced options —
if you want to buy calls or puts rather than sell them. The same
surface fit, but now you want negative IV excess. Most negative
at the top.

```
uv run options-scanner/run_scanner.py NVDA --calls --buy
```

---

## PORTFOLIO SCAN (7:15–8:30)

*[SHOW TERMINAL]*

Here's my favorite feature if you have more than one or two
positions. You export your full transaction history from your
brokerage — Schwab, Robinhood, Fidelity, or Merrill — and point
the portfolio scanner at it.

```
uv run options-scanner/run_portfolio.py \
    --csv input/schwab028.csv --html
```

*[SHOW TERMINAL OUTPUT — MULTIPLE TICKERS SCROLLING]*

It reads the CSV, figures out every ticker where you currently
hold shares, detects which ones already have a covered call open
against them, and scans each position automatically.

*[SHOW HTML PORTFOLIO REPORT — SUMMARY TABLE AT TOP]*

The HTML report has a summary table up top — every position,
whether it's covered or uncovered, the current spot price.
Then scroll down for each ticker's section.

*[SCROLL TO UNCOVERED POSITION SECTION]*

For uncovered positions — shares with no call against them —
it shows the best calls to sell, same as running the single
ticker scanner manually.

*[SCROLL TO COVERED POSITION SECTION]*

For covered positions, it shows the roll candidates. See the
NetCr column here — this is telling you what you'd collect
net if you closed your existing call and opened each of
these instead.

Instead of opening the tool once per ticker, you run one command
and get a full report across your whole account.

---

## THE WEB UI (8:30–9:15)

*[SHOW BROWSER — STREAMLIT APP]*

If you'd rather not touch the terminal at all, there's a web
interface. One command starts a local web server and opens it
in your browser.

```
uv run streamlit run options-scanner/run_app.py
```

*[SHOW SINGLE TICKER TAB — FILL IN NVDA, HIT SCAN]*

You type the ticker, pick Calls or Puts, set your delta range
with a slider, hit Scan. Results appear as an interactive table
you can sort by clicking any column.

*[CLICK "ROLLING AN EXISTING POSITION?" CHECKBOX]*

Check this box if you're rolling. Fields appear for your current
strike and expiration — it looks up the close cost automatically
and shows you the NetCr column.

*[CLICK DOWNLOAD HTML BUTTON]*

This download button generates the HTML report right in your
browser — no file saved on disk unless you want it.

*[SWITCH TO PORTFOLIO TAB]*

The Portfolio tab is drag-and-drop. Upload your brokerage CSV,
pick your brokerage, hit Scan Portfolio. Progress bar while it
fetches each ticker. Results come back in expandable sections,
one per position. Download the full report with one click.

No Python knowledge required to use this once it's set up.

---

## HOW I BUILT THIS — AND HOW LONG IT TOOK (9:15–10:45)

*[SHOW CLAUDE CODE TERMINAL OR SIDE-BY-SIDE: CHAT ON LEFT,
CODE ON RIGHT]*

Let me show you what it actually took to build this, because
I think it might surprise you.

*[SHOW CONVERSATION SUMMARY OR SCROLL THROUGH PROMPT LIST]*

This entire tool — the scanner, the IV surface model, the roll
mode, the portfolio scan, the HTML reports, the Streamlit web
UI, and the YouTube script you're watching — was built in about
twenty-two back-and-forth messages with Claude Code. Here's a
rough summary of what those conversations looked like:

- "Thinking of building a tool to look at an option chain and
  help me pick the best option to sell."
- "I want to target LEAPS for long-term capital gains on the
  premium. Note earnings dates."
- "Yeah let's build it."
- "How do I run it?"
- "I like both ideas — add earnings fallback and delta range
  filters."
- "Go ahead and implement HTML output, buy mode, and
  short-dated options."
- "Build the portfolio scanner and a Streamlit UI. Don't stop
  to ask me anything — just do it."

That's the gist. No architecture meetings, no tickets, no
planning documents. I described what I wanted, Claude built it,
I tested it, I asked for changes.

*[SHOW GIT LOG OR FILE DIFF]*

The result: just under nineteen hundred lines of Python across
ten source files. Chain fetching, IV surface fitting, earnings
detection, terminal output, HTML report generation, portfolio
parsing, and the Streamlit app.

*[SHOW COMMIT HISTORY IF AVAILABLE, OR FILE TREE]*

All of it written part-time in the evenings over two nights.
Not two weeks. Two nights.

I'm going to make a claim here that I can't prove precisely,
but I believe is in the right ballpark: this took roughly
one hundredth of the effort it would have taken me before
Claude. BC — Before Claude. Not one tenth. One hundredth.

Think about what "before Claude" looks like for a project
like this. You'd spend an evening just researching the right
library for IV surface fitting, reading documentation, looking
at Stack Overflow answers that are three years old and half
wrong. Another evening getting the option chain data into a
usable shape. A weekend on the HTML report. Another session
on the Streamlit UI. You'd hit walls, debug things that
shouldn't be broken, context-switch back to the docs, lose
the thread.

I didn't do any of that. I described what I wanted. Claude
knew what libraries to use, knew the right mathematical
approach, wrote the boilerplate, and kept all the context
in its head across sessions. My effort was deciding what I
wanted — not figuring out how to build it.

That's the shift. The bottleneck used to be implementation.
Now it's just knowing what to ask for.

*[SHOW A SPECIFIC INTERESTING PROMPT-AND-RESPONSE EXCHANGE —
e.g. the IV surface fitting suggestion]*

Here's the one that stuck with me. I described the problem —
I want to find options that are priced differently from what
you'd theoretically expect from the rest of the chain. I didn't
know how to formalize that. Claude suggested fitting a
two-dimensional polynomial in log-moneyness and the square root
of time to expiration. That's a simplified version of a model
called SVI that professional volatility desks actually use. I
wouldn't have known to look for that. Claude did.

That's the real value proposition here — not just that Claude
writes the code faster than I can, but that it brings knowledge
I don't have into the conversation.

*[SHOW CLAUDE CODE TERMINAL — BRIEF DEMO OF ASKING FOR A
SMALL CHANGE]*

And extending it works exactly the same way. If I want to add
a feature — say, filtering by bid-ask spread as a percentage
of mid to weed out illiquid options — I just describe it and
Claude adds it. No documentation to read, no library to learn.

The whole thing is open source. Every line is on GitHub. You
can read it, fork it, change it, or just use it as-is.

---

## WHAT YOU NEED — SETUP (10:45–12:15)

*[SHOW GITHUB REPO]*

Let's walk through everything you'd need to do to run this
yourself.

**Step 1 — Get the code.**

Go to the GitHub repository linked in the description. Either
download the zip or clone it:

```
git clone https://github.com/medloh/stockpile.git
cd stockpile
```

You'll need Git installed — git-scm.com has installers for
Windows and Mac.

*[SHOW PYTHON.ORG]*

**Step 2 — Install Python.**

You'll need Python 3.12 or newer. Go to python.org, download
the installer for your platform. On Windows, check the box that
says "Add Python to PATH" during installation — that's the one
people miss.

*[SHOW TERMINAL]*

**Step 3 — Install uv.**

This project uses uv, which is a fast Python package manager.
One command installs it:

On Mac or Linux:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

On Windows, open PowerShell and run:
```
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

If you really don't want to install uv, you can use plain pip
instead — but uv is much faster and handles the workspace
structure this project uses.

*[SHOW TERMINAL — RUN uv sync]*

**Step 4 — Install dependencies.**

From the stockpile folder:

```
uv sync
```

This installs everything — yfinance, numpy, streamlit, tabulate,
all of it. Takes about thirty seconds the first time.

*[SHOW TERMINAL — RUN THE SCANNER]*

**Step 5 — Run it.**

Single ticker, from the stockpile folder:

```
uv run options-scanner/run_scanner.py NVDA --calls
```

Or start the web UI:

```
uv run streamlit run options-scanner/run_app.py
```

Or scan your portfolio — export your transaction history from
your brokerage, drop it in the input folder, and point the
scanner at it:

```
uv run options-scanner/run_portfolio.py \
    --csv input/your_export.csv --html
```

The README in the options-scanner folder has the full flag
reference. Everything in this video is documented there.

**One important thing.** This tool reads public option chain
data from Yahoo Finance — no account needed, no API key, free.
Your brokerage CSV, if you use the portfolio scanner, stays on
your machine. It never leaves. No Anthropic server sees it.

---

## OUTRO (12:15–12:45)

*[ON CAMERA OR TERMINAL]*

That's the options scanner. Find LEAPS calls and puts ranked by
how overpriced the premium is. Roll an existing position for
maximum net credit. Scan your whole portfolio at once from a
brokerage export. Use the web UI if you don't want to touch
the terminal.

Link to the repo is in the description. If you hit a snag
setting it up, drop a comment — I check them.

The biggest thing on the roadmap is replacing the Yahoo Finance
data source with the Schwab developer API — real-time quotes,
proper Greeks, no stale IV. If that's something you'd use,
let me know in the comments, it'll move up the priority list.

If this was useful, like and subscribe. The previous episode
in this series — building position charts that show your real
adjusted cost basis — should be appearing somewhere around
here.

---

## DESCRIPTION

Free Python Options Scanner — Find Overpriced Calls and Puts
to Sell

I built an open-source option chain scanner with Claude Code
that ranks every LEAPS call or put by how overpriced it is
relative to a fitted volatility surface. Useful for selling
covered calls, cash-secured puts, and rolling existing
positions.

**What it does:**
- Fetches the full option chain from Yahoo Finance (free,
  no API key)
- Fits a 2-D volatility surface to find options priced above
  where they should be
- Ranks by IV excess — the gap between actual and expected
  implied volatility
- Filters by delta, open interest, and days to expiration
- Roll mode: shows net credit for rolling an existing position
- Portfolio scan: reads your brokerage CSV and scans every
  open position automatically
- Web UI: browser-based interface, no terminal required

**What you need:**
- Python 3.12+
- uv (free, one-command install)
- The repo (free on GitHub, link below)
- Optional: a brokerage CSV export for the portfolio scan

**Steps covered:**
0:00 Hook — scanning NVDA live
1:15 How the IV surface works
2:45 Selling covered calls — the main use case
5:00 More features: puts, rolling, buy mode, short-dated
7:15 Portfolio scan — one command for all your positions
8:30 Web UI — no terminal needed
9:15 How I built it — 22 prompts, 2 evenings, ~1900 lines
10:45 Setup — Python, uv, cloning the repo, running it

**Links:**
GitHub repo: https://github.com/medloh/stockpile
Claude Code: https://claude.ai/code
Previous episode (cost basis charts): [link]
Previous episode (Google Sheets tracker): [link]

Your brokerage data stays on your machine. This tool only
calls Yahoo Finance's public API — no accounts, no keys, no
data leaves your computer.

If you hit a snag, drop a comment — I check them.

#options #coveredcalls #python #claudecode #optionstrading
#thetagang #leaps #stockmarket #investing #cashsecuredputs

---

## PRODUCTION NOTES

### Before Recording
- **Commit the options-scanner work to git first.** The "how
  I built this" section references the git log and file count —
  you need those to be real and visible on screen. Run:
  `git add options-scanner && git commit -m "Add options-scanner tool"`
  Then use `git log --oneline` and `git diff HEAD~1 --stat` to
  show the scope of what was added in one commit.
- Do a live run of NVDA --calls right before recording so the
  output is fresh and realistic — pick a day when IV is
  elevated if possible (earnings week, market volatility)
- If NVDA's IV+pp spread is flat (all under 2pp like AMD was),
  either use a different ticker for the hook or acknowledge it
  — "right now NVDA's chain is uniformly priced, which itself
  is useful information"
- Pre-generate the HTML report so you can cut straight to the
  browser without waiting
- Have a real brokerage CSV ready for the portfolio scan demo
  — redact or blur any sensitive position sizes if needed
- Have the Streamlit app already running before recording that
  section — startup takes 3-4 seconds
- For the "how I built this" section, decide whether to show
  the actual Claude Code conversation transcript scrolling, or
  just read the prompt summary bullets on screen. The transcript
  is more compelling but harder to read on camera.

### Sections that need strong pacing
- Hook: keep it under 75 seconds — the output is visual and
  speaks for itself, don't over-narrate
- Setup section: this will be the hardest for non-technical
  viewers — go slowly, show every keystroke, mention that
  the README has written instructions they can follow at
  their own pace

### Before Publishing
- Add chapters (timestamps in description)
- Thumbnail set before publishing
- First two lines of description are visible before "show
  more" — make sure they're compelling
- Add cards at 40% and 70% of runtime pointing to the
  Google Sheets and cost basis chart episodes

### After Publishing
- Share to r/thetagang, r/options, r/learnpython,
  r/investing — lead with the scanner output, not the setup
- Pin a comment with the repo link and a prompt:
  "What other signals would make this more useful?"
- Reply to every comment in the first 48 hours
- Add this video to the exit screens of the previous two
  episodes

### Exit Screens
Add to exit screen of:
- Cost basis charts episode
- Google Sheets tracker episode
