"""
strategies.py — Options strategy logic layer.
Base class: OptionStrategy
Subclass:   CoveredCall
"""

from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import List, Tuple
import pandas as pd


# ── Base class ─────────────────────────────────────────────────────────────────

class OptionStrategy(ABC):
    """Abstract base for all options strategies."""

    @abstractmethod
    def summary_metrics(self) -> dict:
        """Return key metrics as a dictionary."""

    @abstractmethod
    def pl_curve(self, price_range: List[float]) -> List[float]:
        """Return P/L values (per contract = ×100) for each price in range."""


# ── Covered Call ──────────────────────────────────────────────────────────────

@dataclass
class CoveredCall(OptionStrategy):
    """
    Covered Call strategy analytics.

    Parameters
    ----------
    cost_basis   : float   Average cost per share of the underlying position.
    strike       : float   Strike price of the short call option.
    premium      : float   Premium received per share for selling the call.
    dte          : int     Days to expiration (used for annualised return).
    contracts    : int     Number of contracts (1 contract = 100 shares).
    """

    cost_basis : float
    strike     : float
    premium    : float
    dte        : int   = 30
    contracts  : int   = 1

    # ── Derived metrics ────────────────────────────────────────────────────────

    @property
    def breakeven(self) -> float:
        """Price at which the position neither profits nor loses."""
        return round(self.cost_basis - self.premium, 4)

    @property
    def max_profit(self) -> float:
        """Maximum profit per contract (capped at strike)."""
        return round(((self.strike - self.cost_basis) + self.premium) * 100 * self.contracts, 2)

    @property
    def max_loss(self) -> float:
        """Maximum loss per contract (stock goes to zero)."""
        return round(-self.breakeven * 100 * self.contracts, 2)

    @property
    def pct_if_assigned(self) -> float:
        """Percentage return on capital if stock is called away at strike."""
        if self.cost_basis == 0:
            return 0.0
        return round(((self.strike - self.cost_basis + self.premium) / self.cost_basis) * 100, 2)

    @property
    def pct_static(self) -> float:
        """Percentage return on capital if stock stays flat (just premium)."""
        if self.cost_basis == 0:
            return 0.0
        return round((self.premium / self.cost_basis) * 100, 2)

    @property
    def annualised_return_if_assigned(self) -> float:
        """Annualised % return assuming assigned, based on DTE."""
        if self.dte <= 0:
            return 0.0
        return round((self.pct_if_assigned / self.dte) * 365, 2)

    @property
    def annualised_static_return(self) -> float:
        """Annualised % return on the static (premium-only) scenario."""
        if self.dte <= 0:
            return 0.0
        return round((self.pct_static / self.dte) * 365, 2)

    # ── P/L curve ──────────────────────────────────────────────────────────────

    def pl_curve(self, price_range: List[float]) -> List[float]:
        """
        P/L per price point at expiration (total for all contracts).

        Logic:
          - Below breakeven  : loss = (price - breakeven) × 100 × contracts
          - Between breakeven & strike : profit grows linearly
          - Above strike     : profit capped at max_profit (call is assigned)
        """
        pls = []
        for price in price_range:
            if price >= self.strike:
                pls.append(self.max_profit)
            else:
                pl = (price - self.breakeven) * 100 * self.contracts
                pls.append(round(pl, 2))
        return pls

    # ── Summary dict ──────────────────────────────────────────────────────────

    def summary_metrics(self) -> dict:
        return {
            "Breakeven Price"           : self.breakeven,
            "Max Profit ($)"            : self.max_profit,
            "Max Loss ($)"              : self.max_loss,
            "% If Assigned"             : self.pct_if_assigned,
            "% Static (Premium Only)"   : self.pct_static,
            "Annualised (If Assigned)"  : self.annualised_return_if_assigned,
            "Annualised (Static)"       : self.annualised_static_return,
            "Contracts"                 : self.contracts,
            "DTE"                       : self.dte,
        }