"""Autres marchés : l'or protège-t-il un portefeuille actions dans les krachs ? Et quelle part lui donner,
sans choisir la meilleure après coup ?
Usage : python3 trading/training_gold.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

import backtest as bt
from data import clean_spikes, load_prices

P = 252


def crashes(spy: pd.Series, threshold: float = -0.15) -> list[tuple]:
    """Périodes où SPY recule de plus de 15 % depuis son plus haut : du plus haut au plus bas."""
    out, peak_d, peak, trough_d, trough, in_dd = [], spy.index[0], spy.iloc[0], None, None, False
    for d, v in spy.items():
        if v >= peak:
            if in_dd and trough / peak - 1 <= threshold:
                out.append((peak_d, trough_d))
            peak, peak_d, in_dd, trough, trough_d = v, d, False, v, d
        else:
            in_dd = True
            if v < trough:
                trough, trough_d = v, d
    if in_dd and trough / peak - 1 <= threshold:
        out.append((peak_d, trough_d))
    return out


def main():
    raw, _ = clean_spikes(load_prices(["SPY", "GLD", "IEF"], start="2004-11-18"))
    p = raw.dropna()
    md = ["# L'or dans les krachs", "", f"Données {p.index[0].date()} → {p.index[-1].date()}.", "",
          "## 1. Chaque baisse de plus de 15 % du S&P 500", "",
          "| Du plus haut | Au plus bas | S&P 500 | Or (GLD) | Obligations US 7-10 ans (IEF) |", "|---|---|---|---|---|"]
    for a, b in crashes(p["SPY"]):
        r = p.loc[b] / p.loc[a] - 1
        md.append(f"| {a.date()} | {b.date()} | {r['SPY']:+.0%} | {r['GLD']:+.0%} | {r['IEF']:+.0%} |")
    md += ["", "## 2. Part d'or dans un portefeuille S&P 500 (rééquilibré en continu, frais 0,20 %)", "",
           "| Part d'or | 2005-2015 rendement/an | 2005-2015 perte max | 2016+ rendement/an | 2016+ perte max | 2016+ Sharpe |",
           "|---|---|---|---|---|---|"]
    for g in (0.0, 0.05, 0.10, 0.15, 0.20, 0.30):
        w = pd.DataFrame({"SPY": 1 - g, "GLD": g, "IEF": 0.0}, index=p.index)
        eq = bt.run(p, w)
        a = bt.metrics(eq[:"2015-12-31"] / eq[:"2015-12-31"].iloc[0], P)
        b = bt.metrics(eq["2016-01-01":] / eq["2016-01-01":].iloc[0], P)
        md.append(f"| {g:.0%} | {a['rendement_annuel']:+.1%} | {a['perte_max']:.0%} | {b['rendement_annuel']:+.1%} | "
                  f"{b['perte_max']:.0%} | {b['sharpe']:.2f} |")
    corr = p.pct_change().rolling(252).corr(pairwise=True).xs("SPY", level=1)["GLD"].dropna()
    md += ["", f"Corrélation or / S&P 500 sur 1 an glissant : médiane {corr.median():+.2f}, "
           f"de {corr.min():+.2f} à {corr.max():+.2f} ; aujourd'hui {corr.iloc[-1]:+.2f}."]
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_gold_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
