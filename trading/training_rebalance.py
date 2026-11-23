"""Rééquilibrage du portefeuille du robot (70 % ACWI + 30 % BTC/ETH avec tendance) : seuil de 2 points (actuel)
contre 5, 10 points, une fois par mois, une fois par an, ou jamais. Simulation avec la vraie dérive des poids.
Usage : python3 trading/training_rebalance.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd

import backtest as bt
import strategies as st
from data import clean_spikes, load_prices
from research import daily

COST = 0.002


def simulate(p: pd.DataFrame, mode: str, band: float = 0.02) -> tuple[pd.Series, int]:
    crypto = ["BTC-USD", "ETH-USD"]
    on = st.trend_band(p[crypto], 150, 0.03) > 0
    tgt = pd.DataFrame({"ACWI": 0.70, "BTC-USD": 0.15 * on["BTC-USD"], "ETH-USD": 0.15 * on["ETH-USD"]}, index=p.index)
    tgt = tgt.shift(1).fillna(0.0)                        # décision d'hier, exécutée aujourd'hui
    units = pd.Series(0.0, index=p.columns)
    cash, equity, trades = 1.0, [], 0
    for i, d in enumerate(p.index):
        px = p.loc[d]
        val = cash + (units * px).sum()
        w = units * px / val
        t = tgt.loc[d]
        held = units > 1e-12
        signal_change = ((t == 0) & held) | ((t > 0) & ~held)      # entrée/sortie crypto : toujours
        if mode == "seuil":
            do = (w - t).abs() > band
        elif mode == "mensuel":
            do = pd.Series(i == 0 or d.month != p.index[i - 1].month, index=p.columns)
        elif mode == "annuel":
            do = pd.Series(i == 0 or d.year != p.index[i - 1].year, index=p.columns)
        else:                                             # jamais (sauf signaux crypto et achat initial)
            do = pd.Series(i == 0, index=p.columns)
        do = do | signal_change
        for a in p.columns[do.values]:
            diff = t[a] * val - units[a] * px[a]
            if abs(diff) < 1e-9:
                continue
            units[a] += diff / px[a]
            if t[a] == 0:
                units[a] = 0.0                            # vente totale : quantité exactement nulle
            cash -= diff + abs(diff) * COST
            trades += 1
        equity.append(cash + (units * px).sum())
    return pd.Series(equity, index=p.index), trades


def main():
    raw, _ = clean_spikes(load_prices(["ACWI", "BTC-USD", "ETH-USD"], start="2014-01-01"))
    p = daily(raw).loc["2017-11-09":].dropna()
    md = ["# Fréquence de rééquilibrage (portefeuille complet du robot, frais 0,20 %)", "",
          f"{p.index[150].date()} → {p.index[-1].date()} (les 150 premiers jours servent à calculer la moyenne).", "",
          "| Méthode | Rendement/an | Perte max | Sharpe | Ordres sur la période |", "|---|---|---|---|---|"]
    for name, mode, band in (("Seuil 2 points (actuel)", "seuil", 0.02), ("Seuil 5 points", "seuil", 0.05),
                             ("Seuil 10 points", "seuil", 0.10), ("Une fois par mois", "mensuel", 0),
                             ("Une fois par an", "annuel", 0), ("Jamais (seulement les signaux crypto)", "jamais", 0)):
        eq, n = simulate(p, mode, band)
        eq = eq.iloc[150:]
        m = bt.metrics(eq / eq.iloc[0])
        md.append(f"| {name} | {m['rendement_annuel']:+.1%} | {m['perte_max']:.0%} | {m['sharpe']:.2f} | {n} |")
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_rebalance_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
