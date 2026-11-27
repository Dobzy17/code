"""Hors marché : le stress du crédit (écart de taux des entreprises) annonce-t-il les krachs, et en profite-t-on ?
Règle fixée AVANT le test (classique dans la littérature) : sortir des actions quand l'écart de crédit est au-dessus
de sa moyenne 200 jours (le stress monte), revenir quand il repasse dessous. Donnée connue avec 1 jour de retard.
Écart : BAA10Y (obligations Baa − État 10 ans, FRED, depuis 1986) ; contrôle avec BAMLH0A0HYM2 (haut rendement) si disponible.
Usage : python3 trading/training_credit.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

import backtest as bt
from data import load_prices
from training_curve import equity_returns, fred, run

P = 252


def main():
    r_eq = equity_returns()
    rf = load_prices(["^IRX"], start="1976-01-01")["^IRX"]
    md = ["# Stress du crédit : sortir des actions quand il monte ?", "",
          "| Écart utilisé | Stratégie | 1987-1999 | 2000+ | Perte max | Temps investi | Changements par an |", "|---|---|---|---|---|---|---|"]
    for sid in ("BAA10Y", "BAMLH0A0HYM2"):
        try:
            sp = fred(sid).shift(1, freq="D")
        except Exception as e:
            md.append(f"| {sid} | indisponible ({type(e).__name__}) | | | | | |")
            continue
        sp = sp.reindex(r_eq.index).ffill().dropna()
        r = r_eq.loc[sp.index[0] + pd.Timedelta(days=300):]
        sp = sp.reindex(r.index)
        for win in (100, 200, 300):
            inv = (sp <= sp.rolling(win).mean()).astype(float)
            for name, i in (("Toujours investi", pd.Series(1.0, index=r.index)), (f"Cash si écart > moyenne {win} j", inv)):
                if name == "Toujours investi" and win != 200:
                    continue
                e = run(r, i, rf)
                a, b = e[:"1999-12-31"], e["2000-01-01":]
                fa = bt.metrics(a / a.iloc[0], P)["rendement_annuel"] if len(a) > 300 else float("nan")
                mb, mf = bt.metrics(b / b.iloc[0], P), bt.metrics(e / e.iloc[0], P)
                ch = i.diff().abs().sum() / ((r.index[-1] - r.index[0]).days / 365.25)
                md.append(f"| {sid} (depuis {r.index[0].year}) | {name} | {fa:+.1%} | {mb['rendement_annuel']:+.1%} | "
                          f"{mf['perte_max']:.0%} | {i.mean():.0%} | {ch:.1f} |")
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_credit_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
