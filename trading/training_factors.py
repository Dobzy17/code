"""Bourse : les « facteurs » reconnus par la recherche (momentum, qualité, faible volatilité, value, petites
capitalisations) ont-ils tenu leurs promesses, une fois emballés dans des ETF accessibles à un particulier ?
Usage : python3 trading/training_factors.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

import backtest as bt
from data import clean_spikes, load_prices

ETF = {"MTUM": "Momentum", "QUAL": "Qualité", "USMV": "Faible volatilité", "VLUE": "Value", "IWM": "Petites capitalisations"}
P = 252


def main():
    raw, _ = clean_spikes(load_prices(list(ETF) + ["SPY"], start="2010-01-01"))
    md = ["# Facteurs en ETF contre le S&P 500 (SPY), dividendes réinvestis", "",
          "Chaque facteur est comparé à SPY **sur sa propre période**, depuis le lancement de son ETF.", "",
          "| Facteur | Depuis | Rendement/an | SPY même période | Écart/an | Perte max | SPY perte max | Années gagnées contre SPY |",
          "|---|---|---|---|---|---|---|---|"]
    for t, name in ETF.items():
        s = raw[t].dropna()
        start = s.index[0] + pd.Timedelta(days=30)        # on laisse passer le premier mois (liquidité)
        a = raw.loc[start:, t].dropna()
        b = raw.loc[a.index, "SPY"]
        ma, mb = bt.metrics(a / a.iloc[0], P), bt.metrics(b / b.iloc[0], P)
        ya = a.resample("YE").last().pct_change().dropna()
        yb = b.resample("YE").last().pct_change().dropna()
        wins = int((ya > yb).sum())
        md.append(f"| {name} ({t}) | {a.index[0].date()} | {ma['rendement_annuel']:+.1%} | {mb['rendement_annuel']:+.1%} | "
                  f"{ma['rendement_annuel'] - mb['rendement_annuel']:+.1%} | {ma['perte_max']:.0%} | {mb['perte_max']:.0%} | "
                  f"{wins} sur {len(ya)} |")
    common = raw[list(ETF) + ["SPY"]].dropna()
    common = common.loc[common.index[0] + pd.Timedelta(days=30):]
    corr = common.pct_change().corr()["SPY"].drop("SPY")
    md += ["", f"Corrélation quotidienne avec SPY ({common.index[0].date()} → aujourd'hui) : "
           + ", ".join(f"{ETF[t]} {c:.2f}" for t, c in corr.items()), ""]
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_factors_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
