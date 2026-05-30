<div align="center">

# 📈 Options Strategy Analyzer

**Real-time options P/L intelligence in a dark FinTech terminal.**

Analyze options strategies against live market data — interactive payoff charts, full metrics, and a plain-English breakdown of every trade.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.22+-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/python/)
[![yfinance](https://img.shields.io/badge/yfinance-0.2.40+-6001D2)](https://github.com/ranaroussi/yfinance)

</div>

---

> ⚠️ **For educational & informational purposes only. Not financial advice.**
> Options trading involves significant risk and is not suitable for all investors.

---

## ✨ Features

- **📡 Live market quotes** — pulls real-time prices via yfinance with a smart fallback chain (regular → post-market → pre-market → last close) and shows market state, % change, and previous close.
- **🎯 Covered Call analyzer** — breakeven, max profit, max loss, % if assigned, static return, and annualised returns, all computed from your position.
- **📊 Interactive P/L chart** — Plotly payoff curve with shaded **loss / profit / opportunity-cost** zones, plus labeled reference lines for current price, breakeven, strike, and cost basis.
- **🧠 Plain-English summary** — every trade explained: best case, static case, risk, and opportunity cost — with key numbers highlighted.
- **📋 Full metrics table** — complete per-share and dollar-total breakdown at a glance.
- **🌑 Dark FinTech UI** — JetBrains Mono + Inter, neon accents, GitHub-dark palette, terminal feel.

## 🖥️ Tech stack

| Layer | Tool |
|-------|------|
| UI / app | Streamlit |
| Data | yfinance |
| Charts | Plotly |
| Math / data | pandas, numpy |

## 🚀 Quick start

```powershell
# Clone, then from the project root:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run main.py
```

App opens at **http://localhost:8501**. Enter a ticker, set strike / premium / expiration / cost basis, and analyze.

## 🧱 Architecture

Clean 4-layer separation:

```
main.py           UI / entry — Streamlit page, theme, inputs, layout
 ├─ data_provider.py   Data — live quotes via yfinance  → StockQuote
 ├─ strategies.py      Logic — OptionStrategy ABC + CoveredCall (pure math)
 └─ charts.py          Viz — Plotly payoff chart with shaded zones
```

Domain math stays pure (no Streamlit/I/O in `strategies.py`); charts take data in and render. See [CLAUDE.md](CLAUDE.md) for the full contract.

## 🗺️ Roadmap

Where this is heading — a full multi-strategy analyzer:

- [ ] **📡 Auto-fetch option prices** — pull the live option chain from yfinance so strikes & premiums populate automatically (cached, with manual override).
- [ ] **🪜 Side-by-side options chain** — classic chain view: calls left, puts right, **strikes down the center**, ATM highlighted, ITM/OTM shading.
- [ ] **➕ More strategies** — Cash-Secured Put · Iron Condor · Strangle · Straddle.
- [ ] **🧩 Custom multi-leg builder** — leg-based payoff engine to assemble any strategy.
- [ ] **🔀 Strategy selector UI** — pick a strategy; inputs, metrics, and chart adapt automatically.

## 📂 Project layout

```
strategy_1/
├─ main.py            # Streamlit entry point
├─ data_provider.py   # yfinance data layer
├─ strategies.py      # strategy math (CoveredCall)
├─ charts.py          # Plotly visualization
├─ requirements.txt   # dependencies
├─ CLAUDE.md          # guidance for Claude Code (architecture, goals, UI rules)
└─ README.md          # this file
```

---

<div align="center">
<sub>Built for learning options. Trade responsibly.</sub>
</div>
