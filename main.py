"""
main.py — Covered Call Strategy Analyzer  ·  Streamlit entry point
"""

import streamlit as st
import datetime
import pandas as pd

from data_provider import get_stock_quote
from strategies import CoveredCall
from charts import build_pl_chart


# ══════════════════════════════════════════════════════════════════════════════
# Page config — must be first Streamlit call
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Options Strategy Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ══════════════════════════════════════════════════════════════════════════════
# Global CSS (FinTech dark theme with neon accents)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@300;400;500;600&display=swap');

/* ── Root variables ─────────────────────────────────────────────── */
:root {
    --bg-primary   : #0d1117;
    --bg-card      : #161b22;
    --bg-hover     : #1c2128;
    --border       : #30363d;
    --text-primary : #e6edf3;
    --text-sub     : #8b949e;
    --green        : #3fb950;
    --yellow       : #d29922;
    --red          : #f85149;
    --blue         : #58a6ff;
    --purple       : #bc8cff;
    --orange       : #ffa657;
    --mono         : 'JetBrains Mono', monospace;
    --sans         : 'Inter', sans-serif;
}

/* ── Global resets ──────────────────────────────────────────────── */
html, body, [class*="css"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: var(--sans) !important;
}

/* ── Sidebar ────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* ── Inputs ─────────────────────────────────────────────────────── */
.stTextInput input, .stNumberInput input, .stDateInput input {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 6px !important;
    font-family: var(--mono) !important;
    font-size: 0.9rem !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(88,166,255,0.15) !important;
}

/* ── Button ─────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #1f6feb, #388bfd) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: var(--mono) !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 1.6rem !important;
    transition: all 0.2s !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(31,111,235,0.4) !important;
}

/* ── Metric cards ────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1rem 1.2rem !important;
}
[data-testid="stMetric"] label { color: var(--text-sub) !important; font-size: 0.72rem !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; }
[data-testid="stMetricValue"] { font-family: var(--mono) !important; font-size: 1.4rem !important; }
[data-testid="stMetricDelta"] { font-family: var(--mono) !important; }

/* ── Dividers ────────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* ── Custom card ─────────────────────────────────────────────────── */
.fin-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}
.fin-card h3 { font-family: var(--mono); font-size: 0.8rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-sub); margin: 0 0 0.6rem 0; }
.fin-card .val { font-family: var(--mono); font-size: 1.6rem; font-weight: 700; }
.val-green  { color: var(--green); }
.val-red    { color: var(--red); }
.val-yellow { color: var(--yellow); }
.val-blue   { color: var(--blue); }
.val-purple { color: var(--purple); }
.val-orange { color: var(--orange); }

/* ── Quote badge ─────────────────────────────────────────────────── */
.quote-badge {
    display: inline-block;
    background: rgba(48,54,61,0.6);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.25rem 0.8rem;
    font-family: var(--mono);
    font-size: 0.78rem;
    color: var(--text-sub);
    margin-left: 0.6rem;
}

/* ── Summary block ───────────────────────────────────────────────── */
.summary-block {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--blue);
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    line-height: 1.75;
    font-size: 0.92rem;
}
.summary-block strong { color: var(--blue); }

/* ── Table ───────────────────────────────────────────────────────── */
.stDataFrame { background: var(--bg-card) !important; border-radius: 10px !important; }
thead tr th { background: #1c2128 !important; color: var(--text-sub) !important; font-family: var(--mono) !important; font-size: 0.75rem !important; text-transform: uppercase !important; letter-spacing: 0.06em !important; }
tbody tr td { font-family: var(--mono) !important; font-size: 0.88rem !important; }

/* ── Sidebar label ───────────────────────────────────────────────── */
.sidebar-label {
    font-family: var(--mono);
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-sub);
    margin-bottom: 0.2rem;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Sidebar — user inputs
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:1.15rem;font-weight:700;
                color:#e6edf3;margin-bottom:0.2rem;">
        📈 Options Analyzer
    </div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#8b949e;
                letter-spacing:0.1em;text-transform:uppercase;margin-bottom:1.5rem;">
        Covered Call Strategy
    </div>
    """, unsafe_allow_html=True)

    # ── Ticker ────────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-label">Underlying Ticker</div>', unsafe_allow_html=True)
    ticker = st.text_input("", value="AAPL", label_visibility="collapsed").upper().strip()

    st.markdown("---")
    st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;letter-spacing:0.08em;text-transform:uppercase;color:#8b949e;margin-bottom:0.8rem;">Option Parameters</div>', unsafe_allow_html=True)

    # ── Strike ────────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-label">Strike Price ($)</div>', unsafe_allow_html=True)
    strike = st.number_input("", value=185.00, step=0.50, format="%.2f", label_visibility="collapsed", key="strike")

    # ── Premium ───────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-label">Call Premium Received ($)</div>', unsafe_allow_html=True)
    premium = st.number_input("", value=3.50, step=0.05, format="%.2f", min_value=0.01, label_visibility="collapsed", key="premium")

    # ── Expiration ────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-label">Expiration Date</div>', unsafe_allow_html=True)
    default_exp = datetime.date.today() + datetime.timedelta(days=30)
    expiration  = st.date_input("", value=default_exp, min_value=datetime.date.today(), label_visibility="collapsed")
    dte = (expiration - datetime.date.today()).days
    st.caption(f"📅 {dte} days to expiration")

    st.markdown("---")
    st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;letter-spacing:0.08em;text-transform:uppercase;color:#8b949e;margin-bottom:0.8rem;">Position Details</div>', unsafe_allow_html=True)

    # ── Cost basis ────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-label">Cost Basis ($/share)</div>', unsafe_allow_html=True)
    cost_basis = st.number_input("", value=175.00, step=0.50, format="%.2f", min_value=0.01, label_visibility="collapsed", key="cost_basis")

    # ── Contracts ────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-label">Contracts (×100 shares)</div>', unsafe_allow_html=True)
    contracts = st.number_input("", value=1, step=1, min_value=1, label_visibility="collapsed", key="contracts")

    st.markdown("---")
    analyze = st.button("⚡  ANALYZE STRATEGY")


# ══════════════════════════════════════════════════════════════════════════════
# Main content
# ══════════════════════════════════════════════════════════════════════════════

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.25rem;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:1.8rem;font-weight:700;color:#e6edf3;">
        Covered Call Analyzer
    </div>
</div>
<div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#8b949e;
            letter-spacing:0.12em;text-transform:uppercase;margin-bottom:1.5rem;">
    Real-Time Options P/L Intelligence
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Run analysis
# ══════════════════════════════════════════════════════════════════════════════

if analyze or True:   # auto-render on load with defaults

    # ── Validation ────────────────────────────────────────────────────────────
    errors = []
    if not ticker:
        errors.append("Please enter a ticker symbol.")
    if strike <= 0:
        errors.append("Strike price must be positive.")
    if premium <= 0:
        errors.append("Premium must be positive.")
    if cost_basis <= 0:
        errors.append("Cost basis must be positive.")
    if dte <= 0:
        errors.append("Expiration date must be in the future.")

    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    # ── Fetch live quote ──────────────────────────────────────────────────────
    with st.spinner(f"Fetching real-time data for {ticker}…"):
        try:
            quote = get_stock_quote(ticker)
        except ValueError as err:
            st.error(str(err))
            st.stop()

    # ── Build strategy ────────────────────────────────────────────────────────
    strategy = CoveredCall(
        cost_basis = cost_basis,
        strike     = strike,
        premium    = premium,
        dte        = max(dte, 1),
        contracts  = contracts,
    )
    metrics = strategy.summary_metrics()

    # ══════════════════════════════════════════════════════════════════════════
    # Row 1 — Live quote card
    # ══════════════════════════════════════════════════════════════════════════
    change_color = "val-green" if quote.change_pct >= 0 else "val-red"
    change_arrow = "▲" if quote.change_pct >= 0 else "▼"
    mkt_badge_color = {
        "REGULAR": "#3fb950", "PRE": "#ffa657", "POST": "#bc8cff"
    }.get(quote.market_state.split("_")[0], "#8b949e")

    st.markdown(f"""
    <div class="fin-card" style="border-left: 3px solid {mkt_badge_color};">
        <h3>{quote.company_name} ({quote.ticker})</h3>
        <div style="display:flex;align-items:baseline;gap:1rem;flex-wrap:wrap;">
            <span class="val val-blue">${quote.current_price:,.2f}</span>
            <span class="val {change_color}" style="font-size:1rem;">
                {change_arrow} {abs(quote.change_pct):.2f}%
            </span>
            <span class="quote-badge" style="border-color:{mkt_badge_color};color:{mkt_badge_color};">
                ● {quote.price_source}
            </span>
            <span class="quote-badge">Prev Close ${quote.previous_close:,.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # Row 2 — Key metric cards
    # ══════════════════════════════════════════════════════════════════════════
    c1, c2, c3, c4, c5 = st.columns(5)

    profit_delta = f"+{metrics['% If Assigned']:.2f}% if assigned"
    c1.metric("Max Profit",   f"${metrics['Max Profit ($)']:,.2f}",  profit_delta)

    c2.metric("Max Loss",     f"${abs(metrics['Max Loss ($)']):,.2f}",
              f"−${strategy.breakeven:.2f} breakeven")

    c3.metric("Breakeven",    f"${metrics['Breakeven Price']:.2f}",
              f"${cost_basis - strategy.breakeven:.2f} buffer")

    c4.metric("Annualised Return",
              f"{metrics['Annualised (If Assigned)']:.1f}%",
              f"{metrics['Annualised (Static)']:.1f}% static")

    c5.metric("Days to Exp.", f"{dte}d",
              f"Exp. {expiration.strftime('%b %d, %Y')}")

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════
    # Row 3 — Chart
    # ══════════════════════════════════════════════════════════════════════════
    fig = build_pl_chart(strategy, quote.current_price, ticker)
    st.plotly_chart(fig, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # Row 4 — Strategy Summary + Detailed Table
    # ══════════════════════════════════════════════════════════════════════════
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown("#### Strategy Summary")

        # Assess moneyness
        itm_otm = "out-of-the-money" if strike > quote.current_price else "in-the-money"
        risk_sentence = (
            f"At current price **${quote.current_price:.2f}**, the stock must "
            f"fall below **${strategy.breakeven:.2f}** before this position loses money — "
            f"a buffer of **${quote.current_price - strategy.breakeven:.2f} "
            f"({((quote.current_price - strategy.breakeven)/quote.current_price*100):.1f}%)**."
            if quote.current_price > strategy.breakeven
            else f"⚠️ The current price **${quote.current_price:.2f}** is already **below the breakeven** "
                 f"of ${strategy.breakeven:.2f}. Consider adjusting the position."
        )

        st.markdown(f"""
        <div class="summary-block">
        You sold <strong>{contracts} × ${strike:.2f} call contract{'s' if contracts>1 else ''}</strong>
        on <strong>{ticker}</strong> ({itm_otm}) with a
        <strong>${premium:.2f} premium</strong> expiring in <strong>{dte} days</strong>.<br><br>

        <strong>Best case:</strong> Stock closes at or above <strong>${strike:.2f}</strong> at expiration.
        Shares are called away and you collect the full
        <strong style="color:var(--green)">${metrics['Max Profit ($)']:,.2f}</strong>
        ({metrics['% If Assigned']:.2f}% / <strong>{metrics['Annualised (If Assigned)']:.1f}% annualised</strong>).<br><br>

        <strong>Static case:</strong> Stock stays flat — you keep the
        <strong style="color:var(--yellow)">${premium*100*contracts:,.2f} premium</strong>
        ({metrics['% Static (Premium Only)']:.2f}% / {metrics['Annualised (Static)']:.1f}% annualised).<br><br>

        <strong>Risk:</strong> {risk_sentence}<br><br>

        <strong>Opportunity cost:</strong> If the stock rallies strongly above
        <strong>${strike:.2f}</strong>, you will not participate in gains beyond
        the strike price (orange zone on chart).
        </div>
        """, unsafe_allow_html=True)

    with col_r:
        st.markdown("#### Full Metrics")
        rows = {
            "Cost Basis"         : f"${cost_basis:.2f}",
            "Strike Price"       : f"${strike:.2f}",
            "Premium Received"   : f"${premium:.2f} / share",
            "Total Premium"      : f"${premium * 100 * contracts:,.2f}",
            "Breakeven"          : f"${strategy.breakeven:.2f}",
            "Max Profit"         : f"${metrics['Max Profit ($)']:,.2f}",
            "Max Loss"           : f"-${abs(metrics['Max Loss ($)']):,.2f}",
            "% If Assigned"      : f"{metrics['% If Assigned']:.2f}%",
            "% Static Return"    : f"{metrics['% Static (Premium Only)']:.2f}%",
            "Ann. (If Assigned)" : f"{metrics['Annualised (If Assigned)']:.2f}%",
            "Ann. (Static)"      : f"{metrics['Annualised (Static)']:.2f}%",
            "DTE"                : f"{dte} days",
            "Contracts"          : f"{contracts}",
        }
        df = pd.DataFrame(list(rows.items()), columns=["Metric", "Value"])
        st.dataframe(df, hide_index=True, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # Footer
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#8b949e;text-align:center;line-height:1.8;">
        ⚠️ For educational & informational purposes only. Not financial advice.<br>
        Options trading involves significant risk and is not suitable for all investors.
    </div>
    """, unsafe_allow_html=True)