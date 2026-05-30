"""
data_provider.py — Real-time stock data engine using yfinance.
Priority: Regular Market Price → Post-Market → Pre-Market
"""

import yfinance as yf
from dataclasses import dataclass
from typing import Optional


@dataclass
class StockQuote:
    ticker: str
    company_name: str
    current_price: float
    previous_close: float
    change_pct: float
    price_source: str          # e.g. "Regular Market", "Post-Market", "Pre-Market"
    market_state: str          # REGULAR | PRE | POST | CLOSED


def get_stock_quote(ticker: str) -> Optional[StockQuote]:
    """
    Fetch the most recent available price for a given ticker symbol.
    Falls back through market states: regular → post-market → pre-market.

    Returns:
        StockQuote dataclass or None if the ticker is invalid.
    """
    try:
        t = yf.Ticker(ticker.upper().strip())
        info = t.info

        # ── Company name ───────────────────────────────────────────────────────
        company_name = (
            info.get("longName")
            or info.get("shortName")
            or ticker.upper()
        )

        # ── Previous close (for change % calculation) ──────────────────────────
        previous_close = (
            info.get("previousClose")
            or info.get("regularMarketPreviousClose")
            or 0.0
        )

        # ── Price priority chain ───────────────────────────────────────────────
        regular_price   = info.get("currentPrice") or info.get("regularMarketPrice")
        post_price      = info.get("postMarketPrice")
        pre_price       = info.get("preMarketPrice")
        market_state_raw = info.get("marketState", "CLOSED").upper()

        if regular_price:
            current_price = float(regular_price)
            price_source  = "Regular Market"
        elif post_price:
            current_price = float(post_price)
            price_source  = "Post-Market"
        elif pre_price:
            current_price = float(pre_price)
            price_source  = "Pre-Market"
        else:
            # Last resort: pull the most recent closing bar
            hist = t.history(period="2d")
            if hist.empty:
                return None
            current_price = float(hist["Close"].iloc[-1])
            price_source  = "Last Close"

        # ── Percentage change vs previous close ───────────────────────────────
        if previous_close and previous_close != 0:
            change_pct = ((current_price - previous_close) / previous_close) * 100
        else:
            change_pct = 0.0

        return StockQuote(
            ticker        = ticker.upper(),
            company_name  = company_name,
            current_price = current_price,
            previous_close= previous_close,
            change_pct    = change_pct,
            price_source  = price_source,
            market_state  = market_state_raw,
        )

    except Exception as exc:
        # Surface the error so the UI can display a friendly message
        raise ValueError(f"Unable to fetch data for '{ticker}': {exc}") from exc