"""
charts.py — Plotly P/L visualization layer.
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from strategies import CoveredCall


# ── Color palette ──────────────────────────────────────────────────────────────
PALETTE = {
    "bg"           : "#0d1117",
    "card"         : "#161b22",
    "border"       : "#30363d",
    "text"         : "#e6edf3",
    "subtext"      : "#8b949e",
    "green"        : "#3fb950",
    "green_fill"   : "rgba(63,185,80,0.15)",
    "yellow"       : "#d29922",
    "yellow_fill"  : "rgba(210,153,34,0.12)",
    "red"          : "#f85149",
    "red_fill"     : "rgba(248,81,73,0.12)",
    "blue"         : "#58a6ff",
    "purple"       : "#bc8cff",
    "orange"       : "#ffa657",
    "gridline"     : "rgba(48,54,61,0.8)",
}


def build_pl_chart(
    strategy: CoveredCall,
    current_price: float,
    ticker: str = "",
) -> go.Figure:
    """
    Render an interactive Covered Call P/L chart.

    Zones
    -----
    RED    : Stock price < Breakeven  → loss territory
    GREEN  : Breakeven ≤ price ≤ Strike → profit zone
    ORANGE : Stock price > Strike     → opportunity cost (capped upside)
    """

    # ── Price range: 40 % below cost basis → 50 % above strike ───────────────
    x_min = max(0.01, strategy.cost_basis * 0.55)
    x_max = strategy.strike * 1.50
    prices = np.linspace(x_min, x_max, 600).tolist()
    pls    = strategy.pl_curve(prices)

    # ── Segment helpers ────────────────────────────────────────────────────────
    def segment(cond_fn):
        xs, ys = [], []
        for p, pl in zip(prices, pls):
            if cond_fn(p):
                xs.append(p); ys.append(pl)
            else:
                xs.append(None); ys.append(None)
        return xs, ys

    loss_x,  loss_y  = segment(lambda p: p < strategy.breakeven)
    profit_x,profit_y= segment(lambda p: strategy.breakeven <= p <= strategy.strike)
    opp_x,   opp_y   = segment(lambda p: p > strategy.strike)

    # ── Figure ────────────────────────────────────────────────────────────────
    fig = go.Figure()

    # --- Filled shading bands (must come before lines) -----------------------

    # Loss zone shading
    loss_fill_x = [p for p in prices if p < strategy.breakeven]
    loss_fill_y = [pl for p, pl in zip(prices, pls) if p < strategy.breakeven]
    if loss_fill_x:
        fig.add_trace(go.Scatter(
            x=loss_fill_x + loss_fill_x[::-1],
            y=loss_fill_y + [0]*len(loss_fill_y),
            fill="toself", fillcolor=PALETTE["red_fill"],
            line=dict(width=0), showlegend=False, hoverinfo="skip",
            name="_loss_fill",
        ))

    # Profit zone shading
    p_fill_x = [p for p in prices if strategy.breakeven <= p <= strategy.strike]
    p_fill_y = [pl for p, pl in zip(prices, pls) if strategy.breakeven <= p <= strategy.strike]
    if p_fill_x:
        fig.add_trace(go.Scatter(
            x=p_fill_x + p_fill_x[::-1],
            y=p_fill_y + [0]*len(p_fill_y),
            fill="toself", fillcolor=PALETTE["green_fill"],
            line=dict(width=0), showlegend=False, hoverinfo="skip",
            name="_profit_fill",
        ))

    # Opportunity cost shading
    o_fill_x = [p for p in prices if p > strategy.strike]
    o_fill_y = [pl for p, pl in zip(prices, pls) if p > strategy.strike]
    if o_fill_x:
        fig.add_trace(go.Scatter(
            x=o_fill_x + o_fill_x[::-1],
            y=o_fill_y + [strategy.max_profit]*len(o_fill_y),
            fill="toself", fillcolor=PALETTE["yellow_fill"],
            line=dict(width=0), showlegend=False, hoverinfo="skip",
            name="_opp_fill",
        ))

    # --- P/L line segments ---------------------------------------------------
    common_line = dict(width=2.5)

    fig.add_trace(go.Scatter(
        x=loss_x, y=loss_y,
        mode="lines", line=dict(**common_line, color=PALETTE["red"]),
        name="Loss Zone",
        hovertemplate="Price: $%{x:.2f}<br>P/L: $%{y:,.0f}<extra>Loss Zone</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=profit_x, y=profit_y,
        mode="lines", line=dict(**common_line, color=PALETTE["green"]),
        name="Profit Zone",
        hovertemplate="Price: $%{x:.2f}<br>P/L: $%{y:,.0f}<extra>Profit Zone</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=opp_x, y=opp_y,
        mode="lines", line=dict(**common_line, color=PALETTE["yellow"]),
        name="Opportunity Cost Zone",
        hovertemplate="Price: $%{x:.2f}<br>P/L: $%{y:,.0f}<extra>Opportunity Cost</extra>",
    ))

    # --- Zero line -----------------------------------------------------------
    fig.add_hline(
        y=0,
        line=dict(color=PALETTE["subtext"], width=1, dash="dot"),
    )

    # --- Vertical reference lines -------------------------------------------
    vline_cfg = [
        (current_price,        PALETTE["blue"],   "Current Price",  "solid"),
        (strategy.breakeven,   PALETTE["red"],    "Breakeven",      "dash"),
        (strategy.strike,      PALETTE["orange"], "Strike",         "dash"),
        (strategy.cost_basis,  PALETTE["purple"], "Cost Basis",     "dot"),
    ]
    for xval, color, label, dash in vline_cfg:
        if x_min <= xval <= x_max:
            fig.add_vline(
                x=xval,
                line=dict(color=color, width=1.5, dash=dash),
                annotation_text=f"  {label}<br>  ${xval:.2f}",
                annotation_position="top",
                annotation=dict(
                    font=dict(color=color, size=11, family="JetBrains Mono, monospace"),
                    bgcolor="rgba(13,17,23,0.75)",
                    borderpad=4,
                ),
            )

    # --- Max profit annotation -----------------------------------------------
    fig.add_annotation(
        x=strategy.strike + (x_max - strategy.strike) * 0.4,
        y=strategy.max_profit * 0.85,
        text=f"<b>MAX PROFIT</b><br>${strategy.max_profit:,.0f}",
        showarrow=False,
        font=dict(color=PALETTE["yellow"], size=12, family="JetBrains Mono, monospace"),
        bgcolor="rgba(13,17,23,0.8)",
        bordercolor=PALETTE["yellow"],
        borderwidth=1,
        borderpad=6,
    )

    # --- Layout --------------------------------------------------------------
    fig.update_layout(
        title=dict(
            text=f"<b>{ticker} · Covered Call P/L at Expiration</b>",
            font=dict(size=18, color=PALETTE["text"], family="JetBrains Mono, monospace"),
            x=0.02, y=0.97,
        ),
        plot_bgcolor =PALETTE["bg"],
        paper_bgcolor=PALETTE["bg"],
        font=dict(color=PALETTE["text"], family="JetBrains Mono, monospace"),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=PALETTE["card"],
            bordercolor=PALETTE["border"],
            font=dict(color=PALETTE["text"], size=12),
        ),
        xaxis=dict(
            title="Stock Price at Expiration ($)",
            gridcolor=PALETTE["gridline"],
            zerolinecolor=PALETTE["border"],
            tickprefix="$",
            tickformat=",.2f",
            showspikes=True,
            spikecolor=PALETTE["subtext"],
            spikethickness=1,
            spikedash="dot",
        ),
        yaxis=dict(
            title="Profit / Loss ($)",
            gridcolor=PALETTE["gridline"],
            zerolinecolor=PALETTE["border"],
            tickprefix="$",
            tickformat=",.0f",
            showspikes=True,
            spikecolor=PALETTE["subtext"],
            spikethickness=1,
        ),
        legend=dict(
            bgcolor="rgba(22,27,34,0.9)",
            bordercolor=PALETTE["border"],
            borderwidth=1,
            font=dict(size=11),
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right",  x=1,
        ),
        margin=dict(l=70, r=40, t=80, b=60),
        height=520,
    )

    return fig