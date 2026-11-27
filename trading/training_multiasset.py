"""Suivi de tendance multi-actifs (actions, obligations, or, matières premières, immobilier) avec des ETF.
C'est la stratégie la mieux documentée en finance (Moskowitz, Ooi & Pedersen 2012 ; Faber 2007 ;
Hurst, Ooi & Pedersen « A Century of Evidence on Trend-Following »).

Question : est-ce que ça bat le cœur actuel du robot (100 % ACWI) ou un 60/40 classique ?
Usage : python3 trading/training_multiasset.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

import backtest as bt
import strategies as st
from data import clean_spikes, load_prices

ETFS = ["SPY", "EFA", "EEM", "IEF", "TLT", "GLD", "DBC", "VNQ"]
P = 252  # jours de bourse par an


def tsmom(p: pd.DataFrame, lookback: int = 252) -> pd.DataFrame:
    """Momentum temporel : on détient un actif si son rendement sur 12 mois est positif."""
    on = (p.pct_change(lookback) > 0).astype(float)
    return on.div(p.notna().sum(axis=1).clip(lower=1), axis=0)


def m(eq, s, e):
    part = eq[s:e]
    return bt.metrics(part / part.iloc[0], P)


def main():
    raw = load_prices(ETFS + ["ACWI"], start="2007-01-01")
    raw, fixed = clean_spikes(raw)
    p = raw[ETFS].dropna()
    acwi = raw[["ACWI"]].dropna()
    sixty = pd.DataFrame({"SPY": 0.6, "IEF": 0.4}, index=p.index)
    cands = {
        "100 % ACWI (cœur actuel)": (acwi, st.buy_hold(acwi)),
        "60/40 actions US / obligations": (p[["SPY", "IEF"]], sixty),
        "8 ETF, poids égaux, sans règle": (p, st.buy_hold(p)),
    }
    for w in (100, 150, 200, 250):
        cands[f"8 ETF, tendance SMA{w}"] = (p, st.trend_sma(p, w))
    cands["8 ETF, momentum 12 mois"] = (p, tsmom(p))
    cands["8 ETF, momentum 12 mois + vol. cible 10 %"] = (p, st.vol_target(tsmom(p), p, 0.10, 60, P) * len(ETFS) / 4)

    md = ["# Suivi de tendance multi-actifs (8 ETF)", "",
          f"ETF : {', '.join(ETFS)}. Frais 0,20 %. Données depuis {p.index[0].date()}. Corrections : {fixed or 'aucune'}.",
          "La dernière ligne autorise jusqu'à 2× de poids total (vol. cible), plafonné ci-dessous à 100 % : pas d'emprunt.", "",
          "| Stratégie | Période | Rendement/an | Perte max | Sharpe |", "|---|---|---|---|---|"]
    curves = {}
    for name, (pp, w) in cands.items():
        tot = w.sum(axis=1)
        w = w.div(tot.clip(lower=1.0), axis=0)          # jamais plus de 100 % investi
        eq = bt.run(pp, w)
        curves[name] = eq
        for lab, s, e in (("2008-2015", "2008-01-01", "2015-12-31"), ("2016+", "2016-01-01", None)):
            x = m(eq, s, e)
            md.append(f"| {name} | {lab} | {x['rendement_annuel']:+.1%} | {x['perte_max']:.1%} | {x['sharpe']:.2f} |")
    md += ["", "## Années de crise", "", "| Stratégie | 2008 | 2020 (krach Covid) | 2022 (actions et obligations baissent ensemble) |",
           "|---|---|---|---|"]
    for name, eq in curves.items():
        y = eq.resample("YE").last().pct_change()
        y.index = y.index.year
        md.append(f"| {name} | " + " | ".join(f"{y.get(a, float('nan')):+.0%}" for a in (2008, 2020, 2022)) + " |")
    out = "\n".join(md) + "\n"
    Path(__file__).parent.joinpath("training_multiasset_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
