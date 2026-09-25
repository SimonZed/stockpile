"""`days_since` — how long a position has been open.

The broker doesn't report when a leg was opened, so this counts it off the
app's own trade log. It feeds the Positions table's **Held** column, which is
blank for anything opened outside the scanner.

(This file used to cover `dte_cell` too — the "85 (12)" cell that packed DTE
and days-open into one string. That cell sorted like text, putting 85 between
8 and 9, so the two figures became two numeric columns and the helper went.)
"""

from datetime import date, datetime, timedelta

import pytest

from options_scanner.format import days_since


def test_days_since_counts_whole_days():
    opened = datetime.now() - timedelta(days=44, hours=3)
    assert days_since(opened.isoformat(timespec="seconds")) == 44


def test_days_since_is_zero_on_the_day_it_opened():
    assert days_since(datetime.now().isoformat(timespec="seconds")) == 0


def test_days_since_accepts_a_bare_date():
    assert days_since(date.today().isoformat()) == 0


@pytest.mark.parametrize("bad", [None, "", "not-a-date", 42, "2026-13-45"])
def test_days_since_gives_up_quietly_on_junk(bad):
    # A malformed record must cost the row its parenthetical, not the table.
    assert days_since(bad) is None
