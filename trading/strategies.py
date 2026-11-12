"""Stratégies simples, connues et documentées publiquement.

Chaque stratégie renvoie un DataFrame de POIDS CIBLES (0 à 1 par actif, somme <= 1,
le reste est en cash) décidés à la clôture du jour t. Le backtest les applique
au jour t+1 : aucune information du futur n'est utilisée.

On reste volontairement sur des règles robustes et peu nombreuses : plus une
stratégie a de paramètres, plus elle risque de « coller » au passé (surapprentissage)
et de s'effondrer en réel.
"""
from __future__ import annotations

import pandas as pd


def buy_hold(prices: pd.DataFrame) -> pd.DataFrame:
    """Référence : tout acheter à poids égaux et ne rien faire."""
    w = prices.notna().astype(float)
    return w.div(w.sum(axis=1).replace(0, 1), axis=0)


def trend_sma(prices: pd.DataFrame, window: int = 150) -> pd.DataFrame:
    """Suivi de tendance : on détient un actif seulement s'il est au-dessus de sa
    moyenne mobile ; sinon cette part reste en cash. Poids égaux entre actifs."""
    sma = prices.rolling(window).mean()
    on = (prices > sma).astype(float)
    n_assets = prices.notna().sum(axis=1).clip(lower=1)
    return on.div(n_assets, axis=0)


def dual_momentum(prices: pd.DataFrame, risky: list[str], safe: str,
                  lookback: int = 252) -> pd.DataFrame:
    """Momentum dual (G. Antonacci) : chaque fin de mois, on prend l'actif risqué
    qui a le plus monté sur 12 mois ; s'il n'a pas battu l'actif refuge
    (obligations), on se réfugie dans l'actif refuge."""
    mom = prices.pct_change(lookback)
    month_end = prices.index.to_series().groupby(prices.index.to_period("M")).max()
    w = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    current = None
    for day in prices.index:
        if day in month_end.values and mom.loc[day, risky].notna().all():
            best = mom.loc[day, risky].idxmax()
            current = best if mom.loc[day, best] > mom.loc[day, safe] else safe
        if current is not None:
            w.loc[day, current] = 1.0
    return w


STRATEGIES = {
    "buy_hold": buy_hold,
    "trend_sma": trend_sma,
    "dual_momentum": dual_momentum,
}
