"""Deux tests vus d'un investisseur EN EUROS (données Yahoo, dividendes réinvestis quand l'ETF les verse) :
1. Bourse — biais « maison » : CAC 40 (C40.PA) ou Europe (EXSA.DE, STOXX 600) contre le Monde (CW8.PA, éligible PEA).
2. Autres marchés — l'or en euros (4GLD.DE, Xetra-Gold) dans un cœur CW8.PA : la leçon 34 (en dollars) tient-elle ?
Usage : python3 trading/training_home_gold_eur.py
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
    raw, _ = clean_spikes(load_prices(["CW8.PA", "C40.PA", "EXSA.DE", "4GLD.DE"], start="2008-01-01"))
    p = raw.ffill().loc["2009-11-16":].dropna()
    md = ["# Vu d'un investisseur en euros", "", f"{p.index[0].date()} → {p.index[-1].date()}, frais 0,20 %.", "",
          "## 1. Biais « maison » : France ou Europe contre le Monde", "",
          "| Cœur actions | 2010-2017 | 2018+ | Perte max | ×capital |", "|---|---|---|---|---|"]
    for name, mix in (("100 % Monde (CW8)", {"CW8.PA": 1.0}), ("100 % CAC 40", {"C40.PA": 1.0}),
                      ("100 % Europe (STOXX 600)", {"EXSA.DE": 1.0}), ("70 % Monde + 30 % CAC 40", {"CW8.PA": 0.7, "C40.PA": 0.3})):
        w = pd.DataFrame({t: mix.get(t, 0.0) for t in p.columns}, index=p.index)
        eq = bt.run(p, w)
        a, b = eq["2010":"2017"], eq["2018":]
        ma, mb, mf = (bt.metrics(x / x.iloc[0], P) for x in (a, b, eq))
        md.append(f"| {name} | {ma['rendement_annuel']:+.1%} | {mb['rendement_annuel']:+.1%} | {mf['perte_max']:.0%} | ×{mf['multiplicateur']:.2f} |")
    md += ["", "## 2. Or en euros dans un cœur Monde", "",
           "| Part d'or | 2010-2017 | 2018+ | Perte max | Sharpe 2018+ |", "|---|---|---|---|---|"]
    for g in (0.0, 0.10, 0.20, 0.30):
        w = pd.DataFrame({"CW8.PA": 1 - g, "C40.PA": 0.0, "EXSA.DE": 0.0, "4GLD.DE": g}, index=p.index)
        eq = bt.run(p, w)
        a, b = eq["2010":"2017"], eq["2018":]
        ma, mb, mf = (bt.metrics(x / x.iloc[0], P) for x in (a, b, eq))
        md.append(f"| {g:.0%} | {ma['rendement_annuel']:+.1%} | {mb['rendement_annuel']:+.1%} | {mf['perte_max']:.0%} | {mb['sharpe']:.2f} |")
    g_only = p["4GLD.DE"]
    worst = (g_only / g_only.cummax() - 1)
    md += ["", f"L'or seul en euros : pire baisse {worst.min():.0%} (jusqu'au {worst.idxmin().date()})."]
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_home_gold_eur_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
