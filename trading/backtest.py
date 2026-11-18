"""Backtest honnête : décision à la clôture t, exécution en t+1, frais et glissement inclus."""
from __future__ import annotations

import numpy as np
import pandas as pd


def run(prices: pd.DataFrame, weights: pd.DataFrame, cost_bps: float = 20,
        cash_rate: pd.Series | None = None, periods_per_year: int = 365) -> pd.Series:
    """Renvoie la courbe de capital (départ = 1).

    cost_bps : frais + glissement par aller simple, en points de base
    (20 = 0,20 % ; réaliste pour un particulier en crypto ou en ETF).
    cash_rate : taux annuel servi sur la part en cash (par ex. bons du Trésor US à 3 mois).
    """
    rets = prices.pct_change().fillna(0.0)
    held = weights.shift(1).fillna(0.0)          # poids décidés hier, détenus aujourd'hui
    turnover = held.diff().abs().sum(axis=1).fillna(held.abs().sum(axis=1))
    port = (held * rets).sum(axis=1) - turnover * cost_bps / 10_000
    if cash_rate is not None:  # taux annuel (0,05 = 5 %) versé sur la part non investie
        rate = cash_rate.reindex(prices.index).ffill().fillna(0.0)
        port += (1 - held.sum(axis=1)).clip(lower=0) * rate / periods_per_year
    return (1 + port).cumprod()


def metrics(equity: pd.Series, periods_per_year: int = 365) -> dict:
    rets = equity.pct_change().dropna()
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    cagr = equity.iloc[-1] ** (1 / years) - 1 if years > 0 else np.nan
    dd = equity / equity.cummax() - 1
    vol = rets.std() * np.sqrt(periods_per_year)
    sharpe = rets.mean() * periods_per_year / vol if vol > 0 else np.nan
    return {
        "rendement_annuel": cagr,
        "perte_max": dd.min(),
        "volatilite": vol,
        "sharpe": sharpe,
        "multiplicateur": equity.iloc[-1],
    }


def fmt(m: dict) -> str:
    return (f"rendement/an {m['rendement_annuel']:+7.1%} | perte max {m['perte_max']:7.1%} | "
            f"Sharpe {m['sharpe']:5.2f} | x{m['multiplicateur']:.1f}")
