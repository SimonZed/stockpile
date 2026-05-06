"""Streamlit web UI for the options scanner."""

import os
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Options Scanner", page_icon="📈", layout="wide")


# ── Cached data fetching ─────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def _fetch_and_enrich(ticker: str, opt_type: str, min_dte: int,
                      max_dte: int | None):
    from chain import fetch_chain
    from iv_surface import compute_iv_excess
    from earnings import fetch_earnings_dates, annotate_earnings
    try:
        df = fetch_chain(ticker, opt_type=opt_type, min_dte=min_dte,
                         max_dte=max_dte)
    except ValueError as exc:
        return pd.DataFrame(), [], str(exc)
    if df.empty:
        return df, [], None
    df = compute_iv_excess(df)
    earnings = fetch_earnings_dates(ticker)
    df = annotate_earnings(df, earnings)
    return df, earnings, None


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_position(ticker: str, min_dte: int):
    """Cached per-ticker chain fetch for portfolio tab."""
    from chain import fetch_chain
    from iv_surface import compute_iv_excess
    from earnings import fetch_earnings_dates, annotate_earnings
    try:
        df = fetch_chain(ticker, opt_type="calls", min_dte=min_dte)
    except ValueError as exc:
        return pd.DataFrame(), [], str(exc)
    if df.empty:
        return df, [], None
    df = compute_iv_excess(df)
    earnings = fetch_earnings_dates(ticker)
    df = annotate_earnings(df, earnings)
    return df, earnings, None


# ── Display helpers ──────────────────────────────────────────────────────────

def _show_df(sub: pd.DataFrame, roll_close_cost: float | None = None) -> None:
    if sub.empty:
        st.info("No options match the current filters.")
        return

    disp = pd.DataFrame({
        "Strike": sub["strike"].apply(lambda x: f"${x:.0f}"),
        "Expiration": sub.apply(
            lambda r: datetime.strptime(r["expiration"], "%Y-%m-%d").strftime("%b %d '%y")
            + (f" {int(r['earnings_count'])}E" if r.get("earnings_count", 0) > 0 else ""),
            axis=1,
        ),
        "DTE":    sub["dte"].astype(int),
        "Bid":    sub["bid"].round(2),
        "Ask":    sub["ask"].round(2),
        "Mid":    sub["mid"].round(2),
        "IV%":    (sub["iv"] * 100).round(1),
        "IV+pp":  (sub["iv_excess"] * 100).round(1),
        "Delta":  sub["delta"].round(2),
        "Ann%":   sub["ann_yield_pct"].round(1),
        "OI":     sub["open_interest"],
    })
    if roll_close_cost is not None:
        disp["NetCr"] = (sub["mid"] - roll_close_cost).round(2)

    col_cfg = {
        "Bid":   st.column_config.NumberColumn("Bid",   format="$%.2f"),
        "Ask":   st.column_config.NumberColumn("Ask",   format="$%.2f"),
        "Mid":   st.column_config.NumberColumn("Mid",   format="$%.2f"),
        "IV%":   st.column_config.NumberColumn("IV%",   format="%.1f%%"),
        "IV+pp": st.column_config.NumberColumn("IV+pp", format="%+.1f pp"),
        "Delta": st.column_config.NumberColumn("Delta", format="%.2f"),
        "Ann%":  st.column_config.NumberColumn("Ann%",  format="%.1f%%"),
        "OI":    st.column_config.NumberColumn("OI",    format="%d"),
    }
    if roll_close_cost is not None:
        col_cfg["NetCr"] = st.column_config.NumberColumn("Net Credit", format="$%+.2f")

    st.dataframe(disp, column_config=col_cfg, hide_index=True,
                 use_container_width=True)


def _show_scan_results(df: pd.DataFrame, mode: str, buy: bool,
                       roll_close_cost: float | None,
                       min_oi: int, top_n: int) -> None:
    iv_asc = buy
    type_labels = {"call": "Calls", "put": "Puts"}
    to_show = [mode] if mode in type_labels else list(type_labels.keys())

    for opt_type in to_show:
        sub = (
            df[df["type"] == opt_type]
            .sort_values(["iv_excess", "open_interest"], ascending=[iv_asc, False])
        )
        sub = sub[sub["open_interest"] >= min_oi].head(top_n)
        if len(to_show) > 1:
            st.subheader(type_labels[opt_type])
        _show_df(sub, roll_close_cost)


# ── Tab: Single Ticker ───────────────────────────────────────────────────────

def _tab_single() -> None:
    # ── Inputs (no form — lets roll section show/hide dynamically) ────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        ticker = st.text_input("Ticker Symbol", "AAPL", key="s_ticker")
        action = st.radio("Action", ["Sell (find overpriced)", "Buy (find underpriced)"],
                          key="s_action")
        option_type = st.radio("Option Type", ["Calls", "Puts", "Both"],
                               key="s_opt_type")
    with c2:
        min_dte = st.number_input("Min Days to Expiration", value=365, min_value=1,
                                  key="s_min_dte")
        max_dte_inp = st.number_input("Max DTE (0 = no limit)", value=0, min_value=0,
                                      key="s_max_dte")
        min_oi = st.number_input("Min Open Interest", value=25, min_value=0,
                                 key="s_min_oi")
    with c3:
        delta_range = st.slider("Delta Range (abs value)", 0.0, 1.0, (0.10, 0.50),
                                step=0.05, key="s_delta")
        top_n = st.number_input("Max rows to show", value=10, min_value=1,
                                max_value=50, key="s_top")

    # ── Roll section (appears only when checkbox is ticked) ───────────────────
    rolling = st.checkbox("Rolling an existing position?", key="s_rolling")
    roll_strike = 0.0
    roll_exp    = date.today()
    roll_type_sel = "call"
    if rolling:
        st.caption("Enter the details of the position you want to close and replace.")
        r1, r2, r3 = st.columns(3)
        with r1:
            roll_type_sel = st.selectbox("Position type", ["call", "put"],
                                         key="s_roll_type")
        with r2:
            roll_strike = st.number_input("Current strike", value=0.0,
                                          min_value=0.0, step=1.0, key="s_roll_strike")
        with r3:
            roll_exp = st.date_input("Current expiration", key="s_roll_exp")

    scanned = st.button("Scan", type="primary", use_container_width=True,
                         key="s_scan_btn")

    # ── Run scan on button click, store in session state ──────────────────────
    if scanned:
        ticker_clean = ticker.strip().upper()
        if not ticker_clean:
            st.error("Enter a ticker symbol.")
            st.session_state.pop("single_results", None)
            return

        buy = action.startswith("Buy")

        # In roll mode, force option type to match the position being rolled
        if rolling:
            eff_opt_fetch = roll_type_sel + "s"   # "calls" or "puts"
            eff_mode      = roll_type_sel          # "call"  or "put"
        else:
            opt_map  = {"Calls": "calls", "Puts": "puts", "Both": "both"}
            mode_map = {"Calls": "call",  "Puts": "put",  "Both": "both"}
            eff_opt_fetch = opt_map[option_type]
            eff_mode      = mode_map[option_type]

        max_dte_arg = int(max_dte_inp) if max_dte_inp > 0 else None
        delta_min, delta_max = delta_range

        with st.spinner(f"Fetching {ticker_clean} option chain…"):
            df, earnings_dates, err = _fetch_and_enrich(
                ticker_clean, eff_opt_fetch, int(min_dte), max_dte_arg
            )

        if err:
            st.error(err)
            st.session_state.pop("single_results", None)
            return
        if df.empty:
            st.warning(f"No options found for {ticker_clean} with the given DTE range.")
            st.session_state.pop("single_results", None)
            return

        # Roll: look up close cost for the existing position
        roll_close_cost = None
        if rolling and roll_strike > 0:
            from stocks_shared.yahoo import fetch_option_chain
            exp_yf = roll_exp.strftime("%Y-%m-%d")
            with st.spinner("Looking up close cost…"):
                chain = fetch_option_chain(ticker_clean, exp_yf)
            if chain is not None:
                side_df = chain.calls if roll_type_sel == "call" else chain.puts
                row = side_df[side_df["strike"] == float(roll_strike)]
                if not row.empty:
                    bid  = float(row["bid"].iloc[0] or 0)
                    ask  = float(row["ask"].iloc[0] or 0)
                    last = float(row["lastPrice"].iloc[0] or 0)
                    roll_close_cost = (bid + ask) / 2 if bid > 0 and ask > 0 else last
                else:
                    st.warning("Position not found in chain — NetCr column omitted.")
            else:
                st.warning(f"Could not fetch chain for {exp_yf} — NetCr column omitted.")

        st.session_state["single_results"] = {
            "ticker": ticker_clean,
            "df": df,
            "earnings_dates": earnings_dates,
            "mode": eff_mode,
            "buy": buy,
            "roll_close_cost": roll_close_cost,
            "delta_min": delta_min,
            "delta_max": delta_max,
            "min_oi": int(min_oi),
            "top_n": int(top_n),
            "roll_exp_str": roll_exp.strftime("%Y-%m-%d") if rolling else None,
            "roll_strike": roll_strike if rolling else None,
            "roll_type": roll_type_sel if rolling else None,
        }

    # ── Display results (persists across re-runs until next scan) ─────────────
    res = st.session_state.get("single_results")
    if not res:
        return

    ticker_r  = res["ticker"]
    df_r      = res["df"]
    mode_r    = res["mode"]
    buy_r     = res["buy"]
    rcc       = res["roll_close_cost"]
    df_filt   = df_r[df_r["delta"].abs().between(
                    res["delta_min"], res["delta_max"])].copy()
    spot      = float(df_r["spot"].iloc[0])
    lt_date   = (date.today() + timedelta(days=366)).strftime("%b %d '%y")

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Spot", f"${spot:.2f}")
    m2.metric("LT Close", lt_date)
    m3.metric("Expirations", df_r["expiration"].nunique())
    ed = res["earnings_dates"]
    m4.metric("Next Earnings", ed[0].strftime("%b %d") if ed else "unknown")

    if rcc is not None:
        st.info(f"Rolling {res['roll_type']} ${res['roll_strike']:.0f} "
                f"{res['roll_exp_str']} — close cost (mid): **${rcc:.2f}**")

    _show_scan_results(df_filt, mode_r, buy_r, rcc,
                       res["min_oi"], res["top_n"])

    from report import render_html
    html = render_html(df_filt, ticker_r, spot, ed, mode_r, buy_r, rcc,
                       res["min_oi"])
    action_tag = "buy" if buy_r else "sell"
    type_tag   = mode_r if mode_r != "both" else "both"
    st.download_button(
        "⬇ Download HTML Report",
        data=html.encode("utf-8"),
        file_name=f"{ticker_r}_{type_tag}_{action_tag}_{date.today().strftime('%Y%m%d')}.html",
        mime="text/html",
        key="s_download",
    )


# ── Tab: Portfolio ───────────────────────────────────────────────────────────

def _tab_portfolio() -> None:
    uploaded = st.file_uploader("Upload brokerage CSV export", type=["csv"])

    pc1, pc2, pc3, pc4, pc5 = st.columns(5)
    with pc1:
        brokerage = st.selectbox(
            "Brokerage", ["schwab", "robinhood", "fidelity", "merrill"]
        )
    with pc2:
        port_min_dte = st.number_input("Min DTE", value=365, min_value=1,
                                       key="p_min_dte")
    with pc3:
        port_min_oi = st.number_input("Min OI", value=25, min_value=0,
                                      key="p_min_oi")
    with pc4:
        port_max_delta = st.slider("Max Delta", 0.0, 1.0, 0.70, 0.05,
                                   key="p_max_delta")
    with pc5:
        port_top = st.number_input("Top N per ticker", value=5, min_value=1,
                                   key="p_top")

    if not st.button("Scan Portfolio", type="primary",
                     disabled=(uploaded is None)):
        return

    from portfolio import get_portfolio
    from stocks_shared.yahoo import fetch_option_chain

    # Write upload to a temp file so the parser can read it
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        f.write(uploaded.getvalue())
        tmp_path = f.name

    try:
        positions = get_portfolio(tmp_path, brokerage)
    except Exception as exc:
        st.error(f"Could not parse CSV: {exc}")
        os.unlink(tmp_path)
        return

    os.unlink(tmp_path)

    if not positions:
        st.warning("No open stock positions found in this CSV.")
        return

    st.success(f"Found {len(positions)} position(s): "
               f"{', '.join(p['ticker'] for p in positions)}")

    progress = st.progress(0, text="Scanning…")
    results = []
    for i, pos in enumerate(positions):
        ticker = pos["ticker"]
        progress.progress((i + 1) / len(positions),
                          text=f"Scanning {ticker} ({i+1}/{len(positions)})…")

        df, earnings_dates, err = _fetch_position(ticker, int(port_min_dte))

        # Look up roll close costs for open calls
        roll_close_costs = {}
        for opt in pos["open_calls"]:
            m, d, y = opt["expiration"].split("/")
            exp_yf = f"{y}-{m}-{d}"
            chain = fetch_option_chain(ticker, exp_yf)
            if chain is not None:
                row = chain.calls[chain.calls["strike"] == float(opt["strike"])]
                if not row.empty:
                    bid  = float(row["bid"].iloc[0] or 0)
                    ask  = float(row["ask"].iloc[0] or 0)
                    last = float(row["lastPrice"].iloc[0] or 0)
                    roll_close_costs[opt["symbol"]] = (
                        (bid + ask) / 2 if bid > 0 and ask > 0 else last
                    )

        results.append({
            "position": pos,
            "error": err,
            "df": df,
            "spot": float(df["spot"].iloc[0]) if not df.empty else None,
            "earnings_dates": earnings_dates,
            "roll_close_costs": roll_close_costs,
        })

    progress.empty()

    for res in results:
        pos    = res["position"]
        ticker = pos["ticker"]
        covered = bool(pos["open_calls"])
        label  = f"{ticker} — {pos['shares']} shares — {'Covered' if covered else 'Uncovered'}"

        with st.expander(label, expanded=True):
            if res["error"]:
                st.error(res["error"])
                continue

            spot           = res["spot"]
            earnings_dates = res["earnings_dates"]
            df             = res["df"]

            m1, m2, m3 = st.columns(3)
            m1.metric("Spot", f"${spot:.2f}")
            lt = (date.today() + timedelta(days=366)).strftime("%b %d '%y")
            m2.metric("LT Close", lt)
            m3.metric("Next Earnings",
                      earnings_dates[0].strftime("%b %d")
                      if earnings_dates else "unknown")

            for opt in pos["open_calls"]:
                close = res["roll_close_costs"].get(opt["symbol"])
                close_str = f" — close mid: **${close:.2f}**" if close else ""
                st.info(f"Open call: **{opt['symbol']}** "
                        f"({opt['contracts']} contract(s)){close_str}")

            roll_close = None
            if pos["open_calls"]:
                first = pos["open_calls"][0]
                roll_close = res["roll_close_costs"].get(first["symbol"])

            df_filt = df[df["delta"].abs() <= port_max_delta].copy()
            _show_scan_results(df_filt, "call", False, roll_close,
                               int(port_min_oi), int(port_top))

    # Portfolio HTML download
    from report import render_portfolio_html
    port_html = render_portfolio_html(
        results, uploaded.name, int(port_min_oi), int(port_top)
    )
    st.download_button(
        "⬇ Download Portfolio Report",
        data=port_html.encode("utf-8"),
        file_name=f"portfolio_{date.today().strftime('%Y%m%d')}.html",
        mime="text/html",
    )


# ── Main ─────────────────────────────────────────────────────────────────────

st.title("📈 Options Scanner")

tab_single, tab_portfolio = st.tabs(["Single Ticker", "Portfolio"])

with tab_single:
    _tab_single()

with tab_portfolio:
    _tab_portfolio()
