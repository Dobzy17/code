"""Hors marché : la règle de Sahm (hausse du chômage) comme signal de sortie des actions.
Série FRED SAHMREALTIME : calculée avec les chiffres DISPONIBLES à l'époque (pas les chiffres révisés). Valeur d'un mois
connue au début du mois suivant (publication de l'emploi) : utilisée avec 35 jours de décalage.
Règle fixée avant le test : cash dès que l'indicateur atteint 0,50 ; retour aux actions quand il repasse sous 0,50
(variante : retour après 6 mois au minimum).
Usage : python3 trading/training_sahm.py
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
    sahm = fred("SAHMREALTIME")
    known = sahm.copy()
    known.index = known.index + pd.Timedelta(days=35)
    r_eq = equity_returns()
    rf = load_prices(["^IRX"], start="1976-01-01")["^IRX"]
    s = known.reindex(r_eq.index, method="ffill")
    trig = s >= 0.5
    starts = [d for d in r_eq.index[trig & ~trig.shift(1, fill_value=False)]]
    level = (1 + r_eq).cumprod()
    md = ["# Règle de Sahm (chômage) : alarme de récession et bourse", "",
          "## 1. Chaque déclenchement (indicateur ≥ 0,50), avec la date où il était CONNU", "",
          "| Connu le | S&P 500 depuis son dernier plus haut (déjà perdu) | S&P 500 +6 mois | +12 mois | Baisse supplémentaire max (12 mois) |",
          "|---|---|---|---|---|"]
    for d in starts:
        before = level.loc[:d]
        already = before.iloc[-1] / before.loc[d - pd.Timedelta(days=730):].max() - 1
        def fwd(days):
            e = level.loc[d:d + pd.Timedelta(days=days)]
            return e.iloc[-1] / e.iloc[0] - 1 if (e.index[-1] - d).days > days - 10 else float("nan")
        win = level.loc[d:d + pd.Timedelta(days=365)]
        md.append(f"| {d.date()} | {already:+.0%} | {fwd(182):+.0%} | {fwd(365):+.0%} | {(win / win.cummax() - 1).min():.0%} |")
    md += ["", "## 2. Stratégies", "", "| Stratégie | 1977-1999 | 2000+ | Perte max | Temps investi |", "|---|---|---|---|---|"]
    out6 = pd.Series(1.0, index=r_eq.index)
    for d in starts:
        out6.loc[d:d + pd.DateOffset(months=6)] = 0.0
    out6[trig] = 0.0
    for name, inv in (("Toujours investi", pd.Series(1.0, index=r_eq.index)),
                      ("Cash tant que Sahm ≥ 0,50", (~trig).astype(float)),
                      ("Cash au moins 6 mois après le signal", out6)):
        e = run(r_eq, inv, rf)
        a, b = e["1977":"1999"], e["2000":]
        ma, mb, mf = bt.metrics(a / a.iloc[0], P), bt.metrics(b / b.iloc[0], P), bt.metrics(e / e.iloc[0], P)
        md.append(f"| {name} | {ma['rendement_annuel']:+.1%} | {mb['rendement_annuel']:+.1%} | {mf['perte_max']:.0%} | {inv.mean():.0%} |")
    md += ["", f"Dernière valeur : {sahm.iloc[-1]:.2f} ({sahm.index[-1].date()})."]
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_sahm_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
