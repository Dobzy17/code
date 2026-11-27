"""Crypto : la règle de tendance a-t-elle besoin de décider 7 jours sur 7 ? Variantes : décisions seulement en semaine,
une fois par semaine (lundi), ou tous les jours (actuel). Satellite BTC/ETH, SMA150, zone ±3 %, frais 0,20 %.
Usage : python3 trading/training_weekdays.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

import backtest as bt
import strategies as st
from data import clean_spikes, load_prices
from research import daily


def restrict(w: pd.DataFrame, allowed: pd.Series) -> pd.DataFrame:
    """Les poids ne peuvent changer que les jours autorisés ; sinon on garde ceux du dernier jour autorisé."""
    out = w.copy()
    out[~allowed.values] = float("nan")
    return out.ffill().fillna(0.0)


def main():
    raw, _ = clean_spikes(load_prices(["BTC-USD", "ETH-USD"], start="2014-01-01"))
    p = daily(raw).loc["2017-11-09":].dropna()
    w = st.trend_band(p, 150, 0.03)
    dow = pd.Series(p.index.dayofweek, index=p.index)
    variants = {"Tous les jours (actuel)": pd.Series(True, index=p.index),
                "Lundi au vendredi seulement": dow < 5,
                "Une fois par semaine (lundi)": dow == 0,
                "Une fois par semaine (dimanche)": dow == 6}
    md = ["# Décider 7 jours sur 7, en semaine ou une fois par semaine ?", "",
          "| Variante | 2018-07 → 2020 | 2021+ | Perte max | Sharpe 2021+ | Ordres |", "|---|---|---|---|---|---|"]
    for name, allowed in variants.items():
        ww = restrict(w, allowed)
        eq = bt.run(p, ww)
        a, b = eq["2018-07-01":"2020-12-31"], eq["2021-01-01":]
        ma, mb, mf = bt.metrics(a / a.iloc[0]), bt.metrics(b / b.iloc[0]), bt.metrics(eq["2018-07-01":] / eq["2018-07-01":].iloc[0])
        n = int((ww.diff().abs() > 0).sum().sum())
        md.append(f"| {name} | {ma['rendement_annuel']:+.1%} | {mb['rendement_annuel']:+.1%} | {mf['perte_max']:.0%} | {mb['sharpe']:.2f} | {n} |")
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_weekdays_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
