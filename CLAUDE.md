# CLAUDE.md

Guidance for Claude Code working in this repo.

## What this is

A **Streamlit options-strategy analyzer**. Today it analyzes a single strategy — the **Covered Call** — for one underlying ticker, pulling a live quote and rendering an interactive profit/loss chart plus full metrics. Dark "FinTech" theme, neon accents.

Educational tool. Not financial advice (footer says so).

## Run it

```powershell
.\venv\Scripts\Activate.ps1          # activate venv (Python 3.12)
streamlit run main.py                # launches on http://localhost:8501
```

First-time / fresh machine:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Dependencies (`requirements.txt`): `streamlit`, `yfinance`, `plotly`, `pandas`. `numpy` comes transitively (used in `charts.py`).

## Architecture

Clean 4-layer split. Keep it this way when extending.

| File | Layer | Responsibility |
|------|-------|----------------|
| [main.py](main.py) | UI / entry | Streamlit page: CSS theme, sidebar inputs, validation, layout, renders quote card + metric cards + chart + summary + table. |
| [data_provider.py](data_provider.py) | Data | `get_stock_quote(ticker)` → `StockQuote` dataclass via yfinance. Price priority: regular → post → pre → last close. |
| [strategies.py](strategies.py) | Domain logic | `OptionStrategy` ABC + `CoveredCall` dataclass. All P/L math, breakeven, returns. **No Streamlit, no I/O here.** |
| [charts.py](charts.py) | Viz | `build_pl_chart(strategy, current_price, ticker)` → Plotly figure with shaded loss/profit/opportunity zones + reference lines. |

Data flow: `main.py` reads sidebar inputs → `get_stock_quote()` → constructs `CoveredCall` → `summary_metrics()` + `build_pl_chart()` → renders.

### Key contracts

- `OptionStrategy` ABC ([strategies.py:15](strategies.py#L15)) requires two methods on every strategy:
  - `summary_metrics() -> dict` — label→value pairs for the metrics table.
  - `pl_curve(price_range: List[float]) -> List[float]` — total P/L (×100 × contracts) per price point at expiration.
- `StockQuote` dataclass ([data_provider.py:11](data_provider.py#L11)): `ticker, company_name, current_price, previous_close, change_pct, price_source, market_state`.
- Money convention: per-share values × `100` × `contracts` for dollar totals. 1 contract = 100 shares.

### Current limitations (the starting point)

- **Only one strategy** (`CoveredCall`), hardcoded in [main.py:274](main.py#L274). No strategy selector.
- **Premium is typed in by hand** — not fetched. yfinance is used only for the stock quote, not the option chain.
- **`charts.build_pl_chart` is Covered-Call-specific** (zone logic, annotations assume capped upside). Not yet generic across strategies.
- Auto-renders on load via `if analyze or True:` ([main.py:245](main.py#L245)) — the "ANALYZE" button is effectively cosmetic.
- No tests, no linter config, no caching on the yfinance call.

## Goals (where we're taking it)

Build this out into a full multi-strategy analyzer. Priorities:

### 1. Auto-fetch option prices
Pull the live **option chain** from yfinance (`yf.Ticker(t).option_chain(expiry)`, `.options` for expiry list) so premiums/strikes populate automatically instead of manual entry. Add a `get_option_chain(ticker, expiry)` to `data_provider.py` returning a clean dataclass/DataFrame (strike, bid, ask, last, IV, volume, OI, for calls + puts). Cache with `@st.cache_data` (TTL) to avoid hammering the API. Let the user pick expiry + strike from real data, with manual override still possible.

### 2. Side-by-side options-chain view (strikes centered)
Render a classic options chain: **calls on the left, puts on the right, strike column down the middle**. Highlight ATM strike. This is the centerpiece UI — make it beautiful and consistent with the existing dark/neon theme. Likely its own module (e.g. `chain_view.py`) and a selectable view/tab in `main.py`.

### 3. More strategies
Add subclasses of `OptionStrategy`, each implementing `summary_metrics()` + `pl_curve()`:
- Cash-Secured Put
- Iron Condor
- Strangle
- Straddle
- (extensible — a "custom..." multi-leg builder is the stretch goal)

To support multi-leg payoffs cleanly, consider refactoring toward a **leg-based engine**: a strategy = list of legs (`{type: call/put/stock, side: long/short, strike, premium, qty}`), and a generic `pl_curve` that sums leg payoffs. This makes `build_pl_chart` generic too (compute breakevens, max profit/loss from the curve rather than strategy-specific formulas). Covered Call becomes: long 100 shares + short 1 call.

### 4. Strategy selector UI
Sidebar/tab to choose strategy; inputs adapt per strategy. Generalize the metrics table, summary block, and chart to be strategy-agnostic.

## UI/UX design language (new features MUST follow this)

The look is a deliberate **dark FinTech terminal**. Every new view, table, or control should feel native to it. Source of truth: the `<style>` block in [main.py:28](main.py#L28) and `PALETTE` in [charts.py:12](charts.py#L12).

### Color tokens
Always use these — never raw ad-hoc hex.

| Token | Hex | Use |
|-------|-----|-----|
| `--bg-primary` | `#0d1117` | page background, input fields |
| `--bg-card` | `#161b22` | cards, sidebar, table surface |
| `--bg-hover` | `#1c2128` | hover, table headers |
| `--border` | `#30363d` | all borders, dividers |
| `--text-primary` | `#e6edf3` | primary text/values |
| `--text-sub` | `#8b949e` | labels, captions, uppercase headers |
| `--green` | `#3fb950` | profit / positive / REGULAR market |
| `--yellow` | `#d29922` | caution / static return / opportunity zone |
| `--red` | `#f85149` | loss / negative / breakeven line |
| `--blue` | `#58a6ff` | current price / primary accent / links |
| `--purple` | `#bc8cff` | cost basis / POST market |
| `--orange` | `#ffa657` | strike line / PRE market |

**Semantic rule:** green = good/profit, red = loss, yellow = caution/capped, blue = "you are here"/current. Keep these meanings consistent in charts, tables, badges.

### Typography
- **JetBrains Mono** — all numbers, tickers, prices, metric values, labels, section headers, code-like data. This is the signature look.
- **Inter** — body/prose text only.
- Section labels: mono, ~0.7rem, `text-transform: uppercase`, `letter-spacing: ~0.1em`, color `--text-sub`. Use the `.sidebar-label` pattern for input labels.
- Money: 2 dp, `$` prefix, thousands comma (`$1,234.56`). Percentages: 1–2 dp with `%`.

### Components & patterns (reuse these)
- **`.fin-card`** — rounded (12px) card on `--bg-card`, 1px `--border`, uppercase mono `<h3>` title + large mono `.val`. Color the left border to signal state (e.g. market state on the quote card). Value color classes: `.val-green/-red/-yellow/-blue/-purple/-orange`.
- **`st.metric`** — already themed (mono value, uppercase label, delta line). Use for headline KPIs in a `st.columns(...)` row.
- **`.summary-block`** — left-accent (3px `--blue`) prose card for plain-English explanation. Every strategy view should have a human-readable summary like the Covered Call one. Bold key numbers, color them with `var(--green/red/yellow)`.
- **Tables** — `st.dataframe(df, hide_index=True, use_container_width=True)`. Headers render uppercase mono via global CSS. Use for full metric breakdowns.
- **Buttons** — blue gradient, mono, bold, uppercase, full-width, lift-on-hover. Don't restyle per feature.
- **Badges** — `.quote-badge` pill (rounded, subtle bg, mono) for small status chips.

### Layout
- `layout="wide"`, sidebar expanded. **All user inputs live in the sidebar**, grouped under uppercase mono section headers with `---` dividers between groups.
- Main area top-to-bottom rhythm: header → live data card → KPI metric row → chart → (summary | table two-column split via `st.columns([3,2])`) → disclaimer footer.
- Charts: `use_container_width=True`, ~520px height, dark `paper`/`plot` bg matching `--bg-primary`, `hovermode="x unified"`, mono fonts, shaded zones with `*_fill` rgba colors, dashed vertical reference lines with labeled annotations. Match [charts.py](charts.py) styling for any new payoff chart.
- The new **options-chain view** (calls left / strikes center / puts right) must use these same tokens: mono numbers, `--bg-card` surface, `--border` gridlines, ATM strike highlighted with `--blue`, ITM/OTM shading via the green/red fill tokens.

### Tone
- Professional, terminal/Bloomberg-ish, data-dense but breathable. Uppercase mono micro-labels everywhere.
- Always keep the educational disclaimer footer.

## Conventions

- Keep domain math in `strategies.py` pure — no Streamlit/yfinance imports there. Same for `charts.py` (Plotly only, takes data in).
- Theme palette lives in two places kept in sync: CSS `:root` vars in [main.py:33](main.py#L33) and `PALETTE` dict in [charts.py:12](charts.py#L12). Reuse these colors; don't introduce new ad-hoc hex values.
- Fonts: JetBrains Mono (numbers/labels), Inter (body).
- Dataclasses for data shapes. Type hints throughout. Round money to 2 dp, percentages to 2 dp.
- yfinance can fail / return partial data — wrap fetches in try/except and surface a friendly `st.error`, as `get_stock_quote` already does.

## Gotchas

- yfinance `.info` is slow and occasionally rate-limited / missing fields — that's why there's a fallback chain. Cache aggressively when adding option-chain fetches.
- `pl_curve` returns **totals** (already ×100×contracts), while per-share props (`breakeven`, `premium`) are per-share. Don't double-multiply.
- Platform is Windows / PowerShell. Use `venv\Scripts\` paths.
