<div align="center">

<br>

# 📈 Options Strategy Analyzer

### Real-time options P/L intelligence in a dark FinTech terminal

*Analyze options strategies against live market data — interactive payoff charts, full metrics, and a plain-English breakdown of every trade.*

<br>

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.22+-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/python/)
[![yfinance](https://img.shields.io/badge/yfinance-0.2.40+-6001D2?style=for-the-badge)](https://github.com/ranaroussi/yfinance)

[![Status](https://img.shields.io/badge/status-active%20development-3fb950?style=flat-square)]()
[![License](https://img.shields.io/badge/license-educational-8b949e?style=flat-square)]()
[![Platform](https://img.shields.io/badge/platform-Windows-58a6ff?style=flat-square)]()

</div>

<br>

<div align="center">

`Live Quotes` &nbsp;·&nbsp; `Covered Call` &nbsp;·&nbsp; `Payoff Charts` &nbsp;·&nbsp; `Annualised Returns` &nbsp;·&nbsp; `Dark Terminal UI`

</div>

---

> [!WARNING]
> **For educational & informational purposes only. This is not financial advice.**
> Options trading involves significant risk and is not suitable for all investors. Past performance does not guarantee future results.

---

## 📑 Table of contents

- [Overview](#-overview)
- [Features](#-features)
- [Screenshots](#-screenshots)
- [Tech stack](#️-tech-stack)
- [Quick start](#-quick-start)
- [Usage](#-usage)
- [Metrics explained](#-metrics-explained)
- [Architecture](#-architecture)
- [Design system](#-design-system)
- [Roadmap](#️-roadmap)
- [Project layout](#-project-layout)
- [Disclaimer](#️-disclaimer)

---

## 🔭 Overview

The Options Strategy Analyzer turns a manual options trade into an instant, visual risk profile. Enter a ticker and your position parameters, and it pulls a **live market quote**, computes the full **risk/reward profile**, and renders an **interactive payoff chart** with shaded profit, loss, and opportunity-cost zones — wrapped in a dark, terminal-style interface built for traders.

Today it specializes in the **Covered Call**. The architecture is built to grow into a complete multi-strategy platform (see the [Roadmap](#️-roadmap)).

<div align="center">

```
   Ticker  ──▶  Live Quote  ──▶  Strategy Math  ──▶  Payoff Chart + Metrics + Summary
  (yfinance)     (real-time)      (pure Python)        (Plotly · dark theme)
```

</div>

---

## ✨ Features

### 📡 Live market data
- Real-time quotes via **yfinance** with a smart fallback chain:
  `Regular Market → Post-Market → Pre-Market → Last Close`
- Displays **current price**, **% change**, **previous close**, **company name**, and a color-coded **market-state** badge (regular / pre / post).

### 🎯 Covered Call analyzer
- Full risk/reward computed from your cost basis, strike, premium, DTE, and contract count.
- Outputs **breakeven**, **max profit**, **max loss**, **% if assigned**, **static return**, and **annualised returns** for both scenarios.

### 📊 Interactive P/L chart
- Plotly payoff curve at expiration with three shaded zones:
  - 🔴 **Loss** — below breakeven
  - 🟢 **Profit** — breakeven up to strike
  - 🟡 **Opportunity cost** — capped upside above strike
- Labeled vertical reference lines: **current price**, **breakeven**, **strike**, **cost basis**.
- Unified hover, spike lines, and a floating **MAX PROFIT** annotation.

### 🧠 Plain-English summary
- Every trade explained in prose: **best case**, **static case**, **risk**, and **opportunity cost** — with key numbers bolded and color-coded.
- Live moneyness assessment (ITM / OTM) and a dynamic buffer-to-breakeven sentence.

### 📋 Full metrics table
- Complete per-share and dollar-total breakdown in one mono-spaced table.

### 🌑 Dark FinTech UI
- GitHub-dark palette, neon accents, **JetBrains Mono** + **Inter** typography, custom cards, metric tiles, and badges — a cohesive terminal aesthetic.

---

## 🖼️ Screenshots

> _Add screenshots/GIFs here once captured — drop them in a `docs/` folder and reference below._

<div align="center">

| Live quote + KPIs | Payoff chart | Summary + metrics |
|:---:|:---:|:---:|
| _`docs/quote.png`_ | _`docs/chart.png`_ | _`docs/summary.png`_ |

</div>

---

## 🖥️ Tech stack

<div align="center">

| Layer | Tool | Role |
|:---|:---|:---|
| 🖼️ **UI / App** | Streamlit | Web app, layout, theming, inputs |
| 📡 **Data** | yfinance | Real-time quotes & (planned) option chains |
| 📊 **Charts** | Plotly | Interactive payoff visualization |
| 🧮 **Math / Data** | pandas · numpy | Metrics tables & price-range math |
| 🐍 **Runtime** | Python 3.12 | — |

</div>

---

## 🚀 Quick start

```powershell
# 1 — Create & activate a virtual environment (Windows / PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2 — Install dependencies
pip install -r requirements.txt

# 3 — Launch the app
streamlit run main.py
```

> 🌐 The app opens automatically at **http://localhost:8501**

<details>
<summary><b>macOS / Linux</b></summary>

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run main.py
```
</details>

---

## 🕹️ Usage

1. **Pick an underlying** — type a ticker in the sidebar (e.g. `AAPL`).
2. **Set option parameters** — strike price, premium received, and expiration date (days-to-expiration auto-calculates).
3. **Enter position details** — your cost basis per share and number of contracts (×100 shares).
4. **Analyze** — the app fetches a live quote and instantly renders the quote card, KPI tiles, payoff chart, summary, and metrics table.

> 💡 The view auto-renders on load with sensible defaults, so you see a working example immediately.

---

## 📐 Metrics explained

<div align="center">

| Metric | Meaning |
|:---|:---|
| **Breakeven** | `cost basis − premium`. Price where the position neither gains nor loses. |
| **Max Profit** | `(strike − cost basis + premium) × 100 × contracts`. Achieved when shares are called away at strike. |
| **Max Loss** | `−breakeven × 100 × contracts`. Worst case if the stock goes to zero. |
| **% If Assigned** | Return on cost basis if the stock closes at or above strike. |
| **% Static** | Return from premium alone if the stock stays flat. |
| **Annualised (If Assigned)** | `% if assigned ÷ DTE × 365`. |
| **Annualised (Static)** | `% static ÷ DTE × 365`. |

</div>

> 💵 **Convention:** per-share values are scaled by `× 100 × contracts` for dollar totals. 1 contract = 100 shares.

---

## 🧱 Architecture

Clean **4-layer separation** — UI, data, logic, and visualization never bleed into each other.

```
┌──────────────────────────────────────────────────────────────┐
│  main.py            UI / entry                                 │
│  Streamlit page · CSS theme · sidebar inputs · layout          │
└───────────────┬────────────────────────────────────────────────┘
                │ orchestrates
   ┌────────────┼─────────────────────────────┐
   ▼            ▼                              ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ data_provider.py │  │  strategies.py   │  │    charts.py     │
│ yfinance →       │  │ OptionStrategy   │  │ Plotly payoff    │
│ StockQuote       │  │ ABC + CoveredCall│  │ chart + zones    │
│ (live data)      │  │ (pure math)      │  │ (takes data in)  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

**Principles**
- `strategies.py` is **pure** — no Streamlit, no I/O. Just math.
- `charts.py` takes data in and renders — no fetching, no business logic.
- `data_provider.py` owns all external API access.
- `main.py` wires them together.

> 📖 Full contracts, conventions, and design rules live in **[CLAUDE.md](CLAUDE.md)**.

---

## 🎨 Design system

A deliberate **dark FinTech terminal** aesthetic. New features follow the same tokens.

<div align="center">

| Token | Hex | Meaning |
|:---|:---|:---|
| 🟩 Green | `#3fb950` | Profit / positive |
| 🟨 Yellow | `#d29922` | Caution / capped upside |
| 🟥 Red | `#f85149` | Loss / breakeven |
| 🟦 Blue | `#58a6ff` | Current price / primary accent |
| 🟪 Purple | `#bc8cff` | Cost basis |
| 🟧 Orange | `#ffa657` | Strike |
| ⬛ BG | `#0d1117` | Page background |
| ⬛ Card | `#161b22` | Cards / surfaces |

</div>

- **Typography:** `JetBrains Mono` for all numbers, tickers & labels · `Inter` for prose.
- **Semantics:** green = good, red = loss, yellow = caution, blue = *you are here*.

---

## 🗺️ Roadmap

Building toward a full multi-strategy analyzer:

| | Goal | Description |
|:---:|:---|:---|
| 🔲 | **Auto-fetch option prices** | Pull the live option chain from yfinance so strikes & premiums populate automatically (cached, with manual override). |
| 🔲 | **Side-by-side options chain** | Classic chain view: **calls left · strikes center · puts right**, ATM highlighted, ITM/OTM shading. |
| 🔲 | **More strategies** | Cash-Secured Put · Iron Condor · Strangle · Straddle. |
| 🔲 | **Custom multi-leg builder** | Leg-based payoff engine to assemble any arbitrary strategy. |
| 🔲 | **Strategy selector UI** | Pick a strategy; inputs, metrics & chart adapt automatically. |

<div align="center">
<sub>✅ shipped &nbsp;·&nbsp; 🔲 planned</sub>
</div>

---

## 📂 Project layout

```
strategy_1/
├─ 📄 main.py            # Streamlit entry point — UI, theme, layout
├─ 📡 data_provider.py   # yfinance data layer → StockQuote
├─ 🧮 strategies.py      # strategy math — OptionStrategy ABC + CoveredCall
├─ 📊 charts.py          # Plotly payoff visualization
├─ 📦 requirements.txt   # dependencies
├─ 🤖 CLAUDE.md          # guidance for Claude Code (architecture, goals, UI rules)
├─ 📘 README.md          # this file
└─ 🚫 .gitignore
```

---

## ⚠️ Disclaimer

This software is provided **for educational and informational purposes only**. It does **not** constitute financial, investment, or trading advice. Options trading carries substantial risk of loss. Always do your own research and consult a licensed financial professional before trading.

---

<div align="center">
<br>
<sub>Built for learning options. <b>Trade responsibly.</b></sub>
<br><br>
📈
</div>
