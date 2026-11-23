"""Radar inversé (retour à la moyenne de long terme, De Bondt & Thaler 1985 ; « value » des pays, Asness et al. 2013) :
chaque fin d'année, acheter les marchés les PLUS FAIBLES des 3 dernières années et les garder 12 mois.
Usage : python3 trading/training_contrarian.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

import backtest as bt
from data import clean_spikes, load_prices
from training_radar import UNIVERSE

P = 252
COUNTRIES = [t for t in UNIVERSE["Actions pays"] if t not in ("QQQ", "IWM")]
ALL = [t for v in UNIVERSE.values() for t in v]


def contrarian(p: pd.DataFrame, n: int, worst: bool = True, years: int = 3) -> pd.DataFrame:
    look = 252 * years
    past = p / p.shift(look) - 1
    age = p.notna().cumsum()
    ends = p.index.to_series().groupby(p.index.year).max().values
    w = pd.DataFrame(float("nan"), index=p.index, columns=p.columns)
    for d in ends:
        elig = past.loc[d][(age.loc[d] > look) & past.loc[d].notna()]
        if len(elig) < n * 2:
            continue
        pick = elig.nsmallest(n).index if worst else elig.nlargest(n).index
        row = pd.Series(0.0, index=p.columns)
        row[pick] = 1 / n
        w.loc[d] = row
    return w.ffill().fillna(0.0)


def main():
    raw, _ = clean_spikes(load_prices(ALL + ["ACWI"], start="2000-01-01"))
    md = ["# Radar inversé : acheter les marchés les plus faibles des 3 dernières années (rééquilibrage annuel)", "",
          "| Univers / stratégie | 2009-2015 | 2016+ | Perte max 2009+ | ×capital 2009+ |", "|---|---|---|---|---|"]

    def row(name, e):
        a, b, f = e["2009-01-01":"2015-12-31"], e["2016-01-01":], e["2009-01-01":]
        ma, mb, mf = (bt.metrics(x / x.iloc[0], P) for x in (a, b, f))
        md.append(f"| {name} | {ma['rendement_annuel']:+.1%} | {mb['rendement_annuel']:+.1%} | {mf['perte_max']:.0%} | ×{mf['multiplicateur']:.2f} |")

    acwi = raw[["ACWI"]].dropna()
    row("ETF monde (référence)", bt.run(acwi, pd.DataFrame(1.0, index=acwi.index, columns=["ACWI"])))
    for label, tick in (("16 pays", COUNTRIES), ("45 marchés", ALL)):
        p = raw[tick].loc["2005-01-01":].dropna(how="all")
        pf = p.fillna(0)
        eqw = pd.DataFrame((p.notna()).astype(float).div(p.notna().sum(axis=1), axis=0), index=p.index)
        row(f"{label} : tous à poids égaux", bt.run(pf, eqw))
        for n in (3, 5):
            row(f"{label} : les {n} PLUS FAIBLES sur 3 ans", bt.run(pf, contrarian(p, n)))
        row(f"{label} : les 5 PLUS FORTS sur 3 ans (contrôle)", bt.run(pf, contrarian(p, 5, worst=False)))
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_contrarian_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
