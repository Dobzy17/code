"""Bourse : les ETF « dividendes » (croissance du dividende ou haut rendement) battent-ils l'indice, dividendes réinvestis ?
Usage : python3 trading/training_dividends.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import backtest as bt
from data import clean_spikes, load_prices

P = 252
ETF = {"VIG": "Croissance du dividende (10 ans de hausse)", "SCHD": "Dividendes de qualité", "NOBL": "Aristocrates (25 ans de hausse)",
       "DVY": "Haut rendement", "HDV": "Haut rendement de qualité"}


def main():
    raw, _ = clean_spikes(load_prices(list(ETF) + ["SPY"], start="2003-01-01"))
    md = ["# ETF dividendes contre S&P 500 (dividendes réinvestis, même période)", "",
          "| ETF | Style | Depuis | Rendement/an | SPY | Écart/an | Perte max | SPY perte max | Années gagnées |", "|---|---|---|---|---|---|---|---|---|"]
    for t, lab in ETF.items():
        s = raw[[t, "SPY"]].dropna().iloc[21:]
        a, b = (bt.metrics(s[x] / s[x].iloc[0], P) for x in (t, "SPY"))
        ya, yb = (s[x].resample("YE").last().pct_change().dropna() for x in (t, "SPY"))
        md.append(f"| {t} | {lab} | {s.index[0].date()} | {a['rendement_annuel']:+.1%} | {b['rendement_annuel']:+.1%} | "
                  f"{a['rendement_annuel'] - b['rendement_annuel']:+.1%} | {a['perte_max']:.0%} | {b['perte_max']:.0%} | "
                  f"{int((ya > yb).sum())} sur {len(ya)} |")
    md += ["", "_En France : dividendes versés imposés à 30 % chaque année sur compte-titres (ces ETF américains ne sont pas "
           "éligibles au PEA) : le retard après impôts est encore plus grand que dans ce tableau._"]
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_dividends_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
