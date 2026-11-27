"""Bourse : la saisonnalité existe-t-elle encore APRÈS sa publication ?
- « Sell in May » (Bouman & Jacobsen, 2002) : investi de novembre à avril, en cash de mai à octobre.
- Effet de fin de mois (Ariel, 1987 ; Lakonishok & Smidt, 1988) : investi seulement le dernier jour du mois + les 3 premiers.
S&P 500 (^GSPC) + 2 %/an de dividendes estimés les jours investis ; cash rémunéré (^IRX) ; frais 0,20 % par changement.
Usage : python3 trading/training_seasonality.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

import backtest as bt
from data import load_prices

P = 252


def run(r: pd.Series, inv: pd.Series, rf: pd.Series) -> pd.Series:
    cost = inv.diff().abs().fillna(0) * 0.002
    rate = rf.reindex(r.index).ffill().fillna(0) / 100 / P
    return (1 + inv * r + (1 - inv) * rate - cost).cumprod()


def main():
    px = load_prices(["^GSPC"], start="1950-01-01")["^GSPC"].dropna()
    rf = load_prices(["^IRX"], start="1960-01-01")["^IRX"]
    r = (px.pct_change() + 0.02 / P).dropna()
    month = r.index.month
    sell_may = pd.Series(((month >= 11) | (month <= 4)).astype(float), index=r.index)
    per = r.index.to_period("M")
    pos = pd.Series(range(len(r)), index=r.index)
    first_idx = pos.groupby(per).transform("min")
    last_idx = pos.groupby(per).transform("max")
    tom = (((pos - first_idx) < 3) | (pos == last_idx)).astype(float)
    md = ["# Saisonnalité du S&P 500 : avant et après publication", "",
          "| Stratégie | 1950-1986 (avant) | 1987-2001 | 2002-2026 (après publication) | Temps investi |", "|---|---|---|---|---|"]
    rows = {"Toujours investi": pd.Series(1.0, index=r.index), "Sell in May (nov.-avril seulement)": sell_may,
            "Fin de mois (4 jours par mois)": tom}
    for name, inv in rows.items():
        e = run(r, inv, rf)
        vals = []
        for a, b in (("1950", "1986"), ("1987", "2001"), ("2002", "2026")):
            x = e[a:b]
            vals.append(bt.metrics(x / x.iloc[0], P)["rendement_annuel"])
        md.append(f"| {name} | {vals[0]:+.1%} | {vals[1]:+.1%} | {vals[2]:+.1%} | {inv.mean():.0%} |")
    # rendement moyen par jour investi : l'effet existe-t-il, même s'il ne paie pas ?
    md += ["", "| Rendement moyen par jour (hors dividendes) | 1950-1986 | 2002-2026 |", "|---|---|---|"]
    rr = px.pct_change().dropna()
    for name, mask in (("Jours de fin de mois", tom.reindex(rr.index).fillna(0) > 0), ("Autres jours", tom.reindex(rr.index).fillna(0) == 0),
                       ("Nov.-avril", sell_may.reindex(rr.index).fillna(0) > 0), ("Mai-oct.", sell_may.reindex(rr.index).fillna(0) == 0)):
        a, b = rr[mask]["1950":"1986"].mean(), rr[mask]["2002":].mean()
        md.append(f"| {name} | {a * 100:+.3f} % | {b * 100:+.3f} % |")
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_seasonality_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
