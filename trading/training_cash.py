"""Rendement du cash : les stratégies avec tendance étaient-elles sous-estimées ?
Taux : bons du Trésor US à 13 semaines (^IRX, Yahoo, gratuit), en dollars.
Usage : python3 trading/training_cash.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

import backtest as bt
import strategies as st
from data import clean_spikes, load_prices
from research import daily
from training_multiasset import ETFS, tsmom


def line(name, eq_a, eq_b, start):
    a = bt.metrics(eq_a[start:] / eq_a[start:].iloc[0], 365)
    b = bt.metrics(eq_b[start:] / eq_b[start:].iloc[0], 365)
    return (f"| {name} | {a['rendement_annuel']:+.1%} (Sharpe {a['sharpe']:.2f}) | "
            f"{b['rendement_annuel']:+.1%} (Sharpe {b['sharpe']:.2f}) | {b['rendement_annuel'] - a['rendement_annuel']:+.1%} |")


def main():
    irx = load_prices(["^IRX"], start="2007-01-01")["^IRX"] / 100
    md = ["# Effet du rendement du cash (bons du Trésor US 3 mois)", "",
          f"Taux moyen : 2008-2015 {irx['2008':'2015'].mean():.2%}, 2016-2021 {irx['2016':'2021'].mean():.2%}, "
          f"2022+ {irx['2022':].mean():.2%}.", "",
          "| Stratégie (2021+ pour la crypto, 2016+ pour les ETF) | Cash à 0 % | Cash rémunéré | Écart |", "|---|---|---|---|"]

    raw = load_prices(["ACWI", "BTC-USD", "ETH-USD"], start="2014-01-01")
    p, _ = clean_spikes(daily(raw).loc["2017-11-09":].dropna())
    c = ["BTC-USD", "ETH-USD"]
    rd = irx.reindex(p.index).ffill()
    w_bot = st.trend_sma(p[c], 150) * 0.30
    w_bot["ACWI"] = 0.70
    w_bh = pd.DataFrame({"ACWI": 0.70, "BTC-USD": 0.15, "ETH-USD": 0.15}, index=p.index)
    for name, w in (("Robot 70/30 + tendance", w_bot[p.columns]), ("70/30 sans règle", w_bh)):
        md.append(line(name, bt.run(p, w), bt.run(p, w, cash_rate=rd), "2021-01-01"))
    for name, w in (("Crypto seule SMA150", st.trend_sma(p[c], 150)), ("Crypto seule sans règle", st.buy_hold(p[c]))):
        md.append(line(name, bt.run(p[c], w), bt.run(p[c], w, cash_rate=rd), "2021-01-01"))

    e = load_prices(ETFS, start="2007-01-01").dropna()
    re_ = irx.reindex(e.index).ffill()
    sixty = pd.DataFrame({"SPY": 0.6, "IEF": 0.4}, index=e.index)
    for name, pp, w in (("8 ETF momentum 12 mois", e, tsmom(e)), ("8 ETF tendance SMA150", e, st.trend_sma(e, 150)),
                        ("60/40", e[["SPY", "IEF"]], sixty)):
        a = bt.run(pp, w)
        b = bt.run(pp, w, cash_rate=re_, periods_per_year=252)
        ma, mb = (bt.metrics(x["2016-01-01":] / x["2016-01-01":].iloc[0], 252) for x in (a, b))
        md.append(f"| {name} | {ma['rendement_annuel']:+.1%} (Sharpe {ma['sharpe']:.2f}) | "
                  f"{mb['rendement_annuel']:+.1%} (Sharpe {mb['sharpe']:.2f}) | {mb['rendement_annuel'] - ma['rendement_annuel']:+.1%} |")
    out = "\n".join(md) + "\n"
    Path(__file__).parent.joinpath("training_cash_results.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
