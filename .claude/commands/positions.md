---
description: Run the Google Sheets position tracker
---

Run the position tracker with the provided arguments: `$ARGUMENTS`.

Execute from the repo root:

```
uv run positions/run_tracker.py $ARGUMENTS
```

The tracker reads a brokerage CSV, computes current positions and
realized/unrealized P&L, and pushes them to a Google Sheet. It needs
a configured `positions/config.toml` and Google service account
credentials — see `google-sheets-setup/README.md` if either is
missing.

If config or credentials aren't set up, walk the user through the
setup steps before running.
