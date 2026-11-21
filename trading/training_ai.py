"""Bourse : un satellite « IA » vaut-il le coup ? Nvidia et semi-conducteurs (SMH), avec et sans la règle de tendance,
puis le MÊME test sur les leaders tech de l'an 2000, choisis à l'époque (le seul moyen de ne pas tricher avec le recul).
Note : Lucent et Nortel, deux géants de 2000, ont disparu de Yahoo ; leur absence rend le test 2000 trop FLATTEUR.
Usage : python3 trading/training_ai.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

import backtest as bt
import strategies as st
from data import clean_spikes, load_prices

P = 252
LEADERS_2000 = ["MSFT", "CSCO", "INTC", "ORCL", "IBM", "QCOM"]


def sat(p: pd.DataFrame, core: str, sats: list[str], share: float, trend: bool) -> pd.Series:
    s = p[sats]
    w_s = (st.trend_band(s, 150, 0.03) if trend else st.buy_hold(s)) * share
    w = pd.DataFrame(0.0, index=p.index, columns=p.columns)
    w[sats] = w_s
    w[core] = 1 - share
    return bt.run(p, w)


def m(e):
    return bt.metrics(e / e.iloc[0], P)


def table(p, core, sats, title):
    md = [f"## {title}", "", "| Portefeuille | Rendement/an | Perte max | Sharpe | ×capital |", "|---|---|---|---|---|"]
    rows = {f"100 % {core}": bt.run(p[[core]], pd.DataFrame(1.0, index=p.index, columns=[core]))}
    for share in (0.10, 0.20):
        rows[f"{1 - share:.0%} {core} + {share:.0%} satellite sans règle"] = sat(p, core, sats, share, False)
        rows[f"{1 - share:.0%} {core} + {share:.0%} satellite avec tendance"] = sat(p, core, sats, share, True)
    rows["100 % satellite sans règle"] = bt.run(p[sats], st.buy_hold(p[sats]))
    rows["100 % satellite avec tendance"] = bt.run(p[sats], st.trend_band(p[sats], 150, 0.03))
    for k, e in rows.items():
        x = m(e)
        md.append(f"| {k} | {x['rendement_annuel']:+.1%} | {x['perte_max']:.0%} | {x['sharpe']:.2f} | ×{x['multiplicateur']:.1f} |")
    return md + [""]


def main():
    raw, fixed = clean_spikes(load_prices(["NVDA", "SMH", "SPY"] + LEADERS_2000, start="1999-01-01"))
    md = ["# Satellite IA : Nvidia et semi-conducteurs, puis le test honnête de l'an 2000", "",
          f"Frais 0,20 %. Tendance : moyenne 150 séances, zone ±3 %. Corrections : {fixed or 'aucune'}.", ""]
    md += table(raw[["SPY", "NVDA", "SMH"]].loc["2010-01-01":].dropna(), "SPY", ["NVDA"], "1. Nvidia depuis 2010 (période connue : forte hausse)")
    md += table(raw[["SPY", "SMH"]].loc["2010-01-01":].dropna(), "SPY", ["SMH"], "2. ETF semi-conducteurs (SMH) depuis 2010")
    p00 = raw[["SPY"] + LEADERS_2000].loc["2000-03-24":].dropna()
    md += table(p00, "SPY", LEADERS_2000, "3. Le test honnête : les 6 leaders tech de mars 2000, à poids égaux, jusqu'à aujourd'hui")
    p00b = p00.loc[:"2012-12-31"]
    md += table(p00b, "SPY", LEADERS_2000, "4. Même test, 2000-2012 seulement (ce qu'a vécu un investisseur pendant 12 ans)")
    out = "\n".join(md) + "\n"
    (Path(__file__).parent / "training_ai_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
