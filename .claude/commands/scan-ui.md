---
description: Launch the options scanner Streamlit web UI in the browser
---

Start the Streamlit web UI for the options scanner. This is the
no-CLI-knowledge way to use the tool.

Execute from the repo root:

```
uv run streamlit run options-scanner/run_app.py
```

The app opens at http://localhost:8501 with two tabs:
- **Single Ticker** — form for one symbol, supports rolling an
  existing position
- **Portfolio** — drag-and-drop a brokerage CSV to scan every open
  stock position

Tell the user the URL once it's running. The process keeps running —
they can close the terminal/tab when done.
