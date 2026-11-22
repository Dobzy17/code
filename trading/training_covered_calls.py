"""Autres marchés / options : les ETF qui vendent des options d'achat (« calls couverts ») versent un gros revenu.
Est-ce qu'il compense la hausse à laquelle ils renoncent ? Comparaison dividendes réinvestis, sur la même période.
Usage : python3 trading/training_covered_calls.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import backtest as bt
from data import clean_spikes, load_prices

P = 252
PAIRS = [("QYLD", "QQQ", "Nasdaq 100, calls vendus chaque mois"), ("XYLD", "SPY", "S&P 500, calls vendus chaque mois"),
         ("JEPI", "SPY", "S&P 500 faible volatilité + calls"), ("JEPQ", "QQQ", "Nasdaq 100 + calls")]


def main():
    tick = sorted({t for a, b, _ in PAIRS for t in (a, b)})
    raw, _ = clean_spikes(load_prices(tick, start="2013-01-01"))
    md = ["# ETF à options d'achat vendues (calls couverts) contre l'indice", "",
          "| ETF | Stratégie | Depuis | Rendement/an | Indice | Écart/an | Perte max | Perte max indice | ×capital vs indice |",
          "|---|---|---|---|---|---|---|---|---|"]
    for a, b, lab in PAIRS:
        s = raw[[a, b]].dropna()
        s = s.iloc[21:]
        ma, mb = (bt.metrics(s[x] / s[x].iloc[0], P) for x in (a, b))
        md.append(f"| {a} | {lab} | {s.index[0].date()} | {ma['rendement_annuel']:+.1%} | {mb['rendement_annuel']:+.1%} ({b}) | "
                  f"{ma['rendement_annuel'] - mb['rendement_annuel']:+.1%} | {ma['perte_max']:.0%} | {mb['perte_max']:.0%} | "
                  f"×{ma['multiplicateur']:.2f} contre ×{mb['multiplicateur']:.2f} |")
    md += ["", "_Fiscalité française : ces ETF américains versent leur revenu en dividendes, imposés chaque année à 30 % sur un "
           "compte-titres (et non éligibles au PEA). Un ETF capitalisant sur l'indice, dans un PEA, n'est imposé qu'au retrait._"]
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_covered_calls_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
