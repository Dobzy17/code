"""Bourse : rotation sectorielle par momentum (9 ETF sectoriels SPDR, depuis 1999).
Chaque fin de mois : détenir les 3 secteurs les plus forts sur N mois (N = 3, 6, 9, 12, et 12 sans le dernier mois).
Usage : python3 trading/training_sectors.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

import backtest as bt
from data import clean_spikes, load_prices

SECTORS = ["XLK", "XLF", "XLE", "XLV", "XLI", "XLP", "XLY", "XLU", "XLB"]
P = 252


def rotation(p: pd.DataFrame, lookback: int, skip: int = 0, top: int = 3) -> pd.DataFrame:
    mom = p.shift(skip) / p.shift(skip + lookback) - 1
    ends = p.index.to_series().groupby(p.index.to_period("M")).max().values
    w = pd.DataFrame(float("nan"), index=p.index, columns=p.columns)
    for d in ends:
        m = mom.loc[d].dropna()
        if len(m) == len(p.columns):
            row = pd.Series(0.0, index=p.columns)
            row[m.nlargest(top).index] = 1 / top
            w.loc[d] = row
    return w.ffill().fillna(0.0)


def main():
    raw, _ = clean_spikes(load_prices(SECTORS + ["SPY"], start="1999-01-01"))
    p = raw[SECTORS].dropna()
    spy = raw[["SPY"]].loc[p.index]
    eq_spy = bt.run(spy, pd.DataFrame(1.0, index=p.index, columns=["SPY"]))
    eq_eq = bt.run(p, pd.DataFrame(1 / 9, index=p.index, columns=SECTORS))
    md = ["# Rotation sectorielle par momentum (3 meilleurs secteurs sur 9, rééquilibrage mensuel)", "",
          f"Données {p.index[0].date()} → {p.index[-1].date()}, frais 0,20 % par ordre.", "",
          "| Stratégie | 2000-2012 | 2013+ | Perte max (tout) | Sharpe 2013+ |", "|---|---|---|---|---|"]

    def row(name, eq):
        a = bt.metrics(eq[:"2012-12-31"] / eq[:"2012-12-31"].iloc[0], P)
        b = bt.metrics(eq["2013-01-01":] / eq["2013-01-01":].iloc[0], P)
        full = bt.metrics(eq / eq.iloc[0], P)
        md.append(f"| {name} | {a['rendement_annuel']:+.1%} | {b['rendement_annuel']:+.1%} | {full['perte_max']:.0%} | {b['sharpe']:.2f} |")

    row("S&P 500 (SPY)", eq_spy)
    row("9 secteurs à poids égaux", eq_eq)
    for lb, skip, lab in ((63, 0, "3 mois"), (126, 0, "6 mois"), (189, 0, "9 mois"), (252, 0, "12 mois"), (231, 21, "12 mois sauf le dernier")):
        row(f"Top 3, momentum {lab}", bt.run(p, rotation(p, lb, skip)))
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_sectors_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
