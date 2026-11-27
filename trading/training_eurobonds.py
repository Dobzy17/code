"""Autres marchés : quelle part d'obligations d'État de la zone euro dans le cœur, côté investisseur EN EUROS ?
Actions : CW8.PA (Amundi MSCI World, éligible PEA, en euros). Obligations : EUNH.DE (iShares Core Euro Government Bond).
Rééquilibrage continu, frais 0,20 %. Attention : un ETF obligataire n'est PAS éligible au PEA (assurance-vie ou compte-titres).
Usage : python3 trading/training_eurobonds.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

import backtest as bt
from data import clean_spikes, load_prices

P = 252


def main():
    raw, _ = clean_spikes(load_prices(["CW8.PA", "EUNH.DE"], start="2009-01-01"))
    p = raw.ffill().dropna()
    md = ["# Obligations d'État en euros dans le cœur (investisseur en euros)", "",
          f"{p.index[0].date()} → {p.index[-1].date()}.", "",
          "| Part obligations | 2010-2016 rendement/an | 2017+ rendement/an | Perte max (tout) | 2022 | 2020 (Covid, pire baisse) | Sharpe 2017+ |",
          "|---|---|---|---|---|---|---|"]
    for b in (0.0, 0.10, 0.20, 0.30, 0.40):
        w = pd.DataFrame({"CW8.PA": 1 - b, "EUNH.DE": b}, index=p.index)
        eq = bt.run(p, w)
        a, c = eq["2010":"2016"], eq["2017":]
        ma, mc, mf = bt.metrics(a / a.iloc[0], P), bt.metrics(c / c.iloc[0], P), bt.metrics(eq / eq.iloc[0], P)
        y22 = eq["2022"].iloc[-1] / eq[:"2021-12-31"].iloc[-1] - 1
        e20 = eq["2020-02-15":"2020-04-30"]
        dd20 = (e20 / e20.cummax() - 1).min()
        md.append(f"| {b:.0%} | {ma['rendement_annuel']:+.1%} | {mc['rendement_annuel']:+.1%} | {mf['perte_max']:.0%} | {y22:+.0%} | "
                  f"{dd20:.0%} | {mc['sharpe']:.2f} |")
    corr = p.pct_change().rolling(252).corr()["CW8.PA"].xs("EUNH.DE", level=1).dropna()
    md += ["", f"Corrélation actions/obligations sur 1 an : avant 2021 médiane {corr[:'2020'].median():+.2f}, depuis 2022 médiane "
           f"{corr['2022':].median():+.2f} (aujourd'hui {corr.iloc[-1]:+.2f})."]
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_eurobonds_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
